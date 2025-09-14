"""
分组管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
import json
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User
from app.models.group import Group, GroupStatus
from app.models.blacklist import Blacklist
from app.schemas.group import (
    GroupResponse, GroupCreate, GroupUpdate, GroupListResponse, 
    GroupSearchParams, GroupDetailRequest, GroupBatchCheckRequest, GroupBatchCheckResponse
)
from app.api.v1.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/list", response_model=GroupListResponse)
async def get_groups(
    search_params: GroupSearchParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分组列表"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限查看分组记录")
    
    query = db.query(Group).filter(Group.is_active == True)
    
    # 状态筛选
    if search_params.status:
        query = query.filter(Group.status == search_params.status)
    
    # 搜索功能
    if search_params.search:
        query = query.filter(
            (Group.name.contains(search_params.search)) |
            (Group.description.contains(search_params.search)) |
            (Group.file_name.contains(search_params.search))
        )
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    groups = query.offset(search_params.skip).limit(search_params.limit).all()
    
    # 转换为Pydantic模型
    group_responses = []
    for group in groups:
        group_dict = group.to_dict()
        group_responses.append(GroupResponse.model_validate(group_dict))
    
    return GroupListResponse(
        data=group_responses,
        total=total,
        page=(search_params.skip // search_params.limit) + 1,
        size=search_params.limit,
        pages=(total + search_params.limit - 1) // search_params.limit
    )


@router.post("/detail", response_model=GroupResponse)
async def get_group(
    request: GroupDetailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分组详情"""
    group = db.query(Group).filter(
        Group.id == request.group_id, 
        Group.is_active == True
    ).first()
    
    if not group:
        raise NotFoundError("分组", str(request.group_id))
    
    group_dict = group.to_dict()
    return GroupResponse.model_validate(group_dict)


@router.post("/create", response_model=GroupResponse)
async def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建分组"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限创建分组")
    
    # 创建分组
    group = Group(
        name=group_data.name,
        description=group_data.description,
        file_name=group_data.file_name,
        file_path=group_data.file_path,
        status=group_data.status,
        created_by=current_user.id
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    group_dict = group.to_dict()
    return GroupResponse.model_validate(group_dict)


@router.post("/update", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新分组"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限更新分组")
    
    group = db.query(Group).filter(Group.id == group_id, Group.is_active == True).first()
    if not group:
        raise NotFoundError("分组", str(group_id))
    
    # 更新字段
    update_data = group_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    
    group.updated_at = datetime.now()
    db.commit()
    db.refresh(group)
    
    group_dict = group.to_dict()
    return GroupResponse.model_validate(group_dict)


@router.post("/delete")
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除分组（软删除）"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限删除分组")
    
    group = db.query(Group).filter(Group.id == group_id, Group.is_active == True).first()
    if not group:
        raise NotFoundError("分组", str(group_id))
    
    # 软删除
    group.is_active = False
    group.status = GroupStatus.DELETED
    group.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "分组删除成功"}


@router.post("/batch-check", response_model=GroupBatchCheckResponse)
async def batch_check_blacklist(
    request: GroupBatchCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量检测分组中的订单黑名单"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限执行批量检测")
    
    # 获取分组
    group = db.query(Group).filter(
        Group.id == request.group_id, 
        Group.is_active == True
    ).first()
    
    if not group:
        raise NotFoundError("分组", str(request.group_id))
    
    # 获取分组下的所有订单
    from app.models.order import Order
    orders = db.query(Order).filter(
        Order.group_id == request.group_id,
        Order.is_active == True
    ).all()
    
    if not orders:
        return GroupBatchCheckResponse(
            group_id=group.id,
            group_name=group.name,
            total_orders=0,
            checked_orders=0,
            blacklist_matches=0,
            new_matches=0,
            check_time=datetime.now(),
            status="no_orders",
            message="该分组下没有订单"
        )
    
    # 获取所有黑名单数据
    blacklist_items = db.query(Blacklist).filter(Blacklist.is_active == True).all()
    logger.info(f"加载了 {len(blacklist_items)} 条黑名单记录")
    
    # 执行批量检测
    checked_count = 0
    new_matches = 0
    
    for order in orders:
        # 如果强制重新检测或者订单未检测过
        if request.force_recheck or order.is_blacklist_checked != "yes":
            try:
                # 执行实际的黑名单匹配
                from app.services.blacklist_matcher import blacklist_matcher
                match_result = blacklist_matcher.check_order_blacklist(order, blacklist_items)
                
                # 更新订单状态
                order.is_blacklist_checked = "yes"
                order.blacklist_risk_level = match_result["risk_level"]
                
                if match_result["is_blacklist"]:
                    order.blacklist_match_info = f"匹配到 {match_result.get('match_count', 0)} 条黑名单记录"
                    new_matches += 1
                    
                    # 记录匹配详情
                    if match_result["matches"]:
                        match_details = []
                        for match in match_result["matches"][:3]:  # 只显示前3个匹配
                            match_details.append(f"{match['match_type']}: {match['match_details']}")
                        order.blacklist_match_details = "; ".join(match_details)
                else:
                    order.blacklist_match_info = "未匹配到黑名单"
                    order.blacklist_match_details = ""
                
                checked_count += 1
                logger.info(f"订单 {order.id} 检测完成: 风险等级={match_result['risk_level']}, 匹配={match_result['is_blacklist']}")
                
            except Exception as e:
                logger.error(f"检测订单 {order.id} 时出错: {e}")
                continue
    
    # 更新分组统计
    group.checked_orders = checked_count
    group.blacklist_matches = new_matches
    group.updated_at = datetime.now()
    db.commit()
    
    return GroupBatchCheckResponse(
        group_id=group.id,
        group_name=group.name,
        total_orders=len(orders),
        checked_orders=checked_count,
        blacklist_matches=group.blacklist_matches,
        new_matches=new_matches,
        check_time=datetime.now(),
        status="completed",
        message=f"批量检测完成，检测了 {checked_count} 个订单，发现 {new_matches} 个黑名单匹配"
    )


@router.post("/upload-excel")
async def upload_excel_to_group(
    group_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传Excel文件到指定分组"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限上传文件")
    
    # 获取分组
    group = db.query(Group).filter(
        Group.id == group_id, 
        Group.is_active == True
    ).first()
    
    if not group:
        raise NotFoundError("分组", str(group_id))
    
    # 这里可以添加Excel文件处理逻辑
    # 暂时返回成功消息
    return {
        "message": f"文件 {file.filename} 上传到分组 {group.name} 成功",
        "group_id": group_id,
        "file_name": file.filename
    }

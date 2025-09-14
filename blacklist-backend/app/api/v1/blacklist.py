"""
黑名单管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User
from app.models.blacklist import Blacklist, BlacklistHistory
from app.schemas.blacklist import BlacklistResponse, BlacklistCreate, BlacklistUpdate, BlacklistHistoryResponse, BlacklistSearchParams
from app.api.v1.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/list", response_model=dict)
async def get_blacklist(
    search_params: BlacklistSearchParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取黑名单列表"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限查看黑名单记录")
    
    query = db.query(Blacklist).filter(Blacklist.is_active == True)
    
    # 风险等级筛选
    if search_params.risk_level:
        query = query.filter(Blacklist.risk_level == search_params.risk_level)
    
    # 搜索功能
    if search_params.search:
        query = query.filter(
            (Blacklist.ktt_name.contains(search_params.search)) |
            (Blacklist.wechat_name.contains(search_params.search)) |
            (Blacklist.order_name_phone.contains(search_params.search)) |
            (Blacklist.blacklist_reason.contains(search_params.search))
        )
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    blacklist_items = query.offset(search_params.skip).limit(search_params.limit).all()
    
    # 转换为Pydantic模型，处理JSON字段
    blacklist_responses = []
    for item in blacklist_items:
        # 处理phone_numbers字段，如果是字符串则解析为列表
        item_dict = item.to_dict()
        if isinstance(item_dict.get('phone_numbers'), str):
            import json
            try:
                item_dict['phone_numbers'] = json.loads(item_dict['phone_numbers'])
            except (json.JSONDecodeError, TypeError):
                item_dict['phone_numbers'] = []
        
        blacklist_responses.append(BlacklistResponse.model_validate(item_dict))
    
    return {
        "data": blacklist_responses,
        "total": total,
        "page": (search_params.skip // search_params.limit) + 1,
        "size": search_params.limit,
        "pages": (total + search_params.limit - 1) // search_params.limit
    }


class BlacklistDetailRequest(BaseModel):
    """黑名单详情请求"""
    blacklist_id: int

@router.post("/detail", response_model=BlacklistResponse)
async def get_blacklist_item(
    request: BlacklistDetailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取黑名单详情"""
    blacklist_item = db.query(Blacklist).filter(
        Blacklist.id == request.blacklist_id, 
        Blacklist.is_active == True
    ).first()
    
    if not blacklist_item:
        raise NotFoundError("黑名单记录", str(request.blacklist_id))
    
    return blacklist_item


@router.post("/", response_model=BlacklistResponse)
async def create_blacklist_item(
    blacklist_data: BlacklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建黑名单记录"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限创建黑名单记录")
    
    # 生成10位唯一ID
    import random
    import string
    
    def generate_unique_id():
        while True:
            new_id = ''.join(random.choices(string.digits, k=10))
            # 检查ID是否已存在
            existing = db.query(Blacklist).filter(Blacklist.new_id == new_id).first()
            if not existing:
                return new_id
    
    # 获取下一个序号
    last_sequence = db.query(Blacklist).order_by(Blacklist.sequence_number.desc()).first()
    next_sequence = (last_sequence.sequence_number + 1) if last_sequence and last_sequence.sequence_number else 1
    
    # 创建黑名单记录
    blacklist_item = Blacklist(
        sequence_number=next_sequence,
        new_id=generate_unique_id(),
        ktt_name=blacklist_data.ktt_name,
        wechat_name=blacklist_data.wechat_name,
        wechat_id=blacklist_data.wechat_id,
        order_name_phone=blacklist_data.order_name_phone,
        phone_numbers=blacklist_data.phone_numbers,
        order_address1=blacklist_data.order_address1,
        order_address2=blacklist_data.order_address2,
        blacklist_reason=blacklist_data.blacklist_reason,
        risk_level=blacklist_data.risk_level,
        created_by=current_user.id
    )
    
    db.add(blacklist_item)
    db.commit()
    db.refresh(blacklist_item)
    
    # 记录变更历史
    import json
    from datetime import datetime
    
    def serialize_for_history(obj):
        """序列化对象用于历史记录"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    history_data = {}
    for key, value in blacklist_item.to_dict().items():
        history_data[key] = serialize_for_history(value)
    
    history = BlacklistHistory(
        blacklist_id=blacklist_item.id,
        action="create",
        new_data=history_data,
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()
    
    logger.info(f"黑名单记录 {blacklist_item.id} 创建成功")
    return blacklist_item


@router.put("/{blacklist_id}", response_model=BlacklistResponse)
async def update_blacklist_item(
    blacklist_id: int,
    blacklist_data: BlacklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新黑名单记录"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限更新黑名单记录")
    
    blacklist_item = db.query(Blacklist).filter(
        Blacklist.id == blacklist_id, 
        Blacklist.is_active == True
    ).first()
    
    if not blacklist_item:
        raise NotFoundError("黑名单记录", str(blacklist_id))
    
    # 保存原始数据
    old_data = blacklist_item.to_dict()
    
    # 更新数据
    update_data = blacklist_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        # 特殊处理JSON字段
        if field == 'phone_numbers' and value is not None:
            if isinstance(value, list):
                setattr(blacklist_item, field, value)
            else:
                setattr(blacklist_item, field, [])
        else:
            setattr(blacklist_item, field, value)
    
    db.commit()
    db.refresh(blacklist_item)
    
    # 记录变更历史
    import json
    from datetime import datetime
    
    def serialize_for_history(obj):
        """序列化对象用于历史记录"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    # 序列化数据用于历史记录
    old_data_serialized = {}
    for key, value in old_data.items():
        old_data_serialized[key] = serialize_for_history(value)
    
    new_data_serialized = {}
    for key, value in blacklist_item.to_dict().items():
        new_data_serialized[key] = serialize_for_history(value)
    
    history = BlacklistHistory(
        blacklist_id=blacklist_item.id,
        action="update",
        old_data=old_data_serialized,
        new_data=new_data_serialized,
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()
    
    logger.info(f"黑名单记录 {blacklist_item.id} 更新成功")
    return blacklist_item


@router.delete("/{blacklist_id}")
async def delete_blacklist_item(
    blacklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除黑名单记录（软删除）"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限删除黑名单记录")
    
    blacklist_item = db.query(Blacklist).filter(
        Blacklist.id == blacklist_id, 
        Blacklist.is_active == True
    ).first()
    
    if not blacklist_item:
        raise NotFoundError("黑名单记录", str(blacklist_id))
    
    # 保存原始数据
    old_data = blacklist_item.to_dict()
    
    # 软删除
    blacklist_item.is_active = False
    db.commit()
    
    # 记录变更历史
    history = BlacklistHistory(
        blacklist_id=blacklist_item.id,
        action="delete",
        old_data=old_data,
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()
    
    logger.info(f"黑名单记录 {blacklist_item.id} 删除成功")
    return {"message": "黑名单记录删除成功"}


@router.get("/{blacklist_id}/history", response_model=List[BlacklistHistoryResponse])
async def get_blacklist_history(
    blacklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取黑名单变更历史"""
    blacklist_item = db.query(Blacklist).filter(
        Blacklist.id == blacklist_id, 
        Blacklist.is_active == True
    ).first()
    
    if not blacklist_item:
        raise NotFoundError("黑名单记录", str(blacklist_id))
    
    history = db.query(BlacklistHistory).filter(
        BlacklistHistory.blacklist_id == blacklist_id
    ).order_by(BlacklistHistory.created_at.desc()).all()
    
    return history


@router.post("/batch-delete")
async def batch_delete_blacklist(
    ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量删除黑名单记录"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限批量删除黑名单记录")
    
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择要删除的记录"
        )
    
    # 批量软删除
    deleted_count = db.query(Blacklist).filter(
        Blacklist.id.in_(ids),
        Blacklist.is_active == True
    ).update({Blacklist.is_active: False}, synchronize_session=False)
    
    db.commit()
    
    logger.info(f"批量删除黑名单记录成功: {deleted_count} 条")
    return {"message": f"成功删除 {deleted_count} 条记录"}


@router.post("/import")
async def import_blacklist(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导入黑名单Excel文件"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限导入黑名单文件")
    
    # 这里应该实现实际的Excel导入逻辑
    # 在实际应用中，可以使用pandas等库处理Excel文件
    
    logger.info(f"黑名单导入请求: {file.filename}")
    return {"message": "导入功能开发中", "filename": file.filename}


@router.get("/export")
async def export_blacklist(
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    ids: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出黑名单数据"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限导出黑名单数据")
    
    # 构建查询
    query = db.query(Blacklist).filter(Blacklist.is_active == True)
    
    if risk_level:
        query = query.filter(Blacklist.risk_level == risk_level)
    
    if search:
        query = query.filter(
            (Blacklist.ktt_name.contains(search)) |
            (Blacklist.order_name.contains(search)) |
            (Blacklist.phone.contains(search)) |
            (Blacklist.blacklist_reason.contains(search))
        )
    
    if ids:
        id_list = [int(id) for id in ids.split(',')]
        query = query.filter(Blacklist.id.in_(id_list))
    
    records = query.all()
    
    # 这里应该实现实际的Excel导出逻辑
    # 在实际应用中，可以使用pandas等库生成Excel文件
    
    logger.info(f"黑名单导出请求: {len(records)} 条记录")
    return {"message": "导出功能开发中", "count": len(records)}

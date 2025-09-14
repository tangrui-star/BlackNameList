#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分组黑名单检测API - 专门用于20250914组的检测逻辑
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.blacklist import Blacklist
from app.models.order import Order
from app.models.group import Group
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.core.exceptions import NotFoundError, ForbiddenError
from app.services.blacklist_matcher import blacklist_matcher
from app.schemas.group import GroupBatchCheckResponse, GroupBatchCheckRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/detect-group-20250914", response_model=GroupBatchCheckResponse)
async def detect_group_20250914(
    request: GroupBatchCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    专门检测20250914组的黑名单匹配逻辑
    
    检测流程：
    1. 获取20250914组的所有订单
    2. 获取所有活跃的黑名单数据
    3. 遍历每个订单，进行多维度匹配：
       - 电话号码匹配（优先级最高）
       - 下单人姓名匹配
       - KTT名字匹配
    4. 记录匹配结果和风险等级
    5. 更新订单检测状态
    """
    
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限执行批量检测")
    
    # 查找20250914分组
    group = db.query(Group).filter(
        Group.name == "20250914",
        Group.is_active == True
    ).first()
    
    if not group:
        raise NotFoundError("分组", "20250914")
    
    logger.info(f"开始检测分组 {group.name} (ID: {group.id}) 的黑名单匹配")
    
    # 获取该分组的所有订单
    orders = db.query(Order).filter(
        Order.group_id == group.id,
        Order.is_active == True
    ).all()
    
    if not orders:
        logger.warning(f"分组 {group.name} 下没有订单")
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
    
    logger.info(f"找到 {len(orders)} 个订单，开始检测...")
    
    # 获取所有活跃的黑名单数据
    blacklist_items = db.query(Blacklist).filter(Blacklist.is_active == True).all()
    logger.info(f"加载了 {len(blacklist_items)} 条黑名单记录")
    
    # 检测统计
    checked_count = 0
    new_matches = 0
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    no_risk_count = 0
    
    # 详细检测结果
    detection_results = []
    
    # 遍历每个订单进行检测
    for i, order in enumerate(orders):
        try:
            logger.info(f"检测订单 {i+1}/{len(orders)}: ID={order.id}, 下单人={order.orderer}, 电话={order.contact_phone}")
            
            # 如果强制重新检测或者订单未检测过
            if request.force_recheck or order.is_blacklist_checked != "yes":
                
                # 执行黑名单匹配
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
                    
                    # 统计风险等级
                    if match_result["risk_level"] == "HIGH":
                        high_risk_count += 1
                    elif match_result["risk_level"] == "MEDIUM":
                        medium_risk_count += 1
                    elif match_result["risk_level"] == "LOW":
                        low_risk_count += 1
                else:
                    order.blacklist_match_info = "未匹配到黑名单"
                    order.blacklist_match_details = ""
                    no_risk_count += 1
                
                checked_count += 1
                
                # 记录详细检测结果
                detection_results.append({
                    "order_id": order.id,
                    "group_tour_number": order.group_tour_number,
                    "orderer": order.orderer,
                    "contact_phone": order.contact_phone,
                    "detailed_address": order.detailed_address,
                    "is_blacklist": match_result["is_blacklist"],
                    "risk_level": match_result["risk_level"],
                    "match_count": match_result.get("match_count", 0),
                    "matches": match_result.get("matches", []),
                    "match_info": order.blacklist_match_info,
                    "match_details": order.blacklist_match_details
                })
                
                logger.info(f"订单 {order.id} 检测完成: 风险等级={match_result['risk_level']}, 匹配={match_result['is_blacklist']}")
            
        except Exception as e:
            logger.error(f"检测订单 {order.id} 时出错: {e}")
            continue
    
    # 更新分组统计信息
    group.total_orders = len(orders)
    group.checked_orders = checked_count
    group.blacklist_matches = new_matches
    group.updated_at = datetime.now()
    
    # 提交数据库更改
    db.commit()
    
    logger.info(f"检测完成: 总订单={len(orders)}, 已检测={checked_count}, 黑名单匹配={new_matches}")
    logger.info(f"风险等级分布: 高风险={high_risk_count}, 中风险={medium_risk_count}, 低风险={low_risk_count}, 无风险={no_risk_count}")
    
    return GroupBatchCheckResponse(
        group_id=group.id,
        group_name=group.name,
        total_orders=len(orders),
        checked_orders=checked_count,
        blacklist_matches=new_matches,
        new_matches=new_matches,
        check_time=datetime.now(),
        status="completed",
        message=f"检测完成: 总订单={len(orders)}, 已检测={checked_count}, 黑名单匹配={new_matches}, 高风险={high_risk_count}, 中风险={medium_risk_count}, 低风险={low_risk_count}"
    )


@router.post("/get-detection-results")
async def get_detection_results(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取检测结果详情
    """
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限查看检测结果")
    
    # 构建查询
    query = db.query(Order).filter(
        Order.group_id == group_id,
        Order.is_active == True,
        Order.is_blacklist_checked == "yes"
    )
    
    if risk_level:
        query = query.filter(Order.blacklist_risk_level == risk_level.upper())
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    orders = query.offset(skip).limit(limit).all()
    
    results = []
    for order in orders:
        results.append({
            "order_id": order.id,
            "group_tour_number": order.group_tour_number,
            "orderer": order.orderer,
            "contact_phone": order.contact_phone,
            "detailed_address": order.detailed_address,
            "order_amount": float(order.order_amount) if order.order_amount else 0,
            "order_status": order.order_status.value if order.order_status else "UNKNOWN",
            "risk_level": order.blacklist_risk_level,
            "match_info": order.blacklist_match_info,
            "match_details": order.blacklist_match_details,
            "payment_time": order.payment_time.isoformat() if order.payment_time else None,
            "created_at": order.created_at.isoformat() if order.created_at else None
        })
    
    return {
        "total": total,
        "results": results,
        "page": (skip // limit) + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/get-detection-statistics")
async def get_detection_statistics(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取检测统计信息
    """
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限查看检测统计")
    
    # 获取分组信息
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise NotFoundError("分组", str(group_id))
    
    # 统计各风险等级的订单数量
    from sqlalchemy import func
    
    risk_stats = db.query(
        Order.blacklist_risk_level,
        func.count(Order.id).label('count')
    ).filter(
        Order.group_id == group_id,
        Order.is_active == True,
        Order.is_blacklist_checked == "yes"
    ).group_by(Order.blacklist_risk_level).all()
    
    risk_distribution = {stat.blacklist_risk_level: stat.count for stat in risk_stats}
    
    return {
        "group_id": group_id,
        "group_name": group.name,
        "total_orders": group.total_orders,
        "checked_orders": group.checked_orders,
        "blacklist_matches": group.blacklist_matches,
        "match_rate": round(group.blacklist_matches / group.total_orders * 100, 2) if group.total_orders > 0 else 0,
        "risk_distribution": risk_distribution,
        "last_check_time": group.updated_at.isoformat() if group.updated_at else None
    }

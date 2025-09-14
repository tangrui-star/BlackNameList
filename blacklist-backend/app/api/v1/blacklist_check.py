#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黑名单检测API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.models.blacklist import Blacklist
from app.models.order import Order
from app.services.blacklist_matcher import blacklist_matcher
from app.schemas.blacklist import BlacklistResponse

router = APIRouter()


@router.get("/check-order/{order_id}")
async def check_single_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """检查单个订单是否在黑名单中"""
    # 获取订单
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 获取所有黑名单数据
    blacklist_items = db.query(Blacklist).filter(Blacklist.is_active == True).all()
    
    # 执行匹配
    result = blacklist_matcher.check_order_blacklist(order, blacklist_items)
    
    # 更新订单的黑名单检测状态
    order.is_blacklist_checked = "yes" if result["is_blacklist"] else "no"
    order.blacklist_risk_level = result["risk_level"]
    order.blacklist_match_info = f"匹配到 {result.get('match_count', 0)} 条黑名单记录" if result["is_blacklist"] else "未匹配到黑名单"
    
    if result["is_blacklist"] and result["matches"]:
        match_details = []
        for match in result["matches"][:3]:  # 只显示前3个匹配
            match_details.append(f"{match['match_type']}: {match['match_details']}")
        order.blacklist_match_details = "; ".join(match_details)
    
    db.commit()
    
    return {
        "order_id": order.id,
        "order_info": {
            "group_tour_number": order.group_tour_number,
            "orderer": order.orderer,
            "contact_phone": order.contact_phone,
            "detailed_address": order.detailed_address
        },
        "blacklist_check": result
    }


@router.get("/check-orders")
async def check_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    risk_level: Optional[str] = Query(None, description="风险等级过滤"),
    db: Session = Depends(get_db)
):
    """批量检查订单黑名单状态"""
    # 获取订单
    query = db.query(Order)
    if risk_level:
        query = query.filter(Order.blacklist_risk_level == risk_level.upper())
    
    orders = query.offset(skip).limit(limit).all()
    
    # 获取所有黑名单数据
    blacklist_items = db.query(Blacklist).filter(Blacklist.is_active == True).all()
    
    results = []
    for order in orders:
        result = blacklist_matcher.check_order_blacklist(order, blacklist_items)
        
        # 更新订单状态
        order.is_blacklist_checked = "yes" if result["is_blacklist"] else "no"
        order.blacklist_risk_level = result["risk_level"]
        order.blacklist_match_info = f"匹配到 {result.get('match_count', 0)} 条黑名单记录" if result["is_blacklist"] else "未匹配到黑名单"
        
        if result["is_blacklist"] and result["matches"]:
            match_details = []
            for match in result["matches"][:3]:
                match_details.append(f"{match['match_type']}: {match['match_details']}")
            order.blacklist_match_details = "; ".join(match_details)
        
        results.append({
            "order_id": order.id,
            "group_tour_number": order.group_tour_number,
            "orderer": order.orderer,
            "contact_phone": order.contact_phone,
            "blacklist_check": result
        })
    
    db.commit()
    
    return {
        "total_checked": len(results),
        "blacklist_matches": len([r for r in results if r["blacklist_check"]["is_blacklist"]]),
        "results": results
    }


@router.get("/blacklist-matches")
async def get_blacklist_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    risk_level: Optional[str] = Query(None, description="风险等级过滤"),
    db: Session = Depends(get_db)
):
    """获取黑名单匹配的订单列表"""
    query = db.query(Order).filter(Order.is_blacklist_checked == "yes")
    
    if risk_level:
        query = query.filter(Order.blacklist_risk_level == risk_level.upper())
    
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
            "payment_time": order.payment_time.isoformat() if order.payment_time else None
        })
    
    return {
        "total_matches": len(results),
        "results": results
    }


@router.get("/statistics")
async def get_blacklist_statistics(db: Session = Depends(get_db)):
    """获取黑名单检测统计信息"""
    from sqlalchemy import func
    
    # 总订单数
    total_orders = db.query(func.count(Order.id)).scalar()
    
    # 已检测订单数
    checked_orders = db.query(func.count(Order.id)).filter(Order.is_blacklist_checked == "yes").scalar()
    
    # 黑名单匹配订单数
    blacklist_matches = db.query(func.count(Order.id)).filter(
        Order.is_blacklist_checked == "yes",
        Order.blacklist_risk_level.in_(["HIGH", "MEDIUM", "LOW"])
    ).scalar()
    
    # 按风险等级统计
    risk_stats = db.query(
        Order.blacklist_risk_level,
        func.count(Order.id).label('count')
    ).filter(
        Order.is_blacklist_checked == "yes"
    ).group_by(Order.blacklist_risk_level).all()
    
    risk_level_stats = {stat.blacklist_risk_level: stat.count for stat in risk_stats}
    
    return {
        "total_orders": total_orders,
        "checked_orders": checked_orders,
        "blacklist_matches": blacklist_matches,
        "match_rate": round(blacklist_matches / total_orders * 100, 2) if total_orders > 0 else 0,
        "risk_level_distribution": risk_level_stats
    }

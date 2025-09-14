#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分组黑名单检测API - 简化版本
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.blacklist import Blacklist
from app.models.order import Order
from app.models.group import Group
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/test-connection")
async def test_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """测试连接"""
    try:
        # 测试数据库连接
        group_count = db.query(Group).count()
        order_count = db.query(Order).count()
        blacklist_count = db.query(Blacklist).count()
        
        return {
            "status": "success",
            "message": "连接正常",
            "data": {
                "group_count": group_count,
                "order_count": order_count,
                "blacklist_count": blacklist_count,
                "user_id": current_user.id,
                "user_name": current_user.username
            }
        }
    except Exception as e:
        logger.error(f"连接测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")


@router.post("/detect-group-20250914-simple")
async def detect_group_20250914_simple(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """简化版20250914组检测"""
    try:
        # 查找20250914分组
        group = db.query(Group).filter(
            Group.name == "20250914",
            Group.is_active == True
        ).first()
        
        if not group:
            raise HTTPException(status_code=404, detail="未找到20250914分组")
        
        # 获取该分组的所有订单
        orders = db.query(Order).filter(
            Order.group_id == group.id,
            Order.is_active == True
        ).all()
        
        # 获取黑名单数据
        blacklist_items = db.query(Blacklist).filter(Blacklist.is_active == True).all()
        
        # 简单统计
        total_orders = len(orders)
        checked_orders = len([o for o in orders if o.is_blacklist_checked == "yes"])
        blacklist_matches = len([o for o in orders if o.blacklist_risk_level and o.blacklist_risk_level != "none"])
        
        return {
            "status": "success",
            "message": "检测完成",
            "data": {
                "group_id": group.id,
                "group_name": group.name,
                "total_orders": total_orders,
                "checked_orders": checked_orders,
                "blacklist_matches": blacklist_matches,
                "blacklist_items_count": len(blacklist_items),
                "check_time": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"检测失败: {e}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

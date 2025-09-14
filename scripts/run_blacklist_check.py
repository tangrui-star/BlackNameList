#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行黑名单检测脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
blacklist_backend_path = project_root / "blacklist-backend"
sys.path.append(str(blacklist_backend_path))

from app.core.database import get_db
from app.models.blacklist import Blacklist
from app.models.order import Order
from app.services.blacklist_matcher import blacklist_matcher
from sqlalchemy import func

def run_blacklist_check():
    """运行黑名单检测"""
    print("开始黑名单检测...")
    
    db = next(get_db())
    
    # 获取所有黑名单数据
    blacklist_items = db.query(Blacklist).filter(Blacklist.is_active == True).all()
    print(f"黑名单数据: {len(blacklist_items)} 条")
    
    # 获取所有订单
    orders = db.query(Order).all()
    print(f"订单数据: {len(orders)} 条")
    
    # 统计信息
    total_orders = len(orders)
    blacklist_matches = 0
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    
    # 检测每个订单
    for i, order in enumerate(orders):
        if (i + 1) % 50 == 0:
            print(f"已检测 {i + 1}/{total_orders} 个订单...")
        
        result = blacklist_matcher.check_order_blacklist(order, blacklist_items)
        
        if result["is_blacklist"]:
            blacklist_matches += 1
            
            # 更新订单状态
            order.is_blacklist_checked = "yes"
            order.blacklist_risk_level = result["risk_level"]
            order.blacklist_match_info = f"匹配到 {result.get('match_count', 0)} 条黑名单记录"
            
            if result["matches"]:
                match_details = []
                for match in result["matches"][:3]:  # 只显示前3个匹配
                    match_details.append(f"{match['match_type']}: {match['match_details']}")
                order.blacklist_match_details = "; ".join(match_details)
            
            # 统计风险等级
            if result["risk_level"] == "HIGH":
                high_risk += 1
            elif result["risk_level"] == "MEDIUM":
                medium_risk += 1
            else:
                low_risk += 1
        else:
            order.is_blacklist_checked = "no"
            order.blacklist_risk_level = "LOW"
            order.blacklist_match_info = "未匹配到黑名单"
            order.blacklist_match_details = None
    
    # 提交更改
    db.commit()
    
    # 输出结果
    print("\n" + "="*50)
    print("黑名单检测完成！")
    print("="*50)
    print(f"总订单数: {total_orders}")
    print(f"黑名单匹配: {blacklist_matches}")
    print(f"匹配率: {blacklist_matches/total_orders*100:.2f}%")
    print(f"高风险: {high_risk}")
    print(f"中风险: {medium_risk}")
    print(f"低风险: {low_risk}")
    print("="*50)
    
    # 显示一些匹配示例
    matched_orders = db.query(Order).filter(Order.is_blacklist_checked == "yes").limit(5).all()
    if matched_orders:
        print("\n匹配示例:")
        for order in matched_orders:
            print(f"订单 {order.id}: {order.orderer} - {order.contact_phone} - {order.blacklist_risk_level} - {order.blacklist_match_info}")

if __name__ == "__main__":
    run_blacklist_check()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复订单状态脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
blacklist_backend_path = project_root / "blacklist-backend"
sys.path.append(str(blacklist_backend_path))

from app.core.database import engine
from sqlalchemy import text

def fix_order_status():
    """修复订单状态"""
    print("开始修复订单状态...")
    
    with engine.connect() as conn:
        try:
            # 更新订单状态为正确的枚举值
            conn.execute(text("UPDATE orders SET order_status = 'PAID' WHERE order_status = 'paid'"))
            conn.execute(text("UPDATE orders SET order_status = 'PENDING' WHERE order_status = 'pending'"))
            conn.execute(text("UPDATE orders SET order_status = 'CANCELLED' WHERE order_status = 'cancelled'"))
            conn.execute(text("UPDATE orders SET order_status = 'SHIPPED' WHERE order_status = 'shipped'"))
            conn.execute(text("UPDATE orders SET order_status = 'DELIVERED' WHERE order_status = 'delivered'"))
            conn.execute(text("UPDATE orders SET order_status = 'REFUNDED' WHERE order_status = 'refunded'"))
            conn.commit()
            print("订单状态更新完成")
            return True
        except Exception as e:
            print(f"更新失败: {e}")
            return False

if __name__ == "__main__":
    success = fix_order_status()
    if success:
        print("✅ 订单状态修复成功！")
    else:
        print("❌ 订单状态修复失败！")
        sys.exit(1)

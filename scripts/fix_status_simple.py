#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单修复订单状态脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
blacklist_backend_path = project_root / "blacklist-backend"
sys.path.append(str(blacklist_backend_path))

from app.core.database import engine
from sqlalchemy import text

def fix_status():
    with engine.connect() as conn:
        # 查看当前状态
        result = conn.execute(text('SELECT DISTINCT order_status FROM orders LIMIT 5'))
        print('当前状态值:')
        for row in result:
            print(f'  {row[0]}')
        
        # 更新状态
        conn.execute(text("UPDATE orders SET order_status = 'PAID' WHERE order_status = 'paid'"))
        conn.execute(text("UPDATE orders SET order_status = 'CANCELLED' WHERE order_status = 'cancelled'"))
        conn.commit()
        print('状态更新完成')
        
        # 再次查看状态分布
        result = conn.execute(text('SELECT order_status, COUNT(*) as count FROM orders GROUP BY order_status'))
        print('更新后状态分布:')
        for row in result:
            print(f'  {row[0]}: {row[1]} 条')

if __name__ == "__main__":
    fix_status()

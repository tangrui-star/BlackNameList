#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复枚举定义脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
blacklist_backend_path = project_root / "blacklist-backend"
sys.path.append(str(blacklist_backend_path))

from app.core.database import engine
from sqlalchemy import text

def fix_enum():
    with engine.connect() as conn:
        try:
            # 修改枚举定义
            conn.execute(text('ALTER TABLE orders MODIFY COLUMN order_status ENUM("PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED", "REFUNDED")'))
            conn.commit()
            print('枚举定义更新完成')
            
            # 更新数据
            conn.execute(text('UPDATE orders SET order_status = "PAID" WHERE order_status = "paid"'))
            conn.execute(text('UPDATE orders SET order_status = "CANCELLED" WHERE order_status = "cancelled"'))
            conn.commit()
            print('数据更新完成')
            
            # 查看结果
            result = conn.execute(text('SELECT order_status, COUNT(*) as count FROM orders GROUP BY order_status'))
            print('最终状态分布:')
            for row in result:
                print(f'  {row[0]}: {row[1]} 条')
                
        except Exception as e:
            print(f'更新失败: {e}')

if __name__ == "__main__":
    fix_enum()

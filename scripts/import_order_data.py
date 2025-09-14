#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入订单数据脚本
将数据源20250915.xlsx文件中的数据导入到订单表中
"""

import pandas as pd
import sys
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
blacklist_backend_path = project_root / "blacklist-backend"
sys.path.append(str(blacklist_backend_path))

from app.core.database import get_db, init_db
from app.models.order import Order, OrderStatus
from app.core.config import settings

def import_order_data():
    """导入订单数据"""
    print("开始导入订单数据...")
    
    # 初始化数据库
    init_db()
    
    # 读取Excel文件
    excel_file = project_root / "数据源20250915.xlsx"
    if not excel_file.exists():
        print(f"错误：文件 {excel_file} 不存在")
        return False
    
    try:
        df = pd.read_excel(excel_file)
        print(f"成功读取Excel文件，共 {len(df)} 行数据")
        
        # 获取数据库会话
        db = next(get_db())
        
        imported_count = 0
        failed_count = 0
        errors = []
        
        # 处理每一行数据
        for index, row in df.iterrows():
            try:
                # 数据清洗和转换
                order_data = {
                    'group_tour_number': str(row['跟团号']) if pd.notna(row['跟团号']) else None,
                    'orderer': str(row['下单人']) if pd.notna(row['下单人']) else None,
                    'member_remarks': str(row['团员备注']) if pd.notna(row['团员备注']) else None,
                    'payment_time': row['支付时间'] if pd.notna(row['支付时间']) else None,
                    'group_leader_remarks': str(row['团长备注']) if pd.notna(row['团长备注']) else None,
                    'product': str(row['商品']) if pd.notna(row['商品']) else None,
                    'order_amount': Decimal(str(row['订单金额'])) if pd.notna(row['订单金额']) else None,
                    'refund_amount': Decimal(str(row['退款金额'])) if pd.notna(row['退款金额']) else Decimal('0'),
                    'order_status': str(row['订单状态']).lower() if pd.notna(row['订单状态']) else 'pending',
                    'pickup_point': str(row['自提点']) if pd.notna(row['自提点']) else None,
                    'consignee': str(row['收货人']) if pd.notna(row['收货人']) else None,
                    'contact_phone': str(row['联系电话']) if pd.notna(row['联系电话']) else None,
                    'detailed_address': str(row['详细地址']) if pd.notna(row['详细地址']) else None,
                }
                
                # 处理订单状态
                status_mapping = {
                    '已支付': 'paid',
                    '待支付': 'pending',
                    '已发货': 'shipped',
                    '已送达': 'delivered',
                    '已取消': 'cancelled',
                    '已退款': 'refunded'
                }
                if order_data['order_status'] in status_mapping:
                    order_data['order_status'] = status_mapping[order_data['order_status']]
                else:
                    order_data['order_status'] = 'pending'
                
                # 创建订单
                order = Order(**order_data)
                db.add(order)
                imported_count += 1
                
                if (index + 1) % 50 == 0:
                    print(f"已处理 {index + 1} 条记录...")
                
            except Exception as e:
                failed_count += 1
                error_msg = f"第{index + 2}行数据错误: {str(e)}"
                errors.append(error_msg)
                print(f"错误: {error_msg}")
        
        # 提交事务
        db.commit()
        print(f"\n导入完成！")
        print(f"成功导入: {imported_count} 条")
        print(f"失败: {failed_count} 条")
        
        if errors:
            print(f"\n错误详情:")
            for error in errors[:10]:  # 只显示前10个错误
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... 还有 {len(errors) - 10} 个错误")
        
        return True
        
    except Exception as e:
        print(f"导入过程中发生错误: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = import_order_data()
    if success:
        print("\n✅ 订单数据导入成功！")
    else:
        print("\n❌ 订单数据导入失败！")
        sys.exit(1)

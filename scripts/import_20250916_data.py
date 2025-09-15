#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入20250916.xlsx订单数据到数据库
这是一个新的数据源组，包含订单信息
"""

import pandas as pd
import sys
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
blacklist_backend_path = project_root / "blacklist-backend"
sys.path.append(str(blacklist_backend_path))

from app.core.database import get_db, init_db
from app.models.order import Order, OrderStatus
from app.models.group import Group
from app.core.config import settings

def create_group_for_import():
    """为这次导入创建一个分组"""
    db = next(get_db())
    try:
        # 检查是否已存在同名分组
        existing_group = db.query(Group).filter(Group.name == "20250916数据源组").first()
        if existing_group:
            print(f"使用现有分组: {existing_group.name} (ID: {existing_group.id})")
            return existing_group.id
        
        # 创建新分组
        group = Group(
            name="20250916数据源组",
            description="从20250916.xlsx文件导入的订单数据",
            file_name="20250916.xlsx",
            file_path=str(project_root / "20250916.xlsx"),
            total_orders=0,  # 稍后更新
            checked_orders=0,
            blacklist_matches=0,
            status="active",
            created_by=1,  # 假设用户ID为1
            is_active=True
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        print(f"创建新分组: {group.name} (ID: {group.id})")
        return group.id
        
    except Exception as e:
        print(f"创建分组时出错: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def analyze_excel_structure(file_path):
    """分析Excel文件结构"""
    print("="*60)
    print("分析Excel文件结构")
    print("="*60)
    
    try:
        df = pd.read_excel(file_path)
        print(f"文件包含 {len(df)} 行数据")
        print(f"列名: {list(df.columns)}")
        
        # 显示前几行数据
        print("\n前5行数据:")
        print(df.head())
        
        # 检查数据类型
        print("\n数据类型:")
        print(df.dtypes)
        
        # 检查空值
        print("\n空值统计:")
        print(df.isnull().sum())
        
        return df
        
    except Exception as e:
        print(f"分析文件时出错: {e}")
        return None

def import_order_data(file_path, group_id):
    """导入订单数据"""
    print("开始导入订单数据...")
    
    # 初始化数据库
    init_db()
    
    if not Path(file_path).exists():
        print(f"错误：文件 {file_path} 不存在")
        return False
    
    try:
        df = pd.read_excel(file_path)
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
                    'group_id': group_id,
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
                    'is_blacklist_checked': 'no',  # 默认未检测
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
                
                print(f"导入记录 {index + 1}: 下单人='{order_data['orderer']}', 电话='{order_data['contact_phone']}'")
                
            except Exception as e:
                failed_count += 1
                error_msg = f"第{index + 2}行数据错误: {str(e)}"
                errors.append(error_msg)
                print(f"错误: {error_msg}")
        
        # 更新分组统计信息
        try:
            group = db.query(Group).filter(Group.id == group_id).first()
            if group:
                group.total_orders = imported_count
                group.checked_orders = 0
                group.blacklist_matches = 0
                db.commit()
                print(f"更新分组统计信息: 总订单数={imported_count}")
        except Exception as e:
            print(f"更新分组统计信息时出错: {e}")
        
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

def main():
    """主函数"""
    print("="*80)
    print("20250916.xlsx 订单数据导入工具")
    print("="*80)
    
    # Excel文件路径
    excel_file = project_root / "20250916.xlsx"
    
    if not excel_file.exists():
        print(f"❌ 错误: 找不到文件 {excel_file}")
        return
    
    # 1. 分析文件结构
    df = analyze_excel_structure(excel_file)
    if df is None:
        print("❌ 文件分析失败")
        return
    
    # 2. 创建分组
    print("\n" + "="*60)
    print("创建数据分组")
    print("="*60)
    group_id = create_group_for_import()
    if group_id is None:
        print("❌ 创建分组失败")
        return
    
    # 3. 导入数据
    print("\n" + "="*60)
    print("导入订单数据")
    print("="*60)
    success = import_order_data(excel_file, group_id)
    
    if success:
        print("\n✅ 数据导入成功！")
        print(f"📊 分组ID: {group_id}")
        print(f"📁 文件: {excel_file}")
    else:
        print("\n❌ 数据导入失败！")

if __name__ == "__main__":
    main()

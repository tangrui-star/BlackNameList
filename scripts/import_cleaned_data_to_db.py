#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将清洗后的黑名单数据导入到数据库
"""

import pymysql
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

def connect_database():
    """连接数据库"""
    return pymysql.connect(
        host='47.109.97.153',
        port=3306,
        user='root',
        password='Root@2025!',
        database='blacklist',
        charset='utf8mb4'
    )

def import_cleaned_data_to_db(cleaned_file: str, user_id: int = 1) -> Dict[str, Any]:
    """将清洗后的数据导入到数据库"""
    connection = None
    stats = {
        'total_records': 0,
        'imported': 0,
        'skipped': 0,
        'errors': 0,
        'with_ktt_name': 0,
        'with_phone': 0,
        'with_wechat_name': 0,
        'with_wechat_id': 0,
        'with_address1': 0,
        'with_address2': 0,
        'with_reason': 0,
        'risk_levels': {}
    }
    
    try:
        print(f"正在读取清洗后的数据文件: {cleaned_file}")
        
        # 读取清洗后的Excel文件
        df = pd.read_excel(cleaned_file)
        stats['total_records'] = len(df)
        
        print(f"清洗后的数据包含 {len(df)} 条记录")
        
        # 连接数据库
        print("正在连接数据库...")
        connection = connect_database()
        cursor = connection.cursor()
        
        # 处理每一行数据
        for index, row in df.iterrows():
            try:
                # 提取清洗后的数据
                ktt_name = row.get('ktt名字_清洗') if pd.notna(row.get('ktt名字_清洗')) else None
                wechat_name = row.get('微信名字_清洗') if pd.notna(row.get('微信名字_清洗')) else None
                wechat_id = row.get('微信号_清洗') if pd.notna(row.get('微信号_清洗')) else None
                order_name_phone = row.get('下单名字和电话_原始') if pd.notna(row.get('下单名字和电话_原始')) else None
                phone_numbers = row.get('提取的电话号码') if pd.notna(row.get('提取的电话号码')) else []
                order_address1 = row.get('下单地址1_清洗') if pd.notna(row.get('下单地址1_清洗')) else None
                order_address2 = row.get('下单地址2_清洗') if pd.notna(row.get('下单地址2_清洗')) else None
                blacklist_reason = row.get('入黑名单原因_清洗') if pd.notna(row.get('入黑名单原因_清洗')) else None
                risk_level = row.get('风险等级') if pd.notna(row.get('风险等级')) else 'medium'
                
                # 统计信息
                if ktt_name:
                    stats['with_ktt_name'] += 1
                if phone_numbers:
                    stats['with_phone'] += 1
                if wechat_name:
                    stats['with_wechat_name'] += 1
                if wechat_id:
                    stats['with_wechat_id'] += 1
                if order_address1:
                    stats['with_address1'] += 1
                if order_address2:
                    stats['with_address2'] += 1
                if blacklist_reason:
                    stats['with_reason'] += 1
                
                # 统计风险等级
                if risk_level in stats['risk_levels']:
                    stats['risk_levels'][risk_level] += 1
                else:
                    stats['risk_levels'][risk_level] = 1
                
                # 检查是否已存在（基于电话号码）
                if phone_numbers:
                    # 检查是否有任何电话号码已存在
                    phone_exists = False
                    for phone in phone_numbers:
                        cursor.execute("SELECT id FROM blacklist WHERE JSON_CONTAINS(phone_numbers, %s)", (json.dumps(phone),))
                        if cursor.fetchone():
                            phone_exists = True
                            break
                    
                    if phone_exists:
                        print(f"跳过重复记录 (电话: {phone_numbers})")
                        stats['skipped'] += 1
                        continue
                
                # 插入数据
                insert_sql = """
                    INSERT INTO blacklist (
                        ktt_name, wechat_name, wechat_id, order_name_phone,
                        phone_numbers, order_address1, order_address2,
                        blacklist_reason, risk_level, created_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                # 将电话号码列表转换为JSON
                phone_numbers_json = json.dumps(phone_numbers, ensure_ascii=False) if phone_numbers else None
                
                # 暂时将created_by设置为NULL，避免外键约束问题
                cursor.execute(insert_sql, (
                    ktt_name, wechat_name, wechat_id, order_name_phone,
                    phone_numbers_json, order_address1, order_address2,
                    blacklist_reason, risk_level, None
                ))
                
                stats['imported'] += 1
                print(f"导入记录 {index + 1}: KTT='{ktt_name}', 电话={phone_numbers}")
                
            except Exception as e:
                print(f"处理第 {index + 1} 行时出错: {e}")
                stats['errors'] += 1
                continue
        
        # 提交事务
        connection.commit()
        
        return stats
        
    except Exception as e:
        print(f"导入过程中出错: {e}")
        if connection:
            connection.rollback()
        stats['errors'] = stats['total_records']
        return stats
    finally:
        if connection:
            connection.close()

def main():
    """主函数"""
    print("="*80)
    print("黑名单数据导入到数据库")
    print("="*80)
    
    # 清洗后的数据文件
    cleaned_file = "data/blacklist/cleaned_blacklist_data.xlsx"
    
    if not Path(cleaned_file).exists():
        print(f"❌ 错误: 找不到清洗后的数据文件 {cleaned_file}")
        print("请先运行 clean_and_organize_data.py 脚本清洗数据")
        return
    
    # 执行导入
    stats = import_cleaned_data_to_db(cleaned_file)
    
    # 显示结果
    print("\n" + "="*80)
    print("导入完成！")
    print("="*80)
    print(f"总记录数: {stats['total_records']}")
    print(f"成功导入: {stats['imported']}")
    print(f"跳过重复: {stats['skipped']}")
    print(f"错误记录: {stats['errors']}")
    print(f"有KTT名字的记录: {stats['with_ktt_name']}")
    print(f"有电话号码的记录: {stats['with_phone']}")
    print(f"有微信名字的记录: {stats['with_wechat_name']}")
    print(f"有微信号的记录: {stats['with_wechat_id']}")
    print(f"有地址1的记录: {stats['with_address1']}")
    print(f"有地址2的记录: {stats['with_address2']}")
    print(f"有黑名单原因的记录: {stats['with_reason']}")
    print(f"风险等级分布: {stats['risk_levels']}")
    
    if stats['imported'] > 0:
        print("\n✅ 数据导入成功！")
    else:
        print("\n❌ 没有数据被导入")

if __name__ == "__main__":
    main()

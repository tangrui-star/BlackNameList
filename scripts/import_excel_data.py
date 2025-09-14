#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入Excel黑名单数据到数据库
支持分离姓名和电话号码
"""

import pymysql
import pandas as pd
import re
import json
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

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

def extract_name_and_phone(text: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    """从文本中提取姓名和电话号码"""
    if not text or pd.isna(text) or str(text).strip() == '':
        return None, None, []
    
    text = str(text).strip()
    
    # 提取所有电话号码（11位手机号）
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    
    # 提取姓名（去除电话号码后的文本）
    name_text = re.sub(r'[0-9\s\-\+\(\)]+', '', text).strip()
    name = name_text if name_text else None
    
    # 主要电话号码（第一个）
    main_phone = phones[0] if phones else None
    
    return name, main_phone, phones

def clean_text(text: Any) -> Optional[str]:
    """清理文本数据"""
    if pd.isna(text) or text is None:
        return None
    
    text = str(text).strip()
    return text if text else None

def import_excel_data(file_path: str, user_id: int = 1) -> Dict[str, Any]:
    """导入Excel数据到数据库"""
    connection = None
    stats = {
        'total_rows': 0,
        'imported': 0,
        'skipped': 0,
        'errors': 0,
        'with_name': 0,
        'with_phone': 0,
        'with_both': 0
    }
    
    try:
        print(f"正在读取Excel文件: {file_path}")
        
        # 读取Excel文件，跳过第一行说明文字
        df = pd.read_excel(file_path, skiprows=1)
        stats['total_rows'] = len(df)
        
        print(f"Excel文件包含 {len(df)} 行数据")
        print(f"列名: {list(df.columns)}")
        
        # 手动设置列名
        expected_columns = ['ktt名字', '微信名字', '微信号', '下单名字和电话', '下单地址1', '下单地址2', '入黑名单原因']
        if len(df.columns) >= len(expected_columns):
            df.columns = expected_columns + list(df.columns[len(expected_columns):])
            print(f"设置列名为: {expected_columns}")
        
        # 连接数据库
        print("正在连接数据库...")
        connection = connect_database()
        cursor = connection.cursor()
        
        # 处理每一行数据
        for index, row in df.iterrows():
            try:
                # 提取数据
                ktt_name = clean_text(row.get('ktt名字'))
                wechat_name = clean_text(row.get('微信名字'))
                wechat_id = clean_text(row.get('微信号'))
                order_name_phone = clean_text(row.get('下单名字和电话'))
                order_address1 = clean_text(row.get('下单地址1'))
                order_address2 = clean_text(row.get('下单地址2'))
                blacklist_reason = clean_text(row.get('入黑名单原因'))
                
                # 分离姓名和电话号码
                order_name, phone, phone_numbers = extract_name_and_phone(order_name_phone)
                
                # 统计信息
                if order_name:
                    stats['with_name'] += 1
                if phone:
                    stats['with_phone'] += 1
                if order_name and phone:
                    stats['with_both'] += 1
                
                # 检查是否已存在（基于电话号码）
                if phone:
                    cursor.execute("SELECT id FROM blacklist WHERE phone = %s", (phone,))
                    if cursor.fetchone():
                        print(f"跳过重复记录 (电话: {phone})")
                        stats['skipped'] += 1
                        continue
                
                # 插入数据
                insert_sql = """
                    INSERT INTO blacklist (
                        ktt_name, wechat_name, wechat_id, order_name, phone,
                        order_name_phone, phone_numbers, order_address1, order_address2,
                        blacklist_reason, risk_level, created_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                # 确定风险等级
                risk_level = 'medium'  # 默认中风险
                if blacklist_reason and ('惯犯' in blacklist_reason or '重点' in blacklist_reason):
                    risk_level = 'high'
                elif blacklist_reason and ('轻微' in blacklist_reason or '提醒' in blacklist_reason):
                    risk_level = 'low'
                
                cursor.execute(insert_sql, (
                    ktt_name, wechat_name, wechat_id, order_name, phone,
                    order_name_phone, json.dumps(phone_numbers, ensure_ascii=False),
                    order_address1, order_address2, blacklist_reason,
                    risk_level, user_id
                ))
                
                stats['imported'] += 1
                print(f"导入记录 {index + 1}: 姓名='{order_name}', 电话='{phone}'")
                
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
        stats['errors'] = stats['total_rows']
        return stats
    finally:
        if connection:
            connection.close()

def main():
    """主函数"""
    print("="*60)
    print("黑名单数据导入工具")
    print("="*60)
    
    # Excel文件路径
    excel_file = "data/blacklist/副本-5_ktt手作骗子持更2025版.xlsx"
    
    if not Path(excel_file).exists():
        print(f"错误: 找不到文件 {excel_file}")
        return
    
    # 执行导入
    stats = import_excel_data(excel_file)
    
    # 显示结果
    print("\n" + "="*60)
    print("导入完成！")
    print("="*60)
    print(f"总行数: {stats['total_rows']}")
    print(f"成功导入: {stats['imported']}")
    print(f"跳过重复: {stats['skipped']}")
    print(f"错误记录: {stats['errors']}")
    print(f"有姓名的记录: {stats['with_name']}")
    print(f"有电话的记录: {stats['with_phone']}")
    print(f"姓名和电话都有的记录: {stats['with_both']}")
    
    if stats['imported'] > 0:
        print("\n✓ 数据导入成功！")
    else:
        print("\n✗ 没有数据被导入")

if __name__ == "__main__":
    main()

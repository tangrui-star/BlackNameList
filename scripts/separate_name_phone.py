#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分离姓名和电话号码的迁移脚本
"""

import pymysql
import re
import json
from typing import List, Tuple, Optional

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

def extract_name_and_phone(text: str) -> Tuple[Optional[str], Optional[str]]:
    """从文本中提取姓名和电话号码"""
    if not text or text.strip() == '':
        return None, None
    
    # 提取电话号码（11位手机号）
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else None
    
    # 提取姓名（去除电话号码后的文本）
    name_text = re.sub(r'[0-9\s\-\+\(\)]+', '', text).strip()
    name = name_text if name_text else None
    
    return name, phone

def migrate_data():
    """执行数据迁移"""
    connection = None
    try:
        print("正在连接数据库...")
        connection = connect_database()
        cursor = connection.cursor()
        
        # 1. 添加新字段
        print("添加新字段...")
        try:
            cursor.execute("""
                ALTER TABLE blacklist 
                ADD COLUMN order_name VARCHAR(200) COMMENT '下单人姓名' AFTER wechat_id
            """)
            print("添加 order_name 字段成功")
        except pymysql.Error as e:
            if "Duplicate column name" in str(e):
                print("order_name 字段已存在")
            else:
                raise e
        
        try:
            cursor.execute("""
                ALTER TABLE blacklist 
                ADD COLUMN phone VARCHAR(20) COMMENT '主要电话号码' AFTER order_name
            """)
            print("添加 phone 字段成功")
        except pymysql.Error as e:
            if "Duplicate column name" in str(e):
                print("phone 字段已存在")
            else:
                raise e
        
        # 2. 获取需要处理的数据
        print("获取数据...")
        cursor.execute("""
            SELECT id, order_name_phone, phone_numbers 
            FROM blacklist 
            WHERE order_name_phone IS NOT NULL AND order_name_phone != ''
        """)
        
        records = cursor.fetchall()
        print(f"找到 {len(records)} 条记录需要处理")
        
        # 3. 处理每条记录
        updated_count = 0
        for record_id, order_name_phone, existing_phones in records:
            name, phone = extract_name_and_phone(order_name_phone)
            
            if name or phone:
                # 更新姓名和电话号码
                update_sql = "UPDATE blacklist SET order_name = %s, phone = %s WHERE id = %s"
                cursor.execute(update_sql, (name, phone, record_id))
                
                # 更新 phone_numbers JSON 字段
                if phone:
                    try:
                        # 解析现有的 phone_numbers
                        if existing_phones:
                            phone_list = json.loads(existing_phones)
                        else:
                            phone_list = []
                        
                        # 添加新提取的电话号码（如果不存在）
                        if phone not in phone_list:
                            phone_list.append(phone)
                        
                        # 更新 phone_numbers
                        cursor.execute(
                            "UPDATE blacklist SET phone_numbers = %s WHERE id = %s",
                            (json.dumps(phone_list, ensure_ascii=False), record_id)
                        )
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，创建新的列表
                        cursor.execute(
                            "UPDATE blacklist SET phone_numbers = %s WHERE id = %s",
                            (json.dumps([phone], ensure_ascii=False), record_id)
                        )
                
                updated_count += 1
                print(f"处理记录 {record_id}: 姓名='{name}', 电话='{phone}'")
        
        # 4. 添加索引
        print("添加索引...")
        try:
            cursor.execute("ALTER TABLE blacklist ADD INDEX idx_order_name (order_name)")
        except pymysql.Error:
            print("索引 idx_order_name 可能已存在")
        
        try:
            cursor.execute("ALTER TABLE blacklist ADD INDEX idx_phone (phone)")
        except pymysql.Error:
            print("索引 idx_phone 可能已存在")
        
        # 5. 提交更改
        connection.commit()
        
        # 6. 显示统计结果
        print("\n" + "="*50)
        print("数据迁移完成！")
        print("="*50)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(order_name) as records_with_name,
                COUNT(phone) as records_with_phone,
                COUNT(CASE WHEN order_name IS NOT NULL AND phone IS NOT NULL THEN 1 END) as records_with_both
            FROM blacklist
        """)
        
        stats = cursor.fetchone()
        print(f"总记录数: {stats[0]}")
        print(f"有姓名的记录: {stats[1]}")
        print(f"有电话的记录: {stats[2]}")
        print(f"姓名和电话都有的记录: {stats[3]}")
        print(f"成功更新的记录: {updated_count}")
        
        return True
        
    except Exception as e:
        print(f"迁移失败: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()

def main():
    """主函数"""
    print("="*60)
    print("黑名单数据迁移 - 分离姓名和电话号码")
    print("="*60)
    
    success = migrate_data()
    
    if success:
        print("\n✓ 数据迁移成功完成！")
    else:
        print("\n✗ 数据迁移失败！")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

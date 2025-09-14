#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新ID系统：添加序号字段，生成10位唯一ID
"""

import pymysql
import random
import string
from typing import Set

def generate_unique_id(existing_ids: Set[str]) -> str:
    """生成10位唯一数字ID"""
    while True:
        # 生成10位数字ID
        new_id = ''.join(random.choices(string.digits, k=10))
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id

def update_id_system():
    """更新ID系统"""
    print("="*80)
    print("更新黑名单ID系统")
    print("="*80)
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host='47.109.97.153',
            port=3306,
            user='root',
            password='Root@2025!',
            database='blacklist',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 1. 添加序号字段
        print("1. 添加序号字段...")
        try:
            cursor.execute("ALTER TABLE blacklist ADD COLUMN sequence_number INT AFTER id")
            print("✓ 序号字段添加成功")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✓ 序号字段已存在")
            else:
                print(f"✗ 添加序号字段失败: {e}")
                return False
        
        # 2. 添加新ID字段
        print("2. 添加新ID字段...")
        try:
            cursor.execute("ALTER TABLE blacklist ADD COLUMN new_id VARCHAR(10) UNIQUE AFTER sequence_number")
            print("✓ 新ID字段添加成功")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✓ 新ID字段已存在")
            else:
                print(f"✗ 添加新ID字段失败: {e}")
                return False
        
        # 3. 获取现有记录
        print("3. 获取现有记录...")
        cursor.execute("SELECT id FROM blacklist WHERE is_active = 1 ORDER BY id")
        records = cursor.fetchall()
        print(f"✓ 找到 {len(records)} 条活跃记录")
        
        # 4. 生成唯一ID
        print("4. 生成唯一ID...")
        existing_ids = set()
        new_ids = []
        
        for i, (old_id,) in enumerate(records):
            new_id = generate_unique_id(existing_ids)
            new_ids.append((old_id, new_id, i + 1))
            if (i + 1) % 50 == 0:
                print(f"  已生成 {i + 1} 个ID...")
        
        print(f"✓ 生成了 {len(new_ids)} 个唯一ID")
        
        # 5. 更新记录
        print("5. 更新记录...")
        for old_id, new_id, sequence in new_ids:
            cursor.execute(
                "UPDATE blacklist SET new_id = %s, sequence_number = %s WHERE id = %s",
                (new_id, sequence, old_id)
            )
        
        connection.commit()
        print(f"✓ 更新了 {len(new_ids)} 条记录")
        
        # 6. 验证结果
        print("6. 验证结果...")
        cursor.execute("SELECT COUNT(*) FROM blacklist WHERE new_id IS NOT NULL AND sequence_number IS NOT NULL")
        updated_count = cursor.fetchone()[0]
        print(f"✓ 成功更新 {updated_count} 条记录")
        
        # 7. 显示样本数据
        print("7. 样本数据:")
        cursor.execute("""
            SELECT id, new_id, sequence_number, ktt_name, risk_level 
            FROM blacklist 
            WHERE is_active = 1 
            ORDER BY sequence_number 
            LIMIT 5
        """)
        samples = cursor.fetchall()
        
        for sample in samples:
            print(f"  原ID: {sample[0]}, 新ID: {sample[1]}, 序号: {sample[2]}, KTT: {sample[3]}, 风险: {sample[4]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ ID系统更新完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        return False

def main():
    """主函数"""
    success = update_id_system()
    
    if success:
        print("\n🎉 ID系统更新成功！")
        print("现在每条记录都有：")
        print("- 原ID: 数据库自增主键")
        print("- 新ID: 10位唯一数字")
        print("- 序号: 显示序号")
    else:
        print("\n❌ ID系统更新失败")

if __name__ == "__main__":
    main()

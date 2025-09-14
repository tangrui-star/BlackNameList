#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理只有电话号码没有名字的记录
"""

import pymysql
import re

def handle_phone_only_records():
    """处理只有电话号码的记录"""
    print("="*80)
    print("处理只有电话号码的记录")
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
        
        # 1. 查找只有电话号码的记录
        print("1. 查找只有电话号码的记录...")
        cursor.execute("""
            SELECT id, order_name_phone 
            FROM blacklist 
            WHERE is_active = 1 AND order_name_phone IS NOT NULL AND order_name_phone != ''
            ORDER BY id
        """)
        records = cursor.fetchall()
        
        phone_only_records = []
        for record_id, order_info in records:
            if not order_info:
                continue
            
            # 检查是否只包含电话号码
            phone_pattern = r'1[3-9]\d{9}'
            phones = re.findall(phone_pattern, order_info)
            
            # 移除电话号码后的文本
            text_without_phones = re.sub(phone_pattern, '', order_info)
            text_without_phones = re.sub(r'[/\s]+', '', text_without_phones).strip()
            
            if phones and not text_without_phones:
                phone_only_records.append((record_id, order_info, phones))
        
        print(f"✓ 找到 {len(phone_only_records)} 条只有电话号码的记录")
        
        if not phone_only_records:
            print("没有需要处理的记录")
            return True
        
        # 2. 显示这些记录
        print("\n只有电话号码的记录:")
        print("-" * 80)
        for record_id, order_info, phones in phone_only_records:
            print(f"ID: {record_id}, 下单人信息: {order_info}, 电话号码: {phones}")
        
        # 3. 询问处理方式
        print("\n处理选项:")
        print("1. 清空下单人信息（设为NULL）")
        print("2. 设为'未知用户'")
        print("3. 保持原样")
        
        # 自动选择选项1：清空下单人信息
        choice = "1"
        print(f"自动选择: {choice}")
        
        # 4. 处理记录
        print("\n2. 处理记录...")
        stats = {
            'total': len(phone_only_records),
            'updated': 0,
            'errors': 0
        }
        
        for record_id, order_info, phones in phone_only_records:
            try:
                if choice == "1":
                    # 清空下单人信息
                    cursor.execute(
                        "UPDATE blacklist SET order_name_phone = NULL WHERE id = %s",
                        (record_id,)
                    )
                    print(f"  ID {record_id}: 清空下单人信息")
                elif choice == "2":
                    # 设为未知用户
                    cursor.execute(
                        "UPDATE blacklist SET order_name_phone = '未知用户' WHERE id = %s",
                        (record_id,)
                    )
                    print(f"  ID {record_id}: 设为'未知用户'")
                else:
                    print(f"  ID {record_id}: 保持原样")
                    continue
                
                stats['updated'] += 1
                
            except Exception as e:
                print(f"  处理记录 {record_id} 时出错: {e}")
                stats['errors'] += 1
        
        # 5. 提交更改
        connection.commit()
        print(f"\n✓ 数据库更新完成")
        
        # 6. 显示统计结果
        print("\n" + "="*80)
        print("处理统计结果")
        print("="*80)
        print(f"总记录数: {stats['total']}")
        print(f"成功更新: {stats['updated']}")
        print(f"处理错误: {stats['errors']}")
        
        # 7. 显示处理后的样本
        print("\n处理后的样本数据:")
        cursor.execute("""
            SELECT id, order_name_phone 
            FROM blacklist 
            WHERE is_active = 1 AND order_name_phone IS NOT NULL AND order_name_phone != ''
            ORDER BY id 
            LIMIT 10
        """)
        samples = cursor.fetchall()
        
        for sample in samples:
            print(f"  ID: {sample[0]}, 下单人信息: {sample[1]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ 只有电话号码的记录处理完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        return False

def main():
    """主函数"""
    success = handle_phone_only_records()
    
    if success:
        print("\n🎉 只有电话号码的记录处理成功！")
    else:
        print("\n❌ 只有电话号码的记录处理失败")

if __name__ == "__main__":
    main()

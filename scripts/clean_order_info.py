#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除下单人信息中的电话号码，只保留名字
"""

import pymysql
import re

def clean_order_info():
    """清除下单人信息中的电话号码"""
    print("="*80)
    print("清除下单人信息中的电话号码")
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
        
        # 1. 获取所有需要处理的记录
        print("1. 获取需要处理的记录...")
        cursor.execute("""
            SELECT id, order_name_phone 
            FROM blacklist 
            WHERE is_active = 1 AND order_name_phone IS NOT NULL AND order_name_phone != ''
            ORDER BY id
        """)
        records = cursor.fetchall()
        print(f"✓ 找到 {len(records)} 条记录需要处理")
        
        # 2. 处理每条记录
        print("\n2. 处理记录...")
        stats = {
            'total_records': len(records),
            'cleaned': 0,
            'no_change': 0,
            'errors': 0,
            'examples': []
        }
        
        for i, (record_id, order_info) in enumerate(records):
            try:
                if not order_info:
                    continue
                
                # 提取电话号码
                phone_pattern = r'1[3-9]\d{9}'
                phones = re.findall(phone_pattern, order_info)
                
                # 移除电话号码，保留名字
                cleaned_info = re.sub(phone_pattern, '', order_info)
                # 清理多余的分隔符和空格
                cleaned_info = re.sub(r'[/\s]+', ' ', cleaned_info).strip()
                # 移除末尾的括号内容（如"（支付宝）"）
                cleaned_info = re.sub(r'（[^）]*）$', '', cleaned_info).strip()
                
                # 如果清理后为空，保留原信息
                if not cleaned_info:
                    cleaned_info = order_info
                
                # 检查是否需要更新
                if cleaned_info != order_info:
                    # 更新数据库
                    cursor.execute(
                        "UPDATE blacklist SET order_name_phone = %s WHERE id = %s",
                        (cleaned_info, record_id)
                    )
                    stats['cleaned'] += 1
                    
                    # 保存示例
                    if len(stats['examples']) < 10:
                        stats['examples'].append({
                            'id': record_id,
                            'original': order_info,
                            'cleaned': cleaned_info,
                            'phones_removed': phones
                        })
                    
                    if (i + 1) % 50 == 0:
                        print(f"  已处理 {i + 1} 条记录...")
                else:
                    stats['no_change'] += 1
                
            except Exception as e:
                print(f"  处理记录 {record_id} 时出错: {e}")
                stats['errors'] += 1
                continue
        
        # 3. 提交更改
        connection.commit()
        print(f"\n✓ 数据库更新完成")
        
        # 4. 显示统计结果
        print("\n" + "="*80)
        print("清理统计结果")
        print("="*80)
        print(f"总记录数: {stats['total_records']}")
        print(f"成功清理: {stats['cleaned']}")
        print(f"无需更改: {stats['no_change']}")
        print(f"处理错误: {stats['errors']}")
        
        # 5. 显示清理示例
        print("\n清理示例:")
        print("-" * 80)
        for example in stats['examples']:
            print(f"ID: {example['id']}")
            print(f"  原始: {example['original']}")
            print(f"  清理后: {example['cleaned']}")
            print(f"  移除的电话: {example['phones_removed']}")
            print()
        
        # 6. 显示清理后的样本
        print("清理后的样本数据:")
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
        
        print("\n✅ 下单人信息清理完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        return False

def main():
    """主函数"""
    success = clean_order_info()
    
    if success:
        print("\n🎉 下单人信息清理成功！")
        print("现在下单人信息栏只包含名字，电话号码已移除")
    else:
        print("\n❌ 下单人信息清理失败")

if __name__ == "__main__":
    main()

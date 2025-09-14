#!/usr/bin/env python3
"""
修复phone_numbers字段格式问题
"""

import pymysql
import json

# 数据库配置
DB_CONFIG = {
    'host': '47.99.134.126',
    'port': 3306,
    'user': 'root',
    'password': 'Tangrui@123',
    'database': 'blacklist_db',
    'charset': 'utf8mb4'
}

def fix_phone_numbers_format():
    """修复phone_numbers字段格式"""
    print("🔧 修复phone_numbers字段格式...")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        
        with connection.cursor() as cursor:
            # 1. 检查phone_numbers字段格式问题
            print("1️⃣ 检查phone_numbers字段格式...")
            cursor.execute("""
                SELECT id, new_id, phone_numbers, 
                       CASE 
                           WHEN phone_numbers IS NULL THEN 'NULL'
                           WHEN JSON_VALID(phone_numbers) THEN 'VALID_JSON'
                           ELSE 'INVALID_JSON'
                       END as json_status
                FROM blacklist 
                WHERE phone_numbers IS NOT NULL
                LIMIT 10
            """)
            
            records = cursor.fetchall()
            print(f"   检查了 {len(records)} 条记录:")
            for record in records:
                print(f"      ID: {record[0]}, new_id: {record[1]}, 状态: {record[3]}")
                if record[3] == 'INVALID_JSON':
                    print(f"        内容: {record[2]}")
            
            # 2. 修复格式错误的记录
            print("\n2️⃣ 修复格式错误的记录...")
            cursor.execute("""
                SELECT id, phone_numbers
                FROM blacklist 
                WHERE phone_numbers IS NOT NULL 
                AND NOT JSON_VALID(phone_numbers)
            """)
            
            invalid_records = cursor.fetchall()
            print(f"   找到 {len(invalid_records)} 条格式错误的记录")
            
            fixed_count = 0
            for record in invalid_records:
                record_id = record[0]
                phone_numbers_str = record[1]
                
                try:
                    # 尝试解析并重新格式化
                    if isinstance(phone_numbers_str, str):
                        # 如果是字符串，尝试解析为列表
                        if phone_numbers_str.startswith('[') and phone_numbers_str.endswith(']'):
                            # 已经是JSON格式的字符串，直接解析
                            parsed = json.loads(phone_numbers_str)
                        else:
                            # 可能是逗号分隔的字符串，转换为列表
                            parsed = [p.strip() for p in phone_numbers_str.split(',') if p.strip()]
                        
                        # 更新记录
                        cursor.execute("""
                            UPDATE blacklist 
                            SET phone_numbers = %s 
                            WHERE id = %s
                        """, (json.dumps(parsed), record_id))
                        
                        fixed_count += 1
                        print(f"      ✅ 修复记录 {record_id}: {phone_numbers_str} -> {parsed}")
                
                except Exception as e:
                    print(f"      ❌ 修复记录 {record_id} 失败: {e}")
            
            print(f"   ✅ 修复了 {fixed_count} 条记录")
            
            # 3. 验证修复结果
            print("\n3️⃣ 验证修复结果...")
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN phone_numbers IS NULL THEN 1 END) as null_count,
                       COUNT(CASE WHEN JSON_VALID(phone_numbers) THEN 1 END) as valid_json_count,
                       COUNT(CASE WHEN NOT JSON_VALID(phone_numbers) THEN 1 END) as invalid_json_count
                FROM blacklist
            """)
            
            stats = cursor.fetchone()
            print(f"   总记录数: {stats[0]}")
            print(f"   空值记录: {stats[1]}")
            print(f"   有效JSON记录: {stats[2]}")
            print(f"   无效JSON记录: {stats[3]}")
            
            # 4. 检查特定记录
            print("\n4️⃣ 检查特定记录 (ID: 938)...")
            cursor.execute("""
                SELECT id, new_id, phone_numbers, order_address1, order_address2
                FROM blacklist 
                WHERE id = 938
            """)
            
            record = cursor.fetchone()
            if record:
                print(f"   ID: {record[0]}")
                print(f"   new_id: {record[1]}")
                print(f"   phone_numbers: {record[2]} (类型: {type(record[2])})")
                print(f"   order_address1: {record[3]}")
                print(f"   order_address2: {record[4]}")
                
                # 如果phone_numbers为空，尝试从其他字段提取
                if not record[2] or record[2] == '[]':
                    print(f"   ⚠️ phone_numbers为空，无法进行电话匹配")
                    print(f"   💡 建议: 该记录只能通过地址匹配")
            
            # 提交事务
            connection.commit()
            print("\n✅ 修复完成！")
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals():
            connection.close()

def main():
    """主函数"""
    print("🔧 修复phone_numbers字段格式问题")
    print("=" * 50)
    
    fix_phone_numbers_format()
    
    print("\n💡 修复后的建议:")
    print("   1. 重新运行检测，看是否能正常匹配")
    print("   2. 对于没有电话号码的黑名单记录，只能通过地址匹配")
    print("   3. 考虑为没有电话号码的记录添加电话号码数据")

if __name__ == "__main__":
    main()

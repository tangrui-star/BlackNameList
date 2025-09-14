#!/usr/bin/env python3
"""
合并黑名单数据库中的phone和phone_numbers字段
保留phone_numbers作为匹配源
"""

import requests
import json
import pymysql
from sqlalchemy import create_engine, text

# 数据库配置
DB_CONFIG = {
    'host': '47.99.134.126',
    'port': 3306,
    'user': 'root',
    'password': 'Tangrui@123',
    'database': 'blacklist_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        return connection
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def check_blacklist_structure():
    """检查黑名单表结构"""
    print("🔍 检查黑名单表结构...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            # 查看表结构
            cursor.execute("DESCRIBE blacklist")
            columns = cursor.fetchall()
            
            print("📋 黑名单表结构:")
            for column in columns:
                print(f"   - {column[0]}: {column[1]} {column[2]} {column[3]}")
            
            # 检查phone和phone_numbers字段的数据
            cursor.execute("""
                SELECT 
                    id, 
                    name, 
                    phone, 
                    phone_numbers,
                    LENGTH(phone) as phone_len,
                    LENGTH(phone_numbers) as phone_numbers_len
                FROM blacklist 
                WHERE phone IS NOT NULL OR phone_numbers IS NOT NULL
                LIMIT 10
            """)
            
            records = cursor.fetchall()
            print(f"\n📊 前10条记录对比:")
            print(f"{'ID':<5} {'姓名':<10} {'phone':<15} {'phone_numbers':<20} {'phone长度':<8} {'phone_numbers长度':<12}")
            print("-" * 80)
            
            for record in records:
                print(f"{record[0]:<5} {record[1]:<10} {str(record[2]):<15} {str(record[3]):<20} {record[4]:<8} {record[5]:<12}")
            
            # 统计字段使用情况
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(phone) as phone_count,
                    COUNT(phone_numbers) as phone_numbers_count,
                    COUNT(CASE WHEN phone IS NOT NULL AND phone_numbers IS NOT NULL THEN 1 END) as both_fields,
                    COUNT(CASE WHEN phone IS NOT NULL AND phone_numbers IS NULL THEN 1 END) as only_phone,
                    COUNT(CASE WHEN phone IS NULL AND phone_numbers IS NOT NULL THEN 1 END) as only_phone_numbers
                FROM blacklist
            """)
            
            stats = cursor.fetchone()
            print(f"\n📈 字段使用统计:")
            print(f"   总记录数: {stats[0]}")
            print(f"   phone字段有数据: {stats[1]}")
            print(f"   phone_numbers字段有数据: {stats[2]}")
            print(f"   两个字段都有数据: {stats[3]}")
            print(f"   只有phone字段有数据: {stats[4]}")
            print(f"   只有phone_numbers字段有数据: {stats[5]}")
            
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
    finally:
        connection.close()

def merge_phone_fields():
    """合并phone和phone_numbers字段"""
    print("\n🔄 开始合并phone和phone_numbers字段...")
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            # 1. 备份原始数据
            print("1️⃣ 创建备份表...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blacklist_backup_phone_merge AS 
                SELECT * FROM blacklist
            """)
            print("   ✅ 备份表创建成功")
            
            # 2. 更新策略：优先使用phone_numbers，如果为空则使用phone
            print("2️⃣ 更新phone_numbers字段...")
            cursor.execute("""
                UPDATE blacklist 
                SET phone_numbers = CASE 
                    WHEN phone_numbers IS NULL OR phone_numbers = '' THEN phone
                    ELSE phone_numbers
                END
                WHERE phone IS NOT NULL AND phone != ''
            """)
            
            updated_rows = cursor.rowcount
            print(f"   ✅ 更新了 {updated_rows} 条记录")
            
            # 3. 将phone字段设置为NULL（因为现在使用phone_numbers作为匹配源）
            print("3️⃣ 清空phone字段...")
            cursor.execute("UPDATE blacklist SET phone = NULL")
            print("   ✅ phone字段已清空")
            
            # 4. 验证合并结果
            print("4️⃣ 验证合并结果...")
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(phone_numbers) as phone_numbers_count,
                    COUNT(phone) as phone_count
                FROM blacklist
            """)
            
            stats = cursor.fetchone()
            print(f"   📊 合并后统计:")
            print(f"      总记录数: {stats[0]}")
            print(f"      phone_numbers有数据: {stats[1]}")
            print(f"      phone字段为空: {stats[2] == 0}")
            
            # 5. 显示一些合并后的示例数据
            cursor.execute("""
                SELECT id, name, phone_numbers 
                FROM blacklist 
                WHERE phone_numbers IS NOT NULL 
                LIMIT 5
            """)
            
            samples = cursor.fetchall()
            print(f"\n📋 合并后的示例数据:")
            for sample in samples:
                print(f"   ID: {sample[0]}, 姓名: {sample[1]}, 电话: {sample[2]}")
            
            # 提交事务
            connection.commit()
            print("\n✅ 字段合并完成！")
            
    except Exception as e:
        print(f"❌ 合并字段失败: {e}")
        connection.rollback()
    finally:
        connection.close()

def update_matching_logic():
    """更新匹配逻辑，使用phone_numbers字段"""
    print("\n🔧 更新匹配逻辑...")
    
    # 这里需要更新后端的匹配逻辑
    print("📝 需要更新以下文件中的匹配逻辑:")
    print("   1. app/services/blacklist_matcher.py")
    print("   2. 将匹配逻辑从使用 'phone' 字段改为使用 'phone_numbers' 字段")
    
    # 检查当前的匹配逻辑
    try:
        with open('blacklist-backend/app/services/blacklist_matcher.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'phone' in content:
            print("   ⚠️ 发现使用 'phone' 字段的匹配逻辑")
            print("   📋 需要将以下内容更新:")
            print("      - 查询条件中的 'phone' 改为 'phone_numbers'")
            print("      - 匹配逻辑中的字段名更新")
        else:
            print("   ✅ 匹配逻辑中未发现 'phone' 字段使用")
            
    except FileNotFoundError:
        print("   ❌ 未找到 blacklist_matcher.py 文件")

def main():
    """主函数"""
    print("🔄 合并黑名单数据库phone字段")
    print("=" * 50)
    
    # 检查表结构
    check_blacklist_structure()
    
    # 询问是否继续
    print("\n⚠️ 警告: 此操作将修改数据库结构，请确认是否继续？")
    print("   1. 将phone和phone_numbers字段合并到phone_numbers")
    print("   2. 清空phone字段")
    print("   3. 创建备份表")
    
    confirm = input("\n是否继续？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    # 执行合并
    merge_phone_fields()
    
    # 更新匹配逻辑说明
    update_matching_logic()
    
    print("\n✅ 操作完成！")
    print("📝 下一步需要:")
    print("   1. 更新后端匹配逻辑使用phone_numbers字段")
    print("   2. 测试匹配功能是否正常")

if __name__ == "__main__":
    main()

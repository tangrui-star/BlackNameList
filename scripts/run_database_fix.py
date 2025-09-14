#!/usr/bin/env python3
"""
执行数据库修复脚本
"""
import mysql.connector
from mysql.connector import Error
import os

def get_db_config():
    """获取数据库配置"""
    return {
        'host': os.getenv('DB_HOST', '47.109.97.153'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'Root@2025!'),
        'database': os.getenv('DB_NAME', 'blacklist'),
        'charset': 'utf8mb4',
        'autocommit': True
    }

def run_sql_file():
    """执行SQL修复脚本"""
    config = get_db_config()
    
    try:
        # 连接数据库
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ 数据库连接成功")
        
        # 读取SQL文件
        with open('fix_database_schema.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # 分割SQL语句
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"准备执行 {len(sql_statements)} 条SQL语句")
        
        # 执行每个SQL语句
        for i, sql in enumerate(sql_statements, 1):
            if sql.upper().startswith('USE '):
                continue  # 跳过USE语句
                
            try:
                print(f"执行语句 {i}: {sql[:100]}...")
                cursor.execute(sql)
                print(f"✅ 语句 {i} 执行成功")
            except Error as e:
                if e.errno == 1060:  # 字段已存在
                    print(f"⚠️  语句 {i} 跳过（字段已存在）: {e}")
                elif e.errno == 1054:  # 字段不存在
                    print(f"⚠️  语句 {i} 跳过（字段不存在）: {e}")
                else:
                    print(f"❌ 语句 {i} 执行失败: {e}")
        
        print("🎉 数据库修复完成")
        
    except Error as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")
    
    return True

def main():
    """主函数"""
    print("=== 数据库修复工具 ===")
    
    if run_sql_file():
        print("\n🎉 数据库修复成功！")
    else:
        print("\n❌ 数据库修复失败！")

if __name__ == "__main__":
    main()

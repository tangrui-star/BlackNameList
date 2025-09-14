#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接服务器数据库并创建 blacklist 数据库
"""

import pymysql
import sys
from pathlib import Path

def connect_and_create_database():
    """连接到服务器数据库并创建 blacklist 数据库"""
    
    # 服务器数据库配置
    config = {
        'host': '47.109.97.153',
        'port': 3306,
        'user': 'root',
        'password': 'Root@2025!',
        'charset': 'utf8mb4'
    }
    
    print("=" * 60)
    print("黑名单管理系统 - 服务器数据库连接")
    print("=" * 60)
    print(f"服务器地址: {config['host']}:{config['port']}")
    print(f"用户名: {config['user']}")
    print("=" * 60)
    
    try:
        # 连接到MySQL服务器（不指定数据库）
        print("正在连接MySQL服务器...")
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # 显示MySQL版本
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✓ 连接成功！MySQL版本: {version}")
        
        # 显示现有数据库
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print(f"✓ 现有数据库: {[db[0] for db in databases]}")
        
        # 创建 blacklist 数据库
        database_name = 'blacklist'
        print(f"\n正在创建数据库: {database_name}")
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ 数据库 {database_name} 创建成功")
        
        # 选择数据库
        cursor.execute(f"USE {database_name}")
        print(f"✓ 已切换到数据库 {database_name}")
        
        # 显示数据库中的表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables:
            print(f"✓ 数据库中的表: {[table[0] for table in tables]}")
        else:
            print("✓ 数据库为空，可以开始创建表结构")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✓ 数据库连接和创建完成！")
        print("=" * 60)
        print(f"数据库名称: {database_name}")
        print(f"服务器地址: {config['host']}:{config['port']}")
        print("现在可以运行数据库初始化脚本来创建表结构了。")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 连接失败: {e}")
        print("\n请检查:")
        print("1. 服务器是否可访问")
        print("2. 用户名和密码是否正确")
        print("3. 端口是否开放")
        print("4. 网络连接是否正常")
        
        return False

def test_connection():
    """测试数据库连接"""
    config = {
        'host': '47.109.97.153',
        'port': 3306,
        'user': 'root',
        'password': 'Root@2025!',
        'database': 'blacklist',
        'charset': 'utf8mb4'
    }
    
    try:
        print("正在测试数据库连接...")
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # 测试查询
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()[0]
        print(f"✓ 当前数据库: {current_db}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ 数据库中的表: {[table[0] for table in tables] if tables else '无'}")
        
        cursor.close()
        connection.close()
        
        print("✓ 数据库连接测试成功！")
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {e}")
        return False

def main():
    """主函数"""
    try:
        # 连接并创建数据库
        if connect_and_create_database():
            print("\n" + "=" * 40)
            print("测试数据库连接...")
            print("=" * 40)
            test_connection()
        
        input("\n按回车键退出...")
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n\n发生未知错误: {e}")

if __name__ == "__main__":
    main()

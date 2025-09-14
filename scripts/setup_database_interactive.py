#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式数据库设置脚本
"""

import pymysql
import getpass
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def get_db_config():
    """获取数据库配置"""
    print("请输入MySQL数据库连接信息:")
    
    host = input("主机地址 (默认: localhost): ").strip() or "localhost"
    port = input("端口 (默认: 3306): ").strip() or "3306"
    user = input("用户名 (默认: root): ").strip() or "root"
    password = getpass.getpass("密码: ")
    
    try:
        port = int(port)
    except ValueError:
        port = 3306
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'charset': 'utf8mb4'
    }

def create_database(config):
    """创建数据库"""
    database_name = 'blacklist_system'
    
    print(f"\n正在连接MySQL服务器 {config['host']}:{config['port']}...")
    try:
        # 连接MySQL服务器（不指定数据库）
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # 创建数据库
        print(f"正在创建数据库: {database_name}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ 数据库 {database_name} 创建成功")
        
        # 选择数据库
        cursor.execute(f"USE {database_name}")
        print(f"✓ 已切换到数据库 {database_name}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")
        return False

def execute_sql_file(config):
    """执行SQL文件"""
    config['database'] = 'blacklist_system'
    
    sql_file = project_root / 'scripts' / 'init_database.sql'
    
    if not sql_file.exists():
        print(f"✗ SQL文件不存在: {sql_file}")
        return False
    
    print("\n正在读取SQL文件...")
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("正在连接数据库...")
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # 分割SQL语句（以分号分隔）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"正在执行 {len(sql_statements)} 条SQL语句...")
        
        success_count = 0
        for i, statement in enumerate(sql_statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    success_count += 1
                    if i % 10 == 0 or i == len(sql_statements):
                        print(f"✓ 已执行 {success_count}/{len(sql_statements)} 条SQL语句")
                except Exception as e:
                    print(f"✗ 执行第 {i} 条SQL语句失败: {e}")
                    if "Duplicate entry" not in str(e):
                        print(f"SQL语句: {statement[:100]}...")
        
        connection.commit()
        print("✓ 所有SQL语句执行完成")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 执行SQL文件失败: {e}")
        return False

def test_connection(config):
    """测试数据库连接"""
    config['database'] = 'blacklist_system'
    
    try:
        print("\n正在测试数据库连接...")
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # 测试查询
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ 用户表中有 {user_count} 条记录")
        
        cursor.execute("SELECT COUNT(*) FROM blacklist")
        blacklist_count = cursor.fetchone()[0]
        print(f"✓ 黑名单表中有 {blacklist_count} 条记录")
        
        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]
        print(f"✓ 角色表中有 {role_count} 条记录")
        
        # 显示默认管理员信息
        cursor.execute("SELECT username, email FROM users WHERE role_id = 1 LIMIT 1")
        admin_user = cursor.fetchone()
        if admin_user:
            print(f"✓ 默认管理员: {admin_user[0]} ({admin_user[1]})")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {e}")
        return False

def save_config(config):
    """保存数据库配置到环境文件"""
    env_file = project_root / '.env'
    
    config_content = f"""# 数据库配置
DB_HOST={config['host']}
DB_PORT={config['port']}
DB_USER={config['user']}
DB_PASSWORD={config['password']}
DB_DATABASE=blacklist_system

# 其他配置
JWT_SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ENVIRONMENT=development
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✓ 数据库配置已保存到 {env_file}")
        return True
    except Exception as e:
        print(f"✗ 保存配置文件失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("黑名单管理系统 - 数据库初始化")
    print("=" * 60)
    
    # 获取数据库配置
    config = get_db_config()
    
    # 步骤1: 创建数据库
    print("\n步骤1: 创建数据库")
    if not create_database(config):
        print("数据库创建失败，退出程序")
        return False
    
    # 步骤2: 执行SQL文件
    print("\n步骤2: 创建表结构和初始数据")
    if not execute_sql_file(config):
        print("SQL文件执行失败，退出程序")
        return False
    
    # 步骤3: 测试连接
    print("\n步骤3: 测试数据库连接")
    if not test_connection(config):
        print("数据库连接测试失败")
        return False
    
    # 步骤4: 保存配置
    print("\n步骤4: 保存数据库配置")
    save_config(config)
    
    print("\n" + "=" * 60)
    print("✓ 数据库初始化完成！")
    print("=" * 60)
    print("\n默认管理员账户:")
    print("用户名: admin")
    print("密码: admin123")
    print("邮箱: admin@blacklist.com")
    print("\n⚠️  请及时修改默认密码！")
    print("\n下一步:")
    print("1. 启动后端服务")
    print("2. 启动前端服务")
    print("3. 访问系统并修改默认密码")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n发生未知错误: {e}")
        sys.exit(1)


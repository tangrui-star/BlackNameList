#!/usr/bin/env python3
"""
初始化用户数据脚本
"""
import pymysql
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_users():
    """初始化用户数据"""
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
        
        with connection.cursor() as cursor:
            # 读取 SQL 文件
            with open('scripts/init_users.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 分割 SQL 语句并执行
            sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for sql in sql_statements:
                if sql:
                    logger.info(f"执行 SQL: {sql[:50]}...")
                    cursor.execute(sql)
            
            connection.commit()
            logger.info("用户数据初始化完成")
            return True
            
    except Exception as e:
        logger.error(f"初始化用户数据失败: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    success = init_users()
    if success:
        print("✅ 用户数据初始化成功")
        print("默认管理员账户: admin/admin123")
        print("测试操作员账户: operator/operator123")
    else:
        print("❌ 用户数据初始化失败")

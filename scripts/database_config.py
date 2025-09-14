#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置文件
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据库配置
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_DATABASE', 'blacklist_system'),
    'charset': 'utf8mb4'
}

# SQLAlchemy配置
SQLALCHEMY_CONFIG = {
    'url': f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}?charset={DATABASE_CONFIG['charset']}",
    'echo': False,  # 是否打印SQL语句
    'pool_size': 10,  # 连接池大小
    'max_overflow': 20,  # 连接池最大溢出
    'pool_timeout': 30,  # 连接池超时时间
    'pool_recycle': 3600,  # 连接回收时间
}

# Redis配置
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD', None),
    'decode_responses': True
}

# JWT配置
JWT_CONFIG = {
    'secret_key': os.getenv('JWT_SECRET_KEY', 'your-secret-key-here-change-in-production'),
    'algorithm': 'HS256',
    'access_token_expire_minutes': 30,
    'refresh_token_expire_days': 7
}

# 文件上传配置
UPLOAD_CONFIG = {
    'max_size': 10 * 1024 * 1024,  # 10MB
    'allowed_extensions': ['.xlsx', '.xls', '.csv'],
    'upload_path': PROJECT_ROOT / 'data' / 'uploads',
    'export_path': PROJECT_ROOT / 'data' / 'exports'
}

# 匹配算法配置
MATCH_CONFIG = {
    'phone_weight': 100,
    'name_weight': 80,
    'ktt_weight': 60,
    'address_weight': 40,
    'threshold': 70,
    'fuzzy_threshold': 80
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}',
    'rotation': '1 day',
    'retention': '30 days',
    'log_path': PROJECT_ROOT / 'blacklist-backend' / 'logs'
}

# 分页配置
PAGINATION_CONFIG = {
    'default_page_size': 20,
    'max_page_size': 100
}

# 缓存配置
CACHE_CONFIG = {
    'default_timeout': 300,  # 5分钟
    'user_cache_timeout': 1800,  # 30分钟
    'blacklist_cache_timeout': 3600,  # 1小时
}

def get_database_url():
    """获取数据库连接URL"""
    return SQLALCHEMY_CONFIG['url']

def get_redis_url():
    """获取Redis连接URL"""
    password_part = f":{REDIS_CONFIG['password']}@" if REDIS_CONFIG['password'] else "@"
    return f"redis://{password_part}{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}"


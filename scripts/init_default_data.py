#!/usr/bin/env python3
"""
初始化默认数据脚本
创建默认角色和用户
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'blacklist-backend'))

import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import Role, User, Permission
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_default_data():
    """初始化默认数据"""
    try:
        # 创建数据库连接
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        logger.info("开始初始化默认数据...")
        
        # 1. 创建默认权限
        permissions_data = [
            {"name": "user_read", "resource": "user", "action": "read", "description": "查看用户"},
            {"name": "user_write", "resource": "user", "action": "write", "description": "编辑用户"},
            {"name": "user_delete", "resource": "user", "action": "delete", "description": "删除用户"},
            {"name": "blacklist_read", "resource": "blacklist", "action": "read", "description": "查看黑名单"},
            {"name": "blacklist_write", "resource": "blacklist", "action": "write", "description": "编辑黑名单"},
            {"name": "blacklist_delete", "resource": "blacklist", "action": "delete", "description": "删除黑名单"},
            {"name": "screening_read", "resource": "screening", "action": "read", "description": "查看筛查"},
            {"name": "screening_write", "resource": "screening", "action": "write", "description": "执行筛查"},
            {"name": "admin_read", "resource": "admin", "action": "read", "description": "查看系统管理"},
            {"name": "admin_write", "resource": "admin", "action": "write", "description": "系统管理"},
        ]
        
        for perm_data in permissions_data:
            existing_perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing_perm:
                permission = Permission(**perm_data)
                db.add(permission)
                logger.info(f"创建权限: {perm_data['name']}")
        
        db.commit()
        
        # 2. 创建默认角色
        roles_data = [
            {
                "name": "超级管理员",
                "description": "拥有所有权限",
                "permissions": ["user_read", "user_write", "user_delete", "blacklist_read", "blacklist_write", "blacklist_delete", "screening_read", "screening_write", "admin_read", "admin_write"]
            },
            {
                "name": "管理员",
                "description": "拥有大部分权限",
                "permissions": ["user_read", "user_write", "blacklist_read", "blacklist_write", "blacklist_delete", "screening_read", "screening_write", "admin_read"]
            },
            {
                "name": "操作员",
                "description": "拥有基本操作权限",
                "permissions": ["blacklist_read", "blacklist_write", "screening_read", "screening_write"]
            },
            {
                "name": "只读用户",
                "description": "只能查看数据",
                "permissions": ["blacklist_read", "screening_read"]
            }
        ]
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                logger.info(f"创建角色: {role_data['name']}")
        
        db.commit()
        
        # 3. 创建默认管理员用户
        admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
        if not admin_role:
            logger.error("超级管理员角色不存在")
            return False
        
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@blacklist.com",
                password_hash=get_password_hash("admin123"),
                full_name="系统管理员",
                phone="13800138000",
                role_id=admin_role.id,
                is_active=True
            )
            db.add(admin_user)
            logger.info("创建默认管理员用户: admin/admin123")
        else:
            logger.info("管理员用户已存在")
        
        # 4. 创建测试用户
        operator_role = db.query(Role).filter(Role.name == "操作员").first()
        if operator_role:
            existing_operator = db.query(User).filter(User.username == "operator").first()
            if not existing_operator:
                operator_user = User(
                    username="operator",
                    email="operator@blacklist.com",
                    password_hash=get_password_hash("operator123"),
                    full_name="操作员",
                    phone="13800138001",
                    role_id=operator_role.id,
                    is_active=True
                )
                db.add(operator_user)
                logger.info("创建测试操作员用户: operator/operator123")
        
        db.commit()
        logger.info("默认数据初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"初始化默认数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_default_data()
    if success:
        print("✅ 默认数据初始化成功")
        print("默认管理员账户: admin/admin123")
        print("测试操作员账户: operator/operator123")
    else:
        print("❌ 默认数据初始化失败")
        sys.exit(1)

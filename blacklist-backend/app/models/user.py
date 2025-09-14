"""
用户相关模型
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Enum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class RiskLevel(str, enum.Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Permission(BaseModel):
    """权限表"""
    __tablename__ = "permissions"
    
    name = Column(String(50), unique=True, nullable=False, comment="权限名称")
    resource = Column(String(50), nullable=False, comment="资源名称")
    action = Column(String(50), nullable=False, comment="操作类型")
    description = Column(Text, comment="权限描述")


class Role(BaseModel):
    """角色表"""
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    description = Column(Text, comment="角色描述")
    permissions = Column(JSON, comment="权限列表")
    
    # 关系
    users = relationship("User", back_populates="role")


class User(BaseModel):
    """用户表"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    full_name = Column(String(100), comment="全名")
    phone = Column(String(20), comment="电话号码")
    role_id = Column(Integer, ForeignKey("roles.id"), comment="角色ID")
    last_login = Column(DateTime(timezone=True), comment="最后登录时间")
    
    # 关系
    role = relationship("Role", back_populates="users")
    created_blacklists = relationship("Blacklist", back_populates="creator")
    screening_tasks = relationship("ScreeningTask", back_populates="creator")
    operation_logs = relationship("OperationLog", back_populates="user")

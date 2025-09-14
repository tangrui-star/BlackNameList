"""
用户相关数据模式
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None


class UserCreate(UserBase):
    """创建用户模式"""
    password: str


class UserUpdate(BaseModel):
    """更新用户模式"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """角色响应模式"""
    id: int
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

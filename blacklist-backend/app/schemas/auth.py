"""
认证相关数据模式
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    name: str
    description: Optional[str] = None
    permissions: Optional[list] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    role: Optional[RoleResponse] = None
    is_active: bool
    last_login: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

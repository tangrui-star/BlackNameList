"""
用户管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, Role
from app.schemas.user import UserResponse, UserCreate, UserUpdate, RoleResponse
from app.api.v1.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/list", response_model=List[UserResponse])
async def get_users(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限查看用户列表")
    
    skip = request_data.get("skip", 0)
    limit = request_data.get("limit", 100)
    role_id = request_data.get("role_id")
    is_active = request_data.get("is_active")
    search = request_data.get("search", "")
    
    # 构建查询
    query = db.query(User).filter(User.is_active == True)
    
    # 角色筛选
    if role_id:
        query = query.filter(User.role_id == role_id)
    
    # 激活状态筛选
    if is_active is not None and is_active != "":
        query = query.filter(User.is_active == (is_active == "true" or is_active == True))
    
    # 搜索筛选
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.full_name.contains(search)) |
            (User.email.contains(search))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise NotFoundError("用户", str(user_id))
    
    return user


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建用户"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限创建用户")
    
    # 检查用户名和邮箱是否已存在
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名或邮箱已存在"
        )
    
    # 创建用户
    from app.core.security import get_password_hash
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role_id=user_data.role_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"用户 {user.username} 创建成功")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限更新用户")
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise NotFoundError("用户", str(user_id))
    
    # 更新用户信息
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password" and value:
            from app.core.security import get_password_hash
            setattr(user, "password_hash", get_password_hash(value))
        elif field != "password":
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"用户 {user.username} 更新成功")
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户（软删除）"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限删除用户")
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise NotFoundError("用户", str(user_id))
    
    # 软删除
    user.is_active = False
    db.commit()
    
    logger.info(f"用户 {user.username} 删除成功")
    return {"message": "用户删除成功"}


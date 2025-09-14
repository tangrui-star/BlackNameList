"""
认证相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token, get_password_hash
from app.core.exceptions import AuthenticationError, UnauthorizedError
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, RefreshTokenRequest, UserResponse, RegisterRequest

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise UnauthorizedError("无效的访问令牌")
    
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("令牌中缺少用户信息")
    
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise UnauthorizedError("用户不存在或已被禁用")
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    try:
        # 查找用户（包含角色信息）
        user = db.query(User).options(joinedload(User.role)).filter(
            (User.username == login_data.username) | (User.email == login_data.username),
            User.is_active == True
        ).first()
        
        if not user:
            raise AuthenticationError("用户名或密码错误")
        
        # 验证密码
        if not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("用户名或密码错误")
        
        # 创建令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # 更新最后登录时间
        from datetime import datetime
        user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()
        
        logger.info(f"用户 {user.username} 登录成功")
        
        # 构建角色响应
        role_response = None
        if user.role:
            role_response = {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description,
                "permissions": user.role.permissions,
                "is_active": user.role.is_active,
                "created_at": user.role.created_at,
                "updated_at": user.role.updated_at
            }
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                role_id=user.role_id,
                role=role_response,
                is_active=user.is_active,
                last_login=str(user.last_login) if user.last_login else None,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
        
    except AuthenticationError as e:
        logger.warning(f"登录失败: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.post("/register", response_model=UserResponse)
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            (User.username == register_data.username) | (User.email == register_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == register_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        # 获取默认角色（操作员）
        from app.models.user import Role
        default_role = db.query(Role).filter(Role.name == "操作员").first()
        if not default_role:
            # 如果没有操作员角色，使用第一个角色
            default_role = db.query(Role).first()
        
        # 创建新用户
        new_user = User(
            username=register_data.username,
            email=register_data.email,
            password_hash=get_password_hash(register_data.password),
            full_name=register_data.full_name or register_data.username,
            phone=register_data.phone,
            role_id=default_role.id if default_role else None,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"用户 {new_user.username} 注册成功")
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            phone=new_user.phone,
            role_id=new_user.role_id,
            is_active=new_user.is_active,
            last_login=str(new_user.last_login) if new_user.last_login else None,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册异常: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        payload = verify_token(refresh_data.refresh_token, token_type="refresh")
        if not payload:
            raise AuthenticationError("无效的刷新令牌")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise AuthenticationError("用户不存在或已被禁用")
        
        # 创建新的访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                role_id=user.role_id,
                is_active=user.is_active,
                last_login=str(user.last_login) if user.last_login else None,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
        
    except AuthenticationError as e:
        logger.warning(f"令牌刷新失败: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"令牌刷新异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    # 构建角色响应
    role_response = None
    if current_user.role:
        role_response = {
            "id": current_user.role.id,
            "name": current_user.role.name,
            "description": current_user.role.description,
            "permissions": current_user.role.permissions,
            "is_active": current_user.role.is_active,
            "created_at": current_user.role.created_at,
            "updated_at": current_user.role.updated_at
        }
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role_id=current_user.role_id,
        role=role_response,
        is_active=current_user.is_active,
        last_login=str(current_user.last_login) if current_user.last_login else None,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/logout")
async def logout():
    """用户登出"""
    # 在实际应用中，可以将令牌加入黑名单
    return {"message": "登出成功"}

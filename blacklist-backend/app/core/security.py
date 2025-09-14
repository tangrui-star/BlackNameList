"""
安全相关功能：密码哈希、JWT token等
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"密码验证失败: {e}")
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"密码哈希生成失败: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"访问令牌创建失败: {e}")
        raise


def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"刷新令牌创建失败: {e}")
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != token_type:
            logger.warning(f"令牌类型不匹配: 期望 {token_type}, 实际 {payload.get('type')}")
            return None
        
        # 检查过期时间
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning("令牌已过期")
            return None
        
        return payload
    except JWTError as e:
        logger.error(f"令牌验证失败: {e}")
        return None
    except Exception as e:
        logger.error(f"令牌处理异常: {e}")
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """从令牌中获取用户ID"""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None

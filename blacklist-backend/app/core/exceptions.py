"""
自定义异常类
"""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class BlacklistException(Exception):
    """黑名单系统基础异常"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BlacklistException):
    """认证异常"""
    pass


class AuthorizationError(BlacklistException):
    """授权异常"""
    pass


class ValidationError(BlacklistException):
    """数据验证异常"""
    pass


class DatabaseError(BlacklistException):
    """数据库异常"""
    pass


class FileProcessingError(BlacklistException):
    """文件处理异常"""
    pass


class MatchingError(BlacklistException):
    """匹配算法异常"""
    pass


# HTTP异常映射
def create_http_exception(
    status_code: int,
    detail: str,
    headers: Optional[Dict[str, str]] = None
) -> HTTPException:
    """创建HTTP异常"""
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


# 常用异常
class NotFoundError(HTTPException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id {resource_id} not found"
        )


class ConflictError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BadRequestError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class InternalServerError(HTTPException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

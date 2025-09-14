"""
角色管理API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.models.user import Role
from app.schemas.user import RoleResponse
from app.api.v1.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/list", response_model=List[RoleResponse])
async def get_roles(
    request_data: dict = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取角色列表"""
    roles = db.query(Role).filter(Role.is_active == True).all()
    return roles

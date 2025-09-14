"""
分组相关数据模式
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GroupStatus(str, Enum):
    """分组状态枚举"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class GroupBase(BaseModel):
    """分组基础模式"""
    name: str
    description: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    status: GroupStatus = GroupStatus.ACTIVE


class GroupCreate(GroupBase):
    """创建分组模式"""
    pass


class GroupUpdate(BaseModel):
    """更新分组模式"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[GroupStatus] = None


class GroupInDB(GroupBase):
    """分组数据库模式"""
    id: int
    total_orders: int = 0
    checked_orders: int = 0
    blacklist_matches: int = 0
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


class Group(GroupInDB):
    """分组响应模式"""
    pass

class GroupResponse(GroupInDB):
    """分组响应模式（别名）"""
    pass


class GroupListResponse(BaseModel):
    """分组列表响应模式"""
    data: List[GroupInDB]
    total: int
    page: int
    size: int
    pages: int


class GroupSearchParams(BaseModel):
    """分组搜索参数"""
    skip: int = 0
    limit: int = 20
    status: Optional[str] = None
    search: Optional[str] = None


class GroupDetailRequest(BaseModel):
    """分组详情请求"""
    group_id: int


class GroupBatchCheckRequest(BaseModel):
    """分组批量检测请求"""
    group_id: int
    force_recheck: bool = False


class GroupBatchCheckResponse(BaseModel):
    """分组批量检测响应"""
    group_id: int
    group_name: str
    total_orders: int
    checked_orders: int
    blacklist_matches: int
    new_matches: int
    check_time: datetime
    status: str
    message: str

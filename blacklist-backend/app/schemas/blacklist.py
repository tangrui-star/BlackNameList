"""
黑名单相关数据模式
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BlacklistBase(BaseModel):
    """黑名单基础模式"""
    ktt_name: Optional[str] = None
    wechat_name: Optional[str] = None
    wechat_id: Optional[str] = None
    order_name: Optional[str] = None
    phone: Optional[str] = None
    order_name_phone: Optional[str] = None
    phone_numbers: Optional[List[str]] = None
    order_address1: Optional[str] = None
    order_address2: Optional[str] = None
    blacklist_reason: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM


class BlacklistCreate(BlacklistBase):
    """创建黑名单模式"""
    pass


class BlacklistUpdate(BaseModel):
    """更新黑名单模式"""
    ktt_name: Optional[str] = None
    wechat_name: Optional[str] = None
    wechat_id: Optional[str] = None
    order_name: Optional[str] = None
    phone: Optional[str] = None
    order_name_phone: Optional[str] = None
    phone_numbers: Optional[List[str]] = None
    order_address1: Optional[str] = None
    order_address2: Optional[str] = None
    blacklist_reason: Optional[str] = None
    risk_level: Optional[RiskLevel] = None


class BlacklistResponse(BlacklistBase):
    """黑名单响应模式"""
    id: int
    sequence_number: Optional[int] = None
    new_id: Optional[str] = None
    created_by: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BlacklistHistoryResponse(BaseModel):
    """黑名单历史响应模式"""
    id: int
    blacklist_id: int
    action: str
    old_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None
    changed_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class BlacklistSearchParams(BaseModel):
    """黑名单搜索参数"""
    skip: int = 0
    limit: int = 100
    risk_level: Optional[str] = None
    search: Optional[str] = None

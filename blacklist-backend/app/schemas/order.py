"""
订单相关模式
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus


class OrderBase(BaseModel):
    """订单基础模式"""
    group_id: Optional[int] = None
    group_tour_number: Optional[str] = None
    orderer: Optional[str] = None
    member_remarks: Optional[str] = None
    payment_time: Optional[datetime] = None
    group_leader_remarks: Optional[str] = None
    product: Optional[str] = None
    order_amount: Optional[Decimal] = None
    refund_amount: Optional[Decimal] = 0
    order_status: Optional[Union[OrderStatus, str]] = None
    pickup_point: Optional[str] = None
    consignee: Optional[str] = None
    contact_phone: Optional[str] = None
    detailed_address: Optional[str] = None
    is_blacklist_checked: Optional[str] = "no"
    blacklist_risk_level: Optional[str] = None
    blacklist_match_info: Optional[str] = None
    blacklist_match_details: Optional[str] = None
    
    @validator('order_status', pre=True)
    def validate_order_status(cls, v):
        if v is None or v == "" or v == "":
            return None
        if isinstance(v, str):
            # 尝试转换为OrderStatus枚举
            try:
                return OrderStatus(v.lower())
            except ValueError:
                return None
        return v


class OrderCreate(OrderBase):
    """创建订单模式"""
    pass


class OrderUpdate(OrderBase):
    """更新订单模式"""
    pass


class OrderInDB(OrderBase):
    """数据库中的订单模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class Order(OrderInDB):
    """订单响应模式"""
    pass


class OrderListResponse(BaseModel):
    """订单列表响应模式"""
    data: List[OrderInDB]
    total: int
    page: int
    size: int


class OrderSearchParams(BaseModel):
    """订单搜索参数"""
    group_id: Optional[int] = None
    group_tour_number: Optional[str] = None
    orderer: Optional[str] = None
    contact_phone: Optional[str] = None
    order_status: Optional[Union[OrderStatus, str]] = None
    is_blacklist_checked: Optional[str] = None
    payment_time_start: Optional[datetime] = None
    payment_time_end: Optional[datetime] = None
    skip: int = 0
    limit: int = 20
    
    @validator('order_status', pre=True)
    def validate_order_status(cls, v):
        if v is None or v == "" or v == "":
            return None
        if isinstance(v, str):
            # 尝试转换为OrderStatus枚举
            try:
                return OrderStatus(v.lower())
            except ValueError:
                return None
        return v


class ExcelUploadResponse(BaseModel):
    """Excel上传响应模式"""
    success: bool
    message: str
    imported_count: int
    failed_count: int
    errors: List[str] = []


class BlacklistCheckResponse(BaseModel):
    """黑名单检测响应模式"""
    is_blacklist: bool
    risk_level: Optional[str] = None
    match_info: Optional[str] = None
    matched_blacklist_ids: List[int] = []

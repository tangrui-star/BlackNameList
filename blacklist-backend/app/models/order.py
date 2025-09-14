"""
订单相关模型
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Enum, Index, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from decimal import Decimal
import enum


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"  # 待处理
    PAID = "paid"  # 已支付
    SHIPPED = "shipped"  # 已发货
    DELIVERED = "delivered"  # 已送达
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"  # 已退款


class Order(BaseModel):
    """订单表"""
    __tablename__ = "orders"
    
    # 分组关联
    group_id = Column(Integer, ForeignKey("groups.id"), comment="所属分组ID")
    
    # Excel列头对应字段
    group_tour_number = Column(String(100), comment="跟团号")
    orderer = Column(String(100), comment="下单人（对应ktt名字）")
    member_remarks = Column(Text, comment="团员备注")
    payment_time = Column(DateTime, comment="支付时间")
    group_leader_remarks = Column(Text, comment="团长备注")
    product = Column(String(200), comment="商品")
    order_amount = Column(DECIMAL(10, 2), comment="订单金额")
    refund_amount = Column(DECIMAL(10, 2), default=0, comment="退款金额")
    order_status = Column(Enum(OrderStatus, name="order_status"), default=OrderStatus.PENDING, comment="订单状态")
    pickup_point = Column(String(200), comment="自提点")
    consignee = Column(String(100), comment="收货人")
    contact_phone = Column(String(20), comment="联系电话（对应phone）")
    detailed_address = Column(Text, comment="详细地址")
    
    # 黑名单检测相关
    is_blacklist_checked = Column(String(10), default="no", comment="是否已检测黑名单")
    blacklist_risk_level = Column(String(20), comment="黑名单风险等级")
    blacklist_match_info = Column(Text, comment="黑名单匹配信息")
    blacklist_match_details = Column(Text, comment="黑名单匹配详情")
    
    # 关系
    group = relationship("Group", back_populates="orders")
    
    # 索引
    __table_args__ = (
        Index('idx_group_id', 'group_id'),
        Index('idx_group_tour_number', 'group_tour_number'),
        Index('idx_orderer', 'orderer'),
        Index('idx_contact_phone', 'contact_phone'),
        Index('idx_order_status', 'order_status'),
        Index('idx_payment_time', 'payment_time'),
        Index('idx_is_blacklist_checked', 'is_blacklist_checked'),
    )

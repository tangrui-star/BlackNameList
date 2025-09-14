"""
黑名单相关模型
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Enum, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.user import RiskLevel


class Blacklist(BaseModel):
    """黑名单主表"""
    __tablename__ = "blacklist"
    
    sequence_number = Column(Integer, comment="序号")
    new_id = Column(String(10), unique=True, comment="10位唯一ID")
    ktt_name = Column(String(100), comment="KTT名字")
    wechat_name = Column(String(100), comment="微信名字")
    wechat_id = Column(String(100), comment="微信号")
    order_name_phone = Column(Text, comment="下单名字和电话（原始数据）")
    phone_numbers = Column(JSON, comment="提取的电话号码列表")
    order_address1 = Column(Text, comment="下单地址1")
    order_address2 = Column(Text, comment="下单地址2")
    blacklist_reason = Column(Text, comment="入黑名单原因")
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM, comment="风险等级")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建用户ID")
    
    # 关系
    creator = relationship("User", back_populates="created_blacklists")
    history_records = relationship("BlacklistHistory", back_populates="blacklist")
    screening_results = relationship("ScreeningResult", back_populates="blacklist")
    
    # 索引
    __table_args__ = (
        Index('idx_ktt_name', 'ktt_name'),
        Index('idx_phone_numbers', 'phone_numbers'),
        Index('idx_risk_level', 'risk_level'),
        Index('idx_created_at', 'created_at'),
    )


class BlacklistHistory(BaseModel):
    """黑名单变更历史表"""
    __tablename__ = "blacklist_history"
    
    blacklist_id = Column(Integer, ForeignKey("blacklist.id"), nullable=False, comment="黑名单ID")
    action = Column(Enum("create", "update", "delete"), nullable=False, comment="操作类型")
    old_data = Column(JSON, comment="原始数据")
    new_data = Column(JSON, comment="新数据")
    changed_by = Column(Integer, ForeignKey("users.id"), comment="操作用户ID")
    
    # 关系
    blacklist = relationship("Blacklist", back_populates="history_records")
    changer = relationship("User")
    
    # 索引
    __table_args__ = (
        Index('idx_blacklist_id', 'blacklist_id'),
        Index('idx_action', 'action'),
        Index('idx_changed_at', 'created_at'),
    )

"""
分组模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel
import enum


class GroupStatus(str, enum.Enum):
    """分组状态枚举"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Group(BaseModel):
    """分组模型"""
    __tablename__ = "groups"
    
    name = Column(String(255), nullable=False, comment="分组名称")
    description = Column(Text, comment="分组描述")
    file_name = Column(String(255), comment="原始文件名")
    file_path = Column(String(500), comment="文件路径")
    total_orders = Column(Integer, default=0, comment="订单总数")
    checked_orders = Column(Integer, default=0, comment="已检测订单数")
    blacklist_matches = Column(Integer, default=0, comment="黑名单匹配数")
    status = Column(String(20), default="active", comment="分组状态")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建者ID")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 关系
    orders = relationship("Order", back_populates="group")
    creator = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "total_orders": self.total_orders,
            "checked_orders": self.checked_orders,
            "blacklist_matches": self.blacklist_matches,
            "status": self.status if self.status else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

"""
筛查相关模型
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Enum, Index, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.user import RiskLevel


class ScreeningTask(BaseModel):
    """筛查任务表"""
    __tablename__ = "screening_tasks"
    
    task_name = Column(String(200), nullable=False, comment="任务名称")
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(500), comment="文件路径")
    total_records = Column(Integer, default=0, comment="总记录数")
    processed_records = Column(Integer, default=0, comment="已处理记录数")
    matched_records = Column(Integer, default=0, comment="匹配记录数")
    status = Column(Enum("pending", "processing", "completed", "failed"), 
                   default="pending", comment="任务状态")
    error_message = Column(Text, comment="错误信息")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建用户ID")
    completed_at = Column(String(50), comment="完成时间")
    
    # 关系
    creator = relationship("User", back_populates="screening_tasks")
    results = relationship("ScreeningResult", back_populates="task")
    
    # 索引
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_created_by', 'created_by'),
        Index('idx_created_at', 'created_at'),
    )


class ScreeningResult(BaseModel):
    """筛查结果表"""
    __tablename__ = "screening_results"
    
    task_id = Column(Integer, ForeignKey("screening_tasks.id"), nullable=False, comment="任务ID")
    blacklist_id = Column(Integer, ForeignKey("blacklist.id"), nullable=False, comment="黑名单ID")
    order_data = Column(JSON, comment="订单数据")
    match_type = Column(Enum("phone", "name", "ktt_name", "address"), 
                       nullable=False, comment="匹配类型")
    match_score = Column(DECIMAL(5, 2), comment="匹配分数")
    match_details = Column(Text, comment="匹配详情")
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM, comment="风险等级")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    verified_by = Column(Integer, ForeignKey("users.id"), comment="验证用户ID")
    verified_at = Column(String(50), comment="验证时间")
    
    # 关系
    task = relationship("ScreeningTask", back_populates="results")
    blacklist = relationship("Blacklist", back_populates="screening_results")
    verifier = relationship("User")
    
    # 索引
    __table_args__ = (
        Index('idx_task_id', 'task_id'),
        Index('idx_blacklist_id', 'blacklist_id'),
        Index('idx_match_type', 'match_type'),
        Index('idx_risk_level', 'risk_level'),
        Index('idx_match_score', 'match_score'),
    )


class SystemConfig(BaseModel):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    config_key = Column(String(100), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, comment="配置值")
    description = Column(Text, comment="配置描述")
    config_type = Column(Enum("string", "number", "boolean", "json"), 
                        default="string", comment="配置类型")
    is_editable = Column(Boolean, default=True, comment="是否可编辑")
    
    # 重写is_active字段，因为数据库表中没有这个字段
    @property
    def is_active(self):
        return True


class OperationLog(BaseModel):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    user_id = Column(Integer, ForeignKey("users.id"), comment="用户ID")
    action = Column(String(100), nullable=False, comment="操作类型")
    resource_type = Column(String(50), comment="资源类型")
    resource_id = Column(String(50), comment="资源ID")
    details = Column(JSON, comment="操作详情")
    ip_address = Column(String(45), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    
    # 关系
    user = relationship("User", back_populates="operation_logs")
    
    # 索引
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_action', 'action'),
        Index('idx_resource_type', 'resource_type'),
        Index('idx_created_at', 'created_at'),
    )

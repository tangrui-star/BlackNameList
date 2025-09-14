"""
筛查相关数据模式
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MatchType(str, Enum):
    """匹配类型枚举"""
    PHONE = "phone"
    NAME = "name"
    KTT_NAME = "ktt_name"
    ADDRESS = "address"


class RiskLevel(str, Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ScreeningTaskBase(BaseModel):
    """筛查任务基础模式"""
    task_name: str
    file_name: str
    file_path: Optional[str] = None


class ScreeningTaskCreate(ScreeningTaskBase):
    """创建筛查任务模式"""
    pass


class ScreeningTaskResponse(ScreeningTaskBase):
    """筛查任务响应模式"""
    id: int
    total_records: int = 0
    processed_records: int = 0
    matched_records: int = 0
    status: TaskStatus
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    completed_at: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ScreeningResultResponse(BaseModel):
    """筛查结果响应模式"""
    id: int
    task_id: int
    blacklist_id: int
    order_data: Optional[Dict[str, Any]] = None
    match_type: MatchType
    match_score: Optional[float] = None
    match_details: Optional[str] = None
    risk_level: RiskLevel
    is_verified: str = "false"
    verified_by: Optional[int] = None
    verified_at: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

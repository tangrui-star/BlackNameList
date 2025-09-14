"""
系统管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.models.blacklist import Blacklist
from app.models.screening import ScreeningTask, ScreeningResult, SystemConfig
from app.api.v1.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取系统统计信息"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限查看系统统计")
    
    # 黑名单统计
    total_blacklist = db.query(Blacklist).filter(Blacklist.is_active == True).count()
    high_risk_blacklist = db.query(Blacklist).filter(
        Blacklist.is_active == True,
        Blacklist.risk_level == "high"
    ).count()
    medium_risk_blacklist = db.query(Blacklist).filter(
        Blacklist.is_active == True,
        Blacklist.risk_level == "medium"
    ).count()
    low_risk_blacklist = db.query(Blacklist).filter(
        Blacklist.is_active == True,
        Blacklist.risk_level == "low"
    ).count()
    
    # 筛查任务统计
    total_tasks = db.query(ScreeningTask).count()
    completed_tasks = db.query(ScreeningTask).filter(ScreeningTask.status == "completed").count()
    processing_tasks = db.query(ScreeningTask).filter(ScreeningTask.status == "processing").count()
    pending_tasks = db.query(ScreeningTask).filter(ScreeningTask.status == "pending").count()
    
    # 筛查结果统计
    total_results = db.query(ScreeningResult).count()
    high_risk_results = db.query(ScreeningResult).filter(ScreeningResult.risk_level == "high").count()
    verified_results = db.query(ScreeningResult).filter(ScreeningResult.is_verified == True).count()
    
    # 用户统计
    total_users = db.query(User).filter(User.is_active == True).count()
    
    return {
        "blacklist_stats": {
            "total": total_blacklist,
            "high_risk": high_risk_blacklist,
            "medium_risk": medium_risk_blacklist,
            "low_risk": low_risk_blacklist
        },
        "screening_stats": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "processing_tasks": processing_tasks,
            "pending_tasks": pending_tasks,
            "total_results": total_results,
            "high_risk_results": high_risk_results,
            "verified_results": verified_results
        },
        "user_stats": {
            "total_users": total_users
        }
    }


@router.get("/config")
async def get_system_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取系统配置"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限查看系统配置")
    
    configs = db.query(SystemConfig).all()
    
    config_dict = {}
    for config in configs:
        config_dict[config.config_key] = {
            "value": config.config_value,
            "description": config.description,
            "type": config.config_type,
            "is_editable": config.is_editable
        }
    
    return config_dict


@router.put("/config")
async def update_system_config(
    config_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新系统配置"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限更新系统配置")
    
    updated_configs = []
    for key, value in config_data.items():
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == key
        ).first()
        
        if config and config.is_editable:
            config.config_value = str(value)
            updated_configs.append(key)
    
    db.commit()
    
    logger.info(f"系统配置更新成功: {updated_configs}")
    return {"message": "配置更新成功", "updated_configs": updated_configs}


@router.post("/backup")
async def create_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建数据备份"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员"]:
        raise ForbiddenError("没有权限创建数据备份")
    
    # 这里应该实现实际的备份逻辑
    # 在实际应用中，可以使用mysqldump等工具
    
    logger.info("数据备份请求")
    return {"message": "备份功能开发中"}


@router.get("/logs")
async def get_system_logs(
    skip: int = 0,
    limit: int = 100,
    level: str = "INFO",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取系统日志"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        raise ForbiddenError("没有权限查看系统日志")
    
    # 这里应该实现实际的日志查询逻辑
    # 在实际应用中，可以使用loguru等日志库
    
    logger.info(f"系统日志查询请求: level={level}, skip={skip}, limit={limit}")
    return {"message": "日志查询功能开发中"}

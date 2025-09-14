"""
订单筛查API
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError, FileProcessingError
from app.core.config import settings
from app.models.user import User
from app.models.screening import ScreeningTask, ScreeningResult
from app.schemas.screening import ScreeningTaskResponse, ScreeningResultResponse, ScreeningTaskCreate
from app.api.v1.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=ScreeningTaskResponse)
async def upload_screening_file(
    file: UploadFile = File(...),
    task_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传筛查文件"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限上传筛查文件")
    
    # 检查文件类型
    if not file.filename:
        raise FileProcessingError("文件名不能为空")
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise FileProcessingError(f"不支持的文件类型: {file_extension}")
    
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise FileProcessingError(f"文件大小超过限制: {settings.MAX_UPLOAD_SIZE} bytes")
    
    # 保存文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_PATH, filename)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 创建筛查任务
    task = ScreeningTask(
        task_name=task_name or f"筛查任务_{timestamp}",
        file_name=file.filename,
        file_path=file_path,
        status="pending",
        created_by=current_user.id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    logger.info(f"筛查文件上传成功: {file.filename}, 任务ID: {task.id}")
    return task


@router.get("/tasks", response_model=List[ScreeningTaskResponse])
async def get_screening_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取筛查任务列表"""
    query = db.query(ScreeningTask)
    
    # 状态筛选
    if status:
        query = query.filter(ScreeningTask.status == status)
    
    # 权限控制：非管理员只能看到自己的任务
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]:
        query = query.filter(ScreeningTask.created_by == current_user.id)
    
    tasks = query.offset(skip).limit(limit).order_by(ScreeningTask.created_at.desc()).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=ScreeningTaskResponse)
async def get_screening_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取筛查任务详情"""
    task = db.query(ScreeningTask).filter(ScreeningTask.id == task_id).first()
    if not task:
        raise NotFoundError("筛查任务", str(task_id))
    
    # 权限控制：非管理员只能查看自己的任务
    if (not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]) and task.created_by != current_user.id:
        raise ForbiddenError("没有权限查看此任务")
    
    return task


@router.post("/tasks/{task_id}/start")
async def start_screening_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """开始筛查任务"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限执行筛查任务")
    
    task = db.query(ScreeningTask).filter(ScreeningTask.id == task_id).first()
    if not task:
        raise NotFoundError("筛查任务", str(task_id))
    
    if task.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务状态不允许开始"
        )
    
    # 更新任务状态
    task.status = "processing"
    db.commit()
    
    # 这里应该启动异步筛查任务
    # 在实际应用中，可以使用Celery等任务队列
    logger.info(f"筛查任务 {task_id} 开始执行")
    
    return {"message": "筛查任务已开始", "task_id": task_id}


@router.get("/tasks/{task_id}/results", response_model=List[ScreeningResultResponse])
async def get_screening_results(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取筛查结果"""
    task = db.query(ScreeningTask).filter(ScreeningTask.id == task_id).first()
    if not task:
        raise NotFoundError("筛查任务", str(task_id))
    
    # 权限控制：非管理员只能查看自己的任务结果
    if (not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]) and task.created_by != current_user.id:
        raise ForbiddenError("没有权限查看此任务结果")
    
    query = db.query(ScreeningResult).filter(ScreeningResult.task_id == task_id)
    
    # 风险等级筛选
    if risk_level:
        query = query.filter(ScreeningResult.risk_level == risk_level)
    
    results = query.offset(skip).limit(limit).all()
    return results


@router.post("/tasks/{task_id}/export")
async def export_screening_results(
    task_id: int,
    format: str = "excel",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出筛查结果"""
    # 检查权限
    if not current_user.role or current_user.role.name not in ["超级管理员", "管理员", "操作员"]:
        raise ForbiddenError("没有权限导出筛查结果")
    
    task = db.query(ScreeningTask).filter(ScreeningTask.id == task_id).first()
    if not task:
        raise NotFoundError("筛查任务", str(task_id))
    
    # 权限控制：非管理员只能导出自己的任务结果
    if (not current_user.role or current_user.role.name not in ["超级管理员", "管理员"]) and task.created_by != current_user.id:
        raise ForbiddenError("没有权限导出此任务结果")
    
    # 这里应该实现实际的导出逻辑
    # 在实际应用中，可以使用pandas等库生成Excel文件
    
    logger.info(f"筛查结果导出请求: 任务ID {task_id}, 格式 {format}")
    return {"message": "导出功能开发中", "task_id": task_id, "format": format}

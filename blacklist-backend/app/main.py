"""
黑名单管理系统主应用
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db, test_connection
from app.core.exceptions import BlacklistException
from app.api.v1 import auth, users, blacklist, screening, admin, roles, orders, blacklist_check, groups, group_detection, group_detection_simple

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="黑名单管理系统API",
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加受信任主机中间件
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "47.109.97.153"]
    )

# 创建必要的目录
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(settings.EXPORT_PATH, exist_ok=True)
os.makedirs(settings.LOG_PATH, exist_ok=True)

# 挂载静态文件（如果目录存在）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
if os.path.exists(settings.UPLOAD_PATH):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_PATH), name="uploads")
if os.path.exists(settings.EXPORT_PATH):
    app.mount("/exports", StaticFiles(directory=settings.EXPORT_PATH), name="exports")


@app.exception_handler(BlacklistException)
async def blacklist_exception_handler(request: Request, exc: BlacklistException):
    """黑名单系统异常处理器"""
    logger.error(f"黑名单系统异常: {exc.message}, 详情: {exc.details}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "BlacklistException",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "内部服务器错误",
            "details": str(exc) if settings.DEBUG else "服务器内部错误"
        }
    )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 测试数据库连接（不阻塞启动）
    try:
        if test_connection():
            logger.info("数据库连接成功")
            # 初始化数据库
            init_db()
            logger.info("数据库初始化完成")
        else:
            logger.warning("数据库连接失败，但应用继续启动")
    except Exception as e:
        logger.error(f"数据库操作异常: {e}")
        logger.warning("应用将在没有数据库连接的情况下启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("应用正在关闭...")


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": settings.APP_VERSION
    }


# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["角色管理"])
app.include_router(blacklist.router, prefix="/api/v1/blacklist", tags=["黑名单管理"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["订单管理"])
app.include_router(groups.router, prefix="/api/v1/groups", tags=["分组管理"])
app.include_router(group_detection.router, prefix="/api/v1/group-detection", tags=["分组检测"])
app.include_router(group_detection_simple.router, prefix="/api/v1/group-detection-simple", tags=["分组检测-简化版"])
app.include_router(screening.router, prefix="/api/v1/screening", tags=["订单筛查"])
app.include_router(blacklist_check.router, prefix="/api/v1/blacklist-check", tags=["黑名单检测"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["系统管理"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

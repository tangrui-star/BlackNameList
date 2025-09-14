"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    try:
        # 导入所有模型以确保它们被注册
        from app.models import user, blacklist, order, screening
        logger.info("数据库模型导入成功")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def test_connection():
    """测试数据库连接"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("数据库连接测试成功")
            return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False

"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "黑名单管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # 数据库配置
    DB_HOST: str = "47.109.97.153"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Root@2025!"
    DB_DATABASE: str = "blacklist"
    DB_CHARSET: str = "utf8mb4"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: list = ["xlsx", "xls", "csv"]
    UPLOAD_PATH: str = "./data/uploads"
    EXPORT_PATH: str = "./data/exports"
    
    # 匹配算法配置
    PHONE_WEIGHT: int = 100
    NAME_WEIGHT: int = 80
    KTT_WEIGHT: int = 60
    ADDRESS_WEIGHT: int = 40
    MATCH_THRESHOLD: int = 70
    FUZZY_THRESHOLD: int = 80
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "./logs"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 缓存配置
    CACHE_TIMEOUT: int = 300
    USER_CACHE_TIMEOUT: int = 1800
    BLACKLIST_CACHE_TIMEOUT: int = 3600
    
    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        from urllib.parse import quote_plus
        password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}?charset={self.DB_CHARSET}"
    
    @property
    def redis_url(self) -> str:
        """构建Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

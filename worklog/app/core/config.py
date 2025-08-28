from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import os

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "WorkLog Pro"
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "http://localhost:8000"  # 后端服务地址
    FRONTEND_HOST: str = "http://localhost:5173"  # 前端服务地址
    FRONTEND_URL: str = "http://localhost:5173"  # 前端URL，用于邀请链接
    
    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "lHg03712")
    DB_NAME: str = os.getenv("DB_NAME", "work_log")
    DB_TABLE_PREFIX: str = "wl_"
    
    # 使用SQLite进行本地开发（设置为True启用）
    USE_SQLITE: bool = False
    
    # 远程配置（注释掉）
    # DB_HOST: str = "192.168.24.93"
    # DB_PORT: int = 3306
    # DB_USER: str = "root"
    # DB_PASSWORD: str = "Y2Cpnn8A82imQeX1"
    # DB_NAME: str = "work_log"
    # DB_TABLE_PREFIX: str = "wl_"
    
    # 数据库URL
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.USE_SQLITE:
            return "sqlite:///./worklog.db"
        else:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # 请在生产环境中更改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # 邮件配置
    SMTP_TLS: bool = False  # 使用 SSL 时不需要 TLS
    SMTP_PORT: int = 465    # 163邮箱 SSL 端口
    SMTP_HOST: str = "smtp.163.com"
    SMTP_USER: str = "zkzk-11@163.com"
    SMTP_PASSWORD: str = "XX7KxqCFD633pYEh"  # 163邮箱授权码
    EMAILS_FROM_EMAIL: str = "zkzk-11@163.com"
    EMAILS_FROM_NAME: str = "WorkLog Pro"
    
    # 钉钉配置
    DINGTALK_APP_KEY: Optional[str] = None
    DINGTALK_APP_SECRET: Optional[str] = None
    
    # 提醒配置
    DEFAULT_REMINDER_INTERVAL: int = 30  # 默认提醒间隔（分钟）
    WORK_HOURS_START: str = "09:00"  # 工作时间开始
    WORK_HOURS_END: str = "18:00"    # 工作时间结束
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

settings = Settings() 
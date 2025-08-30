from pydantic_settings import BaseSettings
from typing import Optional
import os

class ProductionSettings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "WorkLog Pro"
    API_V1_STR: str = "/api/v1"
    
    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = int(os.getenv("PORT", "8000"))
    
    # Railway MySQL配置 - 直接使用共享变量名称
    DB_HOST: str = os.getenv("MYSQLHOST", "localhost")
    DB_PORT: int = int(os.getenv("MYSQLPORT", "3306"))
    DB_USER: str = os.getenv("MYSQLUSER", "root")
    DB_PASSWORD: str = os.getenv("MYSQLPASSWORD", "")
    DB_NAME: str = os.getenv("MYSQLDATABASE", "worklog")
    DB_TABLE_PREFIX: str = "wl_"
    
    # 使用SQLite进行本地开发（设置为True启用）
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "false").lower() == "true"
    
    # 数据库URL
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.USE_SQLITE:
            return "sqlite:///./worklog.db"
        else:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # 邮件配置
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "false").lower() == "true"
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.163.com")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "WorkLog Pro")
    
    # 钉钉配置
    DINGTALK_APP_KEY: Optional[str] = os.getenv("DINGTALK_APP_KEY")
    DINGTALK_APP_SECRET: Optional[str] = os.getenv("DINGTALK_APP_SECRET")
    
    # 提醒配置
    DEFAULT_REMINDER_INTERVAL: int = int(os.getenv("DEFAULT_REMINDER_INTERVAL", "30"))
    WORK_HOURS_START: str = os.getenv("WORK_HOURS_START", "09:00")
    WORK_HOURS_END: str = os.getenv("WORK_HOURS_END", "18:00")
    
    class Config:
        case_sensitive = True

production_settings = ProductionSettings()

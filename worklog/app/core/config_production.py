from pydantic_settings import BaseSettings
from typing import Optional
import os

def safe_int(value: str, default: int) -> int:
    """安全地将字符串转换为整数，处理共享变量未解析的情况"""
    if not value or value.startswith('$shared.') or value.startswith('${{'):
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

class ProductionSettings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "WorkLog Pro"
    API_V1_STR: str = "/api/v1"
    
    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = int(os.getenv("PORT", "8000"))
    
    # Railway MySQL配置 - 使用实际配置的MySQL参数
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = safe_int(os.getenv("DB_PORT"), 3306)
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "worklog")
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
    REDIS_PORT: int = safe_int(os.getenv("REDIS_PORT"), 6379)
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = safe_int(os.getenv("REDIS_DB"), 0)
    
    # 邮件配置
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"  # Gmail使用TLS
    SMTP_PORT: int = safe_int(os.getenv("SMTP_PORT"), 587)  # Gmail TLS端口
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")  # Gmail SMTP服务器
    SMTP_USER: str = os.getenv("SMTP_USER", "未配置邮箱用户")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "未配置邮箱密码")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "未配置发件人邮箱")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "WorkLog Pro")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 打印邮件配置信息（隐藏敏感信息）
        print(f"📧 生产环境邮件配置:")
        print(f"  SMTP_HOST: {self.SMTP_HOST}")
        print(f"  SMTP_PORT: {self.SMTP_PORT}")
        print(f"  SMTP_USER: {self.SMTP_USER}")
        print(f"  SMTP_PASSWORD: {'*' * len(self.SMTP_PASSWORD) if self.SMTP_PASSWORD else '未设置'}")
        print(f"  EMAILS_FROM_EMAIL: {self.EMAILS_FROM_EMAIL}")
        print(f"  EMAILS_FROM_NAME: {self.EMAILS_FROM_NAME}")
        print(f"  SMTP_TLS: {self.SMTP_TLS}")
        
        # 检查关键配置
        if not self.SMTP_USER or self.SMTP_USER == "未配置邮箱用户":
            print("⚠️  警告: SMTP_USER 未正确配置")
        if not self.SMTP_PASSWORD or self.SMTP_PASSWORD == "未配置邮箱密码":
            print("⚠️  警告: SMTP_PASSWORD 未正确配置")
        if not self.EMAILS_FROM_EMAIL or self.EMAILS_FROM_EMAIL == "未配置发件人邮箱":
            print("⚠️  警告: EMAILS_FROM_EMAIL 未正确配置")
    
    # 钉钉配置
    DINGTALK_APP_KEY: Optional[str] = os.getenv("DINGTALK_APP_KEY")
    DINGTALK_APP_SECRET: Optional[str] = os.getenv("DINGTALK_APP_SECRET")
    
    # 提醒配置
    DEFAULT_REMINDER_INTERVAL: int = safe_int(os.getenv("DEFAULT_REMINDER_INTERVAL"), 30)
    WORK_HOURS_START: str = os.getenv("WORK_HOURS_START", "09:00")
    WORK_HOURS_END: str = os.getenv("WORK_HOURS_END", "18:00")
    
    class Config:
        case_sensitive = True

production_settings = ProductionSettings()

from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User

# 获取数据库会话
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 获取当前用户（示例，实际项目中请根据你的认证逻辑调整）
def get_current_user() -> User:
    # 这里应根据你的认证逻辑实现
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未认证用户",
    ) 
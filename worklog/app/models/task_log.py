from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class TaskLog(Base):
    """任务操作日志模型"""
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 操作类型
    action_type = Column(String(50), nullable=False)  # status_change, assign, comment, etc.
    
    # 操作详情
    old_value = Column(Text, nullable=True)  # 旧值（JSON格式）
    new_value = Column(Text, nullable=True)  # 新值（JSON格式）
    description = Column(Text, nullable=True)  # 操作描述
    
    # 额外信息
    extra_data = Column(JSON, nullable=True)  # 额外的元数据
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # 关联关系
    task = relationship("Task", back_populates="task_logs")
    user = relationship("User", back_populates="task_logs")

class TaskStatusChange(Base):
    """任务状态变化记录模型"""
    __tablename__ = "task_status_changes"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 状态变化
    old_status = Column(String(20), nullable=False)
    new_status = Column(String(20), nullable=False)
    
    # 变化原因
    reason = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # 关联关系
    task = relationship("Task", back_populates="task_status_changes")
    user = relationship("User", back_populates="task_status_changes") 
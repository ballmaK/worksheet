from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    status = Column(Enum('pending', 'sent', 'completed', 'skipped', name='reminder_status'), default='pending')
    response_time = Column(Integer)  # 响应时间（秒）
    notification_method = Column(String(20), nullable=False)  # system, email, dingtalk
    
    # 关联
    user = relationship("User", back_populates="reminders")
    
    # 提醒历史
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime(timezone=True))
    is_retry = Column(Boolean, default=False)
    
    # 提醒内容
    reminder_type = Column(String(20), default='regular')  # regular, delayed, urgent
    message = Column(String(500))
    
    # 工作日志关联（如果提醒后创建了工作日志）
    work_log_id = Column(Integer, ForeignKey("work_logs.id"))
    work_log = relationship("WorkLog") 
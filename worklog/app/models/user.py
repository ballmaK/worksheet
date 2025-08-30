from sqlalchemy import Boolean, Column, Integer, String, DateTime, Time, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
# from app.models.team_invite import TeamInvite  # 移除，避免循环依赖

# 用户角色常量
USER_ADMIN = "admin"
USER_NORMAL = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # admin 或 user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 提醒设置
    reminder_interval = Column(Integer, default=60)  # 提醒间隔（分钟）
    work_hours_start = Column(Time, default='09:00:00')  # 工作时间开始
    work_hours_end = Column(Time, default='18:00:00')  # 工作时间结束
    reminder_enabled = Column(Boolean, default=True)
    notification_method = Column(String(20), default='email')  # 通知方式：email, sms, both
    last_reminder_at = Column(DateTime(timezone=True))

    # 团队成员关系
    team_memberships = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 团队关系
    teams = relationship(
        "Team",
        secondary="team_members",
        viewonly=True
    )
    
    # 工作日志
    worklogs = relationship("WorkLog", back_populates="user", cascade="all, delete-orphan")
    work_log_comments = relationship("Comment", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    # templates = relationship("WorkLogTemplate", back_populates="user")  # 暂时注释掉
    sent_invites = relationship("TeamInvite", back_populates="inviter", cascade="all, delete-orphan")
    
    # 任务相关关系
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    task_comments = relationship("TaskComment", back_populates="user")
    task_attachments = relationship("TaskAttachment", back_populates="user")
    
    # 任务操作日志
    task_logs = relationship("TaskLog", back_populates="user", cascade="all, delete-orphan")
    task_status_changes = relationship("TaskStatusChange", back_populates="user", cascade="all, delete-orphan")
    
    # 消息相关关系
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    # received_messages关系已移除，因为消息现在使用recipients字段支持多接收人 

    # 工作日志模板关系
    # templates = relationship("WorkLogTemplate", back_populates="user", cascade="all, delete-orphan") 
    


# 移除文件最后的User.templates赋值，改由db/base.py统一赋值 
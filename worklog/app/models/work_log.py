from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, DECIMAL, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class WorkLogType(str, enum.Enum):
    FEATURE = "feature"           # 功能开发
    BUG = "bug"                  # Bug修复
    IMPROVEMENT = "improvement"   # 改进优化
    DOCUMENTATION = "documentation"  # 文档工作
    MEETING = "meeting"          # 会议
    RESEARCH = "research"        # 调研
    OTHER = "other"              # 其他

class WorkLogStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    BLOCKED = "blocked"          # 受阻
    ON_HOLD = "on_hold"          # 暂停

class WorkLog(Base):
    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)  # 可以为空，表示个人工作日志
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # 可以为空，表示非项目工作日志
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 关联的任务
    work_type = Column(Enum(WorkLogType, values_callable=lambda obj: [e.value for e in obj]), default="feature", nullable=False)
    content = Column(Text, nullable=False)
    details = Column(Text)  # 详细工作内容
    date = Column(DateTime, nullable=False, default=func.now())
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Float, nullable=False, default=0.0)
    progress_percentage = Column(Float, default=0.0)  # 任务完成度
    work_status = Column(Enum(WorkLogStatus, values_callable=lambda obj: [e.value for e in obj]), default="in_progress")
    issues_encountered = Column(Text)  # 遇到的问题
    solutions_applied = Column(Text)   # 解决方案
    blockers = Column(Text)           # 阻碍因素
    remark = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联
    user = relationship("User", back_populates="worklogs")
    team = relationship("Team", back_populates="worklogs")
    project = relationship("Project", back_populates="worklogs")
    task = relationship("Task", back_populates="work_logs")
    comments = relationship("Comment", back_populates="work_log", cascade="all, delete-orphan")
    
    # 标签（JSON格式存储）
    tags = Column(String(255))  # 存储格式: "tag1,tag2,tag3"
    
    # 附件（JSON格式存储）
    attachments = Column(Text)  # 存储格式: [{"name": "file1.pdf", "url": "http://..."}]

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    work_log_id = Column(Integer, ForeignKey("work_logs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    work_log = relationship("WorkLog", back_populates="comments")
    user = relationship("User", back_populates="work_log_comments") 
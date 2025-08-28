from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, DECIMAL, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"           # 待分派
    ASSIGNED = "assigned"         # 已分派
    IN_PROGRESS = "in_progress"   # 进行中
    REVIEW = "review"             # 待审核
    COMPLETED = "completed"       # 已完成
    CANCELLED = "cancelled"       # 已取消

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskType(str, enum.Enum):
    FEATURE = "feature"           # 功能开发
    BUG = "bug"                  # Bug修复
    IMPROVEMENT = "improvement"   # 改进优化
    DOCUMENTATION = "documentation"  # 文档工作
    MEETING = "meeting"          # 会议
    RESEARCH = "research"        # 调研
    OTHER = "other"              # 其他

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    task_level = Column(String(20), default="project")  # project, subtask
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
    
    # 分派相关
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))  # 负责人
    
    # 任务属性
    status = Column(Enum(TaskStatus, values_callable=lambda obj: [e.value for e in obj]), default="pending", nullable=False)
    priority = Column(Enum(TaskPriority, values_callable=lambda obj: [e.value for e in obj]), default="medium", nullable=False)
    task_type = Column(Enum(TaskType, values_callable=lambda obj: [e.value for e in obj]), default="feature", nullable=False)
    
    # 时间相关
    due_date = Column(DateTime)
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    started_at = Column(DateTime)  # 开始工作时间
    completed_at = Column(DateTime)  # 完成时间
    
    # 其他
    tags = Column(String(200))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    team = relationship("Team", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    parent_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task")
    work_logs = relationship("WorkLog", back_populates="task")
    task_logs = relationship("TaskLog", back_populates="task")
    task_status_changes = relationship("TaskStatusChange", back_populates="task")
    comments = relationship("TaskComment", back_populates="task")
    
    # 任务依赖关系
    dependencies = relationship("TaskDependency", foreign_keys="TaskDependency.dependent_task_id", back_populates="dependent_task")
    dependents = relationship("TaskDependency", foreign_keys="TaskDependency.prerequisite_task_id", back_populates="prerequisite_task")
    
    # 任务附件
    attachments = relationship("TaskAttachment", back_populates="task")


class TaskDependency(Base):
    """任务依赖关系模型"""
    __tablename__ = "task_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    prerequisite_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    dependent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    prerequisite_task = relationship("Task", foreign_keys=[prerequisite_task_id], back_populates="dependents")
    dependent_task = relationship("Task", foreign_keys=[dependent_task_id], back_populates="dependencies")


class TaskComment(Base):
    """任务评论模型"""
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")


class TaskAttachment(Base):
    """任务附件模型"""
    __tablename__ = "task_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    task = relationship("Task", back_populates="attachments")
    user = relationship("User", back_populates="task_attachments") 
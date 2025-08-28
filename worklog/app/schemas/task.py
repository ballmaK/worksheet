from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# 用户信息模型
class UserInfo(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# 枚举定义
class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskType(str, Enum):
    FEATURE = "feature"           # 功能开发
    BUG = "bug"                  # Bug修复
    IMPROVEMENT = "improvement"   # 改进优化
    DOCUMENTATION = "documentation"  # 文档工作
    MEETING = "meeting"          # 会议
    RESEARCH = "research"        # 调研
    OTHER = "other"              # 其他

# 基础模型
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    team_id: int = Field(..., description="所属团队ID")
    project_id: Optional[int] = Field(None, description="关联项目ID")
    assignee_id: Optional[int] = Field(None, description="负责人ID")
    status: TaskStatus = Field(TaskStatus.PENDING, description="任务状态")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="任务优先级")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    estimated_hours: Optional[float] = Field(None, ge=0, le=1000, description="预估工时")
    task_type: TaskType = Field(TaskType.OTHER, description="任务类型")
    tags: Optional[str] = Field(None, description="标签，JSON格式")

# 快速创建模型 - 只需要标题
class TaskQuickCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    team_id: Optional[int] = Field(None, description="所属团队ID，如果不提供则使用用户默认团队")
    priority: Optional[TaskPriority] = Field(TaskPriority.MEDIUM, description="任务优先级")

class TaskCommentBase(BaseModel):
    content: str = Field(..., min_length=1, description="评论内容")

# 创建模型
class TaskCreate(TaskBase):
    pass

# 更新模型
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    team_id: Optional[int] = None
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0, le=1000)
    task_type: Optional[TaskType] = None
    tags: Optional[str] = None
    actual_hours: Optional[float] = Field(None, ge=0, le=1000)

# 项目信息模型
class ProjectInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

# 响应模型
class TaskCommentResponse(TaskCommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: UserInfo

    class Config:
        from_attributes = True

class TaskResponse(TaskBase):
    id: int
    creator_id: int
    actual_hours: Optional[float] = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    
    # 关联信息
    creator: UserInfo
    assignee: Optional[UserInfo] = None
    project: Optional[ProjectInfo] = None
    comments: List[TaskCommentResponse] = []
    
    # 统计信息
    comment_count: int = 0

    class Config:
        from_attributes = True

# 列表响应模型
class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 任务统计模型
class TaskStatistics(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    review: int
    cancelled: int
    overdue: int
    total_estimated_hours: float
    completed_hours: float
    completion_rate: float

# 任务筛选模型
class TaskFilter(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    task_type: Optional[TaskType] = None
    assignee_id: Optional[int] = None
    creator_id: Optional[int] = None
    project_id: Optional[int] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    tags: Optional[str] = None
    search: Optional[str] = None 
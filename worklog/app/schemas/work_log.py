from typing import Optional, List, Any
from pydantic import BaseModel, constr
from datetime import datetime
from enum import Enum

class WorkTypeEnum(str, Enum):
    FEATURE = "feature"           # 功能开发
    BUG = "bug"                  # Bug修复
    IMPROVEMENT = "improvement"   # 改进优化
    DOCUMENTATION = "documentation"  # 文档工作
    MEETING = "meeting"          # 会议
    RESEARCH = "research"        # 调研
    OTHER = "other"              # 其他

# 工作日志基础模型
class WorkLogBase(BaseModel):
    title: Optional[str] = None
    work_type: WorkTypeEnum
    content: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    remark: Optional[str] = None
    tags: Optional[str] = None
    attachments: Optional[str] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None  # 关联的任务ID
    team_id: Optional[int] = None
    progress_percentage: Optional[float] = None  # 任务完成度
    issues_encountered: Optional[str] = None  # 遇到的问题
    solutions_applied: Optional[str] = None   # 解决方案
    blockers: Optional[str] = None           # 阻碍因素

# 创建工作日志
class WorkLogCreate(WorkLogBase):
    pass

# 更新工作日志
class WorkLogUpdate(BaseModel):
    title: Optional[str] = None
    work_type: Optional[WorkTypeEnum] = None
    content: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    remark: Optional[str] = None
    tags: Optional[str] = None
    attachments: Optional[str] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    team_id: Optional[int] = None
    progress_percentage: Optional[float] = None
    issues_encountered: Optional[str] = None
    solutions_applied: Optional[str] = None
    blockers: Optional[str] = None

# DB模型
class WorkLogInDB(WorkLogBase):
    id: int
    user_id: int
    team_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 工作日志响应
class WorkLogResponse(WorkLogBase):
    id: int
    user_id: int
    user_name: Optional[str] = None
    team_name: Optional[str] = None
    project_name: Optional[str] = None
    task_title: Optional[str] = None  # 关联的任务标题
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 评论基础模型
class CommentBase(BaseModel):
    content: constr(min_length=1, max_length=1000)

# 创建评论
class CommentCreate(CommentBase):
    pass

# 评论响应
class CommentResponse(CommentBase):
    id: int
    work_log_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int 
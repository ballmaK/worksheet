from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.enums import ProjectStatus

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="项目名称")
    description: Optional[str] = Field(None, max_length=200, description="项目描述")
    status: ProjectStatus = Field(ProjectStatus.NOT_STARTED, description="项目状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    progress: int = Field(0, ge=0, le=100, description="项目进度(0-100)")

class ProjectCreate(ProjectBase):
    team_id: int = Field(..., description="所属团队ID")

class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="项目名称")
    team_id: Optional[int] = Field(None, description="所属团队ID")

class ProjectInDB(ProjectBase):
    id: int
    team_id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(ProjectInDB):
    team_name: Optional[str] = None
    creator_name: Optional[str] = None
    task_count: Optional[int] = 0
    member_count: Optional[int] = 0
    worklog_count: Optional[int] = 0

    class Config:
        from_attributes = True 
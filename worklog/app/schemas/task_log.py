from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TaskLogBase(BaseModel):
    action_type: str = Field(..., description="操作类型")
    description: Optional[str] = Field(None, description="操作描述")
    old_value: Optional[str] = Field(None, description="旧值")
    new_value: Optional[str] = Field(None, description="新值")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外元数据")

class TaskLogCreate(TaskLogBase):
    task_id: int = Field(..., description="任务ID")

class TaskLogResponse(TaskLogBase):
    id: int
    task_id: int
    user_id: int
    user_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TaskStatusChangeBase(BaseModel):
    old_status: str = Field(..., description="旧状态")
    new_status: str = Field(..., description="新状态")
    reason: Optional[str] = Field(None, description="变化原因")
    comment: Optional[str] = Field(None, description="备注")

class TaskStatusChangeCreate(TaskStatusChangeBase):
    task_id: int = Field(..., description="任务ID")

class TaskStatusChangeResponse(TaskStatusChangeBase):
    id: int
    task_id: int
    user_id: int
    user_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TaskActivityLog(BaseModel):
    """任务活动日志（包含所有类型的操作）"""
    id: int
    task_id: int
    user_id: int
    user_name: Optional[str] = None
    action_type: str
    description: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True 
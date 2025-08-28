from typing import Optional
from pydantic import BaseModel, constr
from datetime import datetime

# 提醒基础模型
class ReminderBase(BaseModel):
    scheduled_at: datetime
    reminder_type: str = "regular"  # regular, delayed, urgent
    message: Optional[str] = None

# 创建提醒
class ReminderCreate(ReminderBase):
    pass

# 更新提醒
class ReminderUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    reminder_type: Optional[str] = None
    message: Optional[str] = None

# 提醒响应
class ReminderResponse(ReminderBase):
    id: int
    user_id: int
    status: str
    sent_at: Optional[datetime] = None
    response_time: Optional[int] = None
    retry_count: int
    last_retry_at: Optional[datetime] = None
    is_retry: bool
    work_log_id: Optional[int] = None

    class Config:
        from_attributes = True 
from typing import Optional
from pydantic import BaseModel, constr
from datetime import datetime

class TemplateBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    work_type: str
    content_template: str
    duration: Optional[float] = None
    tags: Optional[str] = None
    is_default: Optional[bool] = False

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    work_type: Optional[str] = None
    content_template: Optional[str] = None
    duration: Optional[float] = None
    tags: Optional[str] = None
    is_default: Optional[bool] = None

class TemplateResponse(TemplateBase):
    id: int
    user_id: int
    use_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
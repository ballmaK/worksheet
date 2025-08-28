from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

# Message schemas
class MessageBase(BaseModel):
    title: str
    content: str
    message_type: str
    priority: str = "normal"
    message_data: Optional[Dict[str, Any]] = {}

class MessageCreate(MessageBase):
    recipients: list[int]
    sender_id: Optional[int] = None

class MessageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_read: Optional[bool] = None
    is_deleted: Optional[bool] = None

class MessageResponse(MessageBase):
    id: int
    sender_id: Optional[int]
    recipients: list[int]
    is_read: bool
    is_deleted: bool
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    sent_via_email: bool
    sent_via_websocket: bool
    sent_via_desktop: bool
    
    class Config:
        from_attributes = True

# MessageTemplate schemas
class MessageTemplateBase(BaseModel):
    name: str
    title_template: str
    content_template: str
    message_type: str
    priority: str = "normal"
    variables: Optional[Dict[str, Any]] = {}
    send_via_email: bool = False
    send_via_websocket: bool = True
    send_via_desktop: bool = True
    is_active: bool = True

class MessageTemplateCreate(MessageTemplateBase):
    pass

class MessageTemplateUpdate(BaseModel):
    name: Optional[str] = None
    title_template: Optional[str] = None
    content_template: Optional[str] = None
    message_type: Optional[str] = None
    priority: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    send_via_email: Optional[bool] = None
    send_via_websocket: Optional[bool] = None
    send_via_desktop: Optional[bool] = None
    is_active: Optional[bool] = None

class MessageTemplateResponse(MessageTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Message statistics
class MessageStats(BaseModel):
    total_messages: int
    unread_messages: int
    urgent_messages: int
    important_messages: int
    messages_by_type: Dict[str, int]
    
    class Config:
        from_attributes = True 
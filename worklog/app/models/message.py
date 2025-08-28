from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    
    # 消息基本信息
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum('task', 'team', 'worklog', 'system', 'user', 'project', name='message_type'), nullable=False)
    priority = Column(Enum('urgent', 'important', 'normal', 'low', name='message_priority'), default='normal')
    
    # 发送者和接收者
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 系统消息可以为空
    recipients = Column(JSON, nullable=False)
    
    # 消息状态
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 消息传递状态
    sent_via_email = Column(Boolean, default=False)
    sent_via_websocket = Column(Boolean, default=False)
    sent_via_desktop = Column(Boolean, default=False)
    
    # 关联数据（JSON格式存储额外信息）
    message_data = Column(JSON, default={})
    
    # 关联
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")

class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # 模板信息
    name = Column(String(100), nullable=False, unique=True)
    title_template = Column(String(200), nullable=False)
    content_template = Column(Text, nullable=False)
    message_type = Column(Enum('task', 'team', 'worklog', 'system', 'user', 'project', name='message_type'), nullable=False)
    priority = Column(Enum('urgent', 'important', 'normal', 'low', name='message_priority'), default='normal')
    
    # 模板变量
    variables = Column(JSON, default={})  # 模板中可用的变量列表
    
    # 发送设置
    send_via_email = Column(Boolean, default=False)
    send_via_websocket = Column(Boolean, default=True)
    send_via_desktop = Column(Boolean, default=True)
    
    # 状态
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
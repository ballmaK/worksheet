from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta

from app.models.message import Message, MessageTemplate
from app.schemas.message import MessageCreate, MessageUpdate, MessageTemplateCreate, MessageTemplateUpdate

class MessageCRUD:
    def create(self, db: Session, *, obj_in: MessageCreate) -> Message:
        """
        创建消息，支持多接收人
        """
        db_obj = Message(
            title=obj_in.title,
            content=obj_in.content,
            message_type=obj_in.message_type,
            priority=obj_in.priority,
            sender_id=obj_in.sender_id,
            recipients=obj_in.recipients,
            message_data=obj_in.message_data or {}
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, message_id: int) -> Optional[Message]:
        """获取单个消息"""
        return db.query(Message).filter(Message.id == message_id).first()

    def get_by_receiver(
        self, 
        db: Session, 
        receiver_id: int, 
        skip: int = 0, 
        limit: int = 100,
        unread_only: bool = False,
        message_type: Optional[str] = None
    ) -> List[Message]:
        """
        获取用户接收的消息
        """
        query = db.query(Message).filter(
            Message.recipients.contains([receiver_id]),
            Message.is_deleted == False
        )
        if unread_only:
            query = query.filter(Message.is_read == False)
        if message_type:
            query = query.filter(Message.message_type == message_type)
        return query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

    def mark_as_read(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        message = db.query(Message).filter(
            Message.id == message_id,
            Message.recipients.contains([user_id])
        ).first()
        if message:
            message.is_read = True
            message.read_at = datetime.utcnow()
            db.add(message)
            db.commit()
            db.refresh(message)
        return message

    def mark_all_as_read(self, db: Session, user_id: int, message_type: Optional[str] = None) -> int:
        query = db.query(Message).filter(
            Message.recipients.contains([user_id]),
            Message.is_read == False,
            Message.is_deleted == False
        )
        if message_type:
            query = query.filter(Message.message_type == message_type)
        count = query.count()
        query.update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        db.commit()
        return count

    def delete_message(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        message = db.query(Message).filter(
            Message.id == message_id,
            Message.recipients.contains([user_id])
        ).first()
        if message:
            message.is_deleted = True
            db.add(message)
            db.commit()
            db.refresh(message)
        return message

    def get_unread_count(self, db: Session, user_id: int) -> int:
        return db.query(Message).filter(
            Message.recipients.contains([user_id]),
            Message.is_read == False,
            Message.is_deleted == False
        ).count()

    def get_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        total_messages = db.query(Message).filter(
            Message.recipients.contains([user_id]),
            Message.is_deleted == False
        ).count()
        unread_messages = db.query(Message).filter(
            Message.recipients.contains([user_id]),
            Message.is_read == False,
            Message.is_deleted == False
        ).count()
        urgent_messages = db.query(Message).filter(
            Message.recipients.contains([user_id]),
            Message.priority == "urgent",
            Message.is_deleted == False
        ).count()
        important_messages = db.query(Message).filter(
            Message.recipients.contains([user_id]),
            Message.priority == "important",
            Message.is_deleted == False
        ).count()
        messages_by_type = db.query(
            Message.message_type,
            func.count(Message.id)
        ).filter(
            Message.recipients.contains([user_id]),
            Message.is_deleted == False
        ).group_by(Message.message_type).all()
        return {
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "urgent_messages": urgent_messages,
            "important_messages": important_messages,
            "messages_by_type": dict(messages_by_type)
        }

class MessageTemplateCRUD:
    def create(self, db: Session, *, obj_in: MessageTemplateCreate) -> MessageTemplate:
        """创建消息模板"""
        db_obj = MessageTemplate(
            name=obj_in.name,
            title_template=obj_in.title_template,
            content_template=obj_in.content_template,
            message_type=obj_in.message_type,
            priority=obj_in.priority,
            variables=obj_in.variables or {},
            send_via_email=obj_in.send_via_email,
            send_via_websocket=obj_in.send_via_websocket,
            send_via_desktop=obj_in.send_via_desktop,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, template_id: int) -> Optional[MessageTemplate]:
        """获取单个模板"""
        return db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[MessageTemplate]:
        """根据名称获取模板"""
        return db.query(MessageTemplate).filter(
            and_(
                MessageTemplate.name == name,
                MessageTemplate.is_active == True
            )
        ).first()

    def get_active_templates(self, db: Session, message_type: Optional[str] = None) -> List[MessageTemplate]:
        """获取活跃模板"""
        query = db.query(MessageTemplate).filter(MessageTemplate.is_active == True)
        
        if message_type:
            query = query.filter(MessageTemplate.message_type == message_type)
        
        return query.all()

    def update(self, db: Session, *, db_obj: MessageTemplate, obj_in: MessageTemplateUpdate) -> MessageTemplate:
        """更新模板"""
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, template_id: int) -> MessageTemplate:
        """删除模板"""
        obj = db.query(MessageTemplate).get(template_id)
        db.delete(obj)
        db.commit()
        return obj

message_crud = MessageCRUD()
message_template_crud = MessageTemplateCRUD() 
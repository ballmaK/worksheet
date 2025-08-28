from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.message import (
    MessageCreate, 
    MessageUpdate, 
    MessageResponse, 
    MessageTemplateCreate,
    MessageTemplateUpdate,
    MessageTemplateResponse,
    MessageStats
)
from app.crud.message import message_crud, message_template_crud
from app.core.ws_manager import ws_manager
from app.core.message_service import message_push_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 消息相关端点
@router.get("/", response_model=List[MessageResponse])
def read_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = Query(False, description="只获取未读消息"),
    message_type: Optional[str] = Query(None, description="消息类型过滤")
) -> Any:
    """
    获取用户消息列表
    """
    messages = message_crud.get_by_receiver(
        db=db,
        receiver_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        message_type=message_type
    )
    return messages

@router.get("/stats", response_model=MessageStats)
def get_message_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取用户消息统计
    """
    stats = message_crud.get_stats(db=db, user_id=current_user.id)
    return stats

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取未读消息数量
    """
    count = message_crud.get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}

@router.get("/{message_id}", response_model=MessageResponse)
def read_message(
    *,
    db: Session = Depends(get_db),
    message_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定消息
    """
    message = message_crud.get(db=db, message_id=message_id)
    if not message or current_user.id not in message.recipients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    return message

@router.put("/{message_id}/read", response_model=MessageResponse)
def mark_message_as_read(
    *,
    db: Session = Depends(get_db),
    message_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    标记消息为已读
    """
    message = message_crud.mark_as_read(
        db=db, 
        message_id=message_id, 
        user_id=current_user.id
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    return message

@router.put("/mark-all-read")
def mark_all_messages_as_read(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    message_type: Optional[str] = Query(None, description="消息类型")
) -> Any:
    """
    标记所有消息为已读
    """
    count = message_crud.mark_all_as_read(
        db=db, 
        user_id=current_user.id,
        message_type=message_type
    )
    return {"marked_count": count}

@router.delete("/{message_id}", response_model=MessageResponse)
def delete_message(
    *,
    db: Session = Depends(get_db),
    message_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除消息
    """
    message = message_crud.delete_message(
        db=db, 
        message_id=message_id, 
        user_id=current_user.id
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    return message

# 消息模板相关端点（管理员功能）
@router.post("/templates/", response_model=MessageTemplateResponse)
def create_message_template(
    *,
    db: Session = Depends(get_db),
    template_in: MessageTemplateCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建消息模板（管理员功能）
    """
    # TODO: 检查用户权限
    template = message_template_crud.create(db=db, obj_in=template_in)
    return template

@router.get("/templates/", response_model=List[MessageTemplateResponse])
def read_message_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    message_type: Optional[str] = Query(None, description="消息类型过滤")
) -> Any:
    """
    获取消息模板列表
    """
    if message_type:
        templates = message_template_crud.get_active_templates(
            db=db, 
            message_type=message_type
        )
    else:
        templates = message_template_crud.get_active_templates(db=db)
    return templates

@router.get("/templates/{template_id}", response_model=MessageTemplateResponse)
def read_message_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定消息模板
    """
    template = message_template_crud.get(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    return template

@router.put("/templates/{template_id}", response_model=MessageTemplateResponse)
def update_message_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    template_in: MessageTemplateUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新消息模板
    """
    template = message_template_crud.get(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    template = message_template_crud.update(
        db=db, 
        db_obj=template, 
        obj_in=template_in
    )
    return template

@router.delete("/templates/{template_id}", response_model=MessageTemplateResponse)
def delete_message_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除消息模板（管理员功能）
    """
    # TODO: 检查用户权限
    template = message_template_crud.delete_template(
        db=db, 
        template_id=template_id
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    return template

# WebSocket连接状态和测试功能
@router.get("/connection-status")
def get_connection_status(
    *,
    current_user: User = Depends(get_current_user)
) -> dict:
    """获取用户WebSocket连接状态"""
    is_connected = ws_manager.is_user_connected(current_user.id)
    connected_users = ws_manager.get_connected_users()
    
    return {
        "is_connected": is_connected,
        "connected_users_count": len(connected_users),
        "connected_users": connected_users
    }

@router.post("/test-notification")
def send_test_notification(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """发送测试通知（仅用于开发测试）"""
    try:
        # 使用后台任务发送通知，避免阻塞
        import threading
        
        def send_test_notification():
            try:
                import asyncio
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    message_push_service.send_system_notification(
                        db=db,
                        title="测试通知",
                        content="这是一条测试通知消息",
                        recipients=[current_user.id],
                        notification_type="test"
                    )
                )
                loop.close()
            except Exception as e:
                logger.error(f"后台发送测试通知失败: {e}")
        
        # 在后台线程中执行
        thread = threading.Thread(target=send_test_notification)
        thread.daemon = True
        thread.start()
        
        return {"message": "测试通知已启动后台发送"}
    except Exception as e:
        logger.error(f"发送测试通知失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送测试通知失败: {str(e)}"
        ) 
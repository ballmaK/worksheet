from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate, ReminderResponse

router = APIRouter()

@router.post("/", response_model=ReminderResponse)
def create_reminder(
    *,
    db: Session = Depends(get_db),
    reminder_in: ReminderCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建提醒
    """
    reminder = Reminder(
        user_id=current_user.id,
        scheduled_at=reminder_in.scheduled_at,
        reminder_type=reminder_in.reminder_type,
        message=reminder_in.message
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.get("/", response_model=List[ReminderResponse])
def read_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取提醒列表
    """
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return reminders

@router.get("/{reminder_id}", response_model=ReminderResponse)
def read_reminder(
    *,
    db: Session = Depends(get_db),
    reminder_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定提醒
    """
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在"
        )
    return reminder

@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    *,
    db: Session = Depends(get_db),
    reminder_id: int,
    reminder_in: ReminderUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新提醒
    """
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在"
        )
    
    for field, value in reminder_in.dict(exclude_unset=True).items():
        setattr(reminder, field, value)
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.delete("/{reminder_id}", response_model=ReminderResponse)
def delete_reminder(
    *,
    db: Session = Depends(get_db),
    reminder_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除提醒
    """
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在"
        )
    
    db.delete(reminder)
    db.commit()
    return reminder 
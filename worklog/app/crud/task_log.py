from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.task_log import TaskLog, TaskStatusChange
from app.models.task import Task
from app.models.user import User
from app.schemas.task_log import TaskLogCreate, TaskStatusChangeCreate
import json

def create_task_log(
    db: Session, 
    task_id: int, 
    user_id: int, 
    action_type: str, 
    description: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> TaskLog:
    """创建任务操作日志"""
    task_log = TaskLog(
        task_id=task_id,
        user_id=user_id,
        action_type=action_type,
        description=description,
        old_value=json.dumps(old_value) if old_value is not None else None,
        new_value=json.dumps(new_value) if new_value is not None else None,
        extra_data=extra_data
    )
    db.add(task_log)
    db.commit()
    db.refresh(task_log)
    return task_log

def create_status_change_log(
    db: Session,
    task_id: int,
    user_id: int,
    old_status: str,
    new_status: str,
    reason: Optional[str] = None,
    comment: Optional[str] = None
) -> TaskStatusChange:
    """创建任务状态变化日志"""
    status_change = TaskStatusChange(
        task_id=task_id,
        user_id=user_id,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
        comment=comment
    )
    db.add(status_change)
    db.commit()
    db.refresh(status_change)
    return status_change

def get_task_logs(
    db: Session,
    task_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """获取任务的操作日志"""
    logs = db.query(TaskLog).options(
        joinedload(TaskLog.user)
    ).filter(
        TaskLog.task_id == task_id
    ).order_by(
        TaskLog.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    result = []
    for log in logs:
        log_dict = {
            'id': log.id,
            'task_id': log.task_id,
            'user_id': log.user_id,
            'user_name': log.user.username if log.user else None,
            'action_type': log.action_type,
            'description': log.description,
            'old_value': json.loads(log.old_value) if log.old_value else None,
            'new_value': json.loads(log.new_value) if log.new_value else None,
            'extra_data': log.extra_data,
            'created_at': log.created_at
        }
        result.append(log_dict)
    
    return result

def get_task_status_changes(
    db: Session,
    task_id: int,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """获取任务的状态变化历史"""
    changes = db.query(TaskStatusChange).options(
        joinedload(TaskStatusChange.user)
    ).filter(
        TaskStatusChange.task_id == task_id
    ).order_by(
        TaskStatusChange.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    result = []
    for change in changes:
        change_dict = {
            'id': change.id,
            'task_id': change.task_id,
            'user_id': change.user_id,
            'user_name': change.user.username if change.user else None,
            'old_status': change.old_status,
            'new_status': change.new_status,
            'reason': change.reason,
            'comment': change.comment,
            'created_at': change.created_at
        }
        result.append(change_dict)
    
    return result

def get_task_activity_logs(
    db: Session,
    task_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """获取任务的完整活动日志（包括所有操作）"""
    # 获取操作日志
    task_logs = get_task_logs(db, task_id, limit, offset)
    
    # 获取状态变化日志
    status_changes = get_task_status_changes(db, task_id, limit, offset)
    
    # 合并并排序
    all_logs = []
    
    for log in task_logs:
        all_logs.append({
            **log,
            'log_type': 'operation'
        })
    
    for change in status_changes:
        all_logs.append({
            **change,
            'log_type': 'status_change',
            'action_type': 'status_change'
        })
    
    # 按时间排序
    all_logs.sort(key=lambda x: x['created_at'], reverse=True)
    
    return all_logs[:limit]

def log_task_creation(
    db: Session,
    task: Task,
    user_id: int
) -> TaskLog:
    """记录任务创建日志"""
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="task_created",
        description=f"创建了任务「{task.title}」",
        new_value={
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'assignee_id': task.assignee_id
        }
    )

def log_task_status_change(
    db: Session,
    task: Task,
    user_id: int,
    old_status: str,
    new_status: str,
    reason: Optional[str] = None,
    comment: Optional[str] = None
) -> tuple[TaskLog, TaskStatusChange]:
    """记录任务状态变化"""
    # 创建状态变化记录
    status_change = create_status_change_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
        comment=comment
    )
    
    # 创建操作日志
    task_log = create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="status_change",
        description=f"将任务状态从「{old_status}」更改为「{new_status}」",
        old_value={'status': old_status},
        new_value={'status': new_status},
        extra_data={
            'reason': reason,
            'comment': comment
        }
    )
    
    return task_log, status_change

def log_task_assignment(
    db: Session,
    task: Task,
    user_id: int,
    old_assignee_id: Optional[int],
    new_assignee_id: Optional[int]
) -> TaskLog:
    """记录任务分配变化"""
    old_assignee_name = None
    new_assignee_name = None
    
    if old_assignee_id:
        old_user = db.query(User).filter(User.id == old_assignee_id).first()
        old_assignee_name = old_user.username if old_user else None
    
    if new_assignee_id:
        new_user = db.query(User).filter(User.id == new_assignee_id).first()
        new_assignee_name = new_user.username if new_user else None
    
    description = f"将任务分配给「{new_assignee_name}」" if new_assignee_name else "取消了任务分配"
    
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="assignment_change",
        description=description,
        old_value={'assignee_id': old_assignee_id, 'assignee_name': old_assignee_name},
        new_value={'assignee_id': new_assignee_id, 'assignee_name': new_assignee_name}
    )

def log_task_update(
    db: Session,
    task: Task,
    user_id: int,
    changes: Dict[str, Any],
    description: Optional[str] = None
) -> TaskLog:
    """记录任务更新日志"""
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="task_updated",
        description=description or "更新了任务信息",
        old_value={},
        new_value=changes
    )

def log_task_claim(
    db: Session,
    task: Task,
    user_id: int
) -> TaskLog:
    """记录任务认领日志"""
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="task_claimed",
        description=f"认领了任务「{task.title}」",
        new_value={
            'assignee_id': user_id,
            'status': task.status
        }
    )

def log_task_start(
    db: Session,
    task: Task,
    user_id: int
) -> TaskLog:
    """记录任务开始工作日志"""
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="task_started",
        description=f"开始工作「{task.title}」",
        new_value={
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'status': task.status
        }
    )

def log_task_submit_review(
    db: Session,
    task: Task,
    user_id: int
) -> TaskLog:
    """记录任务提交审核日志"""
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="task_submitted",
        description=f"提交任务「{task.title}」进行审核",
        new_value={
            'status': task.status
        }
    )

def log_task_approve(
    db: Session,
    task: Task,
    user_id: int
) -> TaskLog:
    """记录任务审核通过日志"""
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="task_approved",
        description=f"审核通过任务「{task.title}」",
        new_value={
            'status': task.status,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        }
    )

def log_task_reject(
    db: Session,
    task: Task,
    user_id: int,
    reason: str
) -> TaskLog:
    """记录任务审核拒绝日志"""
    return create_task_log(
        db=db,
        task_id=task.id,
        user_id=user_id,
        action_type="task_rejected",
        description=f"审核拒绝任务「{task.title}」",
        old_value={'status': 'review'},
        new_value={
            'status': task.status,
            'reject_reason': reason
        },
        extra_data={'reject_reason': reason}
    ) 
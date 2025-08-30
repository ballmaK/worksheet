from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import logging

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.work_log import WorkLog
from app.models.task_log import TaskLog
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.schemas.project import ProjectResponse
from app.core.message_service import message_push_service

logger = logging.getLogger(__name__)

router = APIRouter()

# 项目概览接口
@router.get("/{project_id}/overview")
def get_project_overview(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int
) -> Any:
    """
    获取项目概览信息
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否有权限访问该项目
    team_member = db.query(TeamMember).filter(
        TeamMember.team_id == project.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问该项目"
        )
    
    # 统计任务信息
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    in_progress_tasks = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
    pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])
    
    # 统计工时信息
    total_estimated_hours = sum(t.estimated_hours or 0 for t in tasks)
    total_actual_hours = sum(t.actual_hours or 0 for t in tasks)
    
    # 获取最近的工作日志
    recent_worklogs = db.query(WorkLog).filter(
        WorkLog.project_id == project_id
    ).order_by(desc(WorkLog.created_at)).limit(5).all()
    
    # 获取项目成员
    team_members = db.query(TeamMember).filter(
        TeamMember.team_id == project.team_id
    ).all()
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status.value if project.status else "unknown",
            "progress": project.progress,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "created_at": project.created_at
        },
        "statistics": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours
        },
        "recent_activities": [
            {
                "id": wl.id,
                "type": "worklog",
                "title": f"{wl.user.username} 提交了工作日志",
                "content": wl.content[:100] + "..." if len(wl.content) > 100 else wl.content,
                "created_at": wl.created_at,
                "user": {
                    "id": wl.user.id,
                    "username": wl.user.username
                }
            }
            for wl in recent_worklogs
        ],
        "team_members": [
            {
                "id": tm.user.id,
                "username": tm.user.username,
                "role": tm.role,
                "joined_at": tm.created_at
            }
            for tm in team_members
        ]
    }

# 项目任务列表接口
@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
def get_project_tasks(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    keyword: Optional[str] = None
) -> Any:
    """
    获取项目任务列表
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否有权限访问该项目
    team_member = db.query(TeamMember).filter(
        TeamMember.team_id == project.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问该项目"
        )
    
    # 构建查询
    query = db.query(Task).filter(Task.project_id == project_id)
    
    # 应用过滤条件
    if status:
        query = query.filter(Task.status == status)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    
    if keyword:
        query = query.filter(
            or_(
                Task.title.contains(keyword),
                Task.description.contains(keyword)
            )
        )
    
    # 分页查询
    tasks = query.order_by(desc(Task.created_at)).offset(skip).limit(limit).all()
    
    return tasks

# 创建项目任务接口
@router.post("/{project_id}/tasks", response_model=TaskResponse)
def create_project_task(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    task_in: TaskCreate
) -> Any:
    """
    创建项目任务
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否有权限在该项目中创建任务
    team_member = db.query(TeamMember).filter(
        TeamMember.team_id == project.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限在该项目中创建任务"
        )
    
    # 创建任务
    task_data = task_in.dict()
    task_data["project_id"] = project_id
    task_data["team_id"] = project.team_id
    task_data["creator_id"] = current_user.id
    
    task = Task(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 发送消息通知
    if task.assignee_id and task.assignee_id != current_user.id:
        message_push_service.send_task_assignment_notification(
            task_id=task.id,
            assignee_id=task.assignee_id,
            assigner_id=current_user.id
        )
    
    return task

# 项目活动流接口（基于现有数据聚合）
@router.get("/{project_id}/activities")
def get_project_activities(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    skip: int = 0,
    limit: int = 50
) -> Any:
    """
    获取项目活动流（基于任务日志、工作日志等聚合）
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否有权限访问该项目
    team_member = db.query(TeamMember).filter(
        TeamMember.team_id == project.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问该项目"
        )
    
    activities = []
    
    # 获取任务日志
    task_logs = db.query(TaskLog).join(Task).filter(
        Task.project_id == project_id
    ).order_by(desc(TaskLog.created_at)).offset(skip).limit(limit).all()
    
    for log in task_logs:
        activities.append({
            "id": f"task_log_{log.id}",
            "type": "task_log",
            "title": f"任务状态更新: {log.action_type}",
            "content": log.description or f"任务 {log.task.title} 状态更新",
            "created_at": log.created_at,
            "user": {
                "id": log.user.id,
                "username": log.user.username
            },
            "metadata": {
                "task_id": log.task_id,
                "action_type": log.action_type
            }
        })
    
    # 获取工作日志
    work_logs = db.query(WorkLog).filter(
        WorkLog.project_id == project_id
    ).order_by(desc(WorkLog.created_at)).offset(skip).limit(limit).all()
    
    for wl in work_logs:
        activities.append({
            "id": f"worklog_{wl.id}",
            "type": "worklog",
            "title": f"{wl.user.username} 提交了工作日志",
            "content": wl.content[:100] + "..." if len(wl.content) > 100 else wl.content,
            "created_at": wl.created_at,
            "user": {
                "id": wl.user.id,
                "username": wl.user.username
            },
            "metadata": {
                "worklog_id": wl.id,
                "duration": wl.duration
            }
        })
    
    # 按时间排序
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "activities": activities[skip:skip+limit],
        "total": len(activities),
        "page": skip // limit + 1,
        "page_size": limit
    }

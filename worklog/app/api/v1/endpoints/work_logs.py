from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import speech_recognition as sr
import json
from math import ceil

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.work_log import WorkLog, Comment
from app.models.work_log_template import WorkLogTemplate
from app.schemas.work_log import WorkLogCreate, WorkLogUpdate, WorkLogResponse, CommentCreate, CommentResponse

# 添加分页响应模型
from pydantic import BaseModel
from typing import List

class WorkLogListResponse(BaseModel):
    items: List[WorkLogResponse]
    total: int
    page: int
    size: int
    pages: int

router = APIRouter()

@router.post("", response_model=WorkLogResponse)
def create_work_log(
    *,
    db: Session = Depends(get_db),
    work_log_in: WorkLogCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建工作日志
    """
    # 处理结束时间：如果没有设置结束时间，根据任务预估时间计算
    end_time = work_log_in.end_time
    if not end_time and work_log_in.task_id:
        from app.models.task import Task
        task = db.query(Task).filter(Task.id == work_log_in.task_id, Task.is_deleted == False).first()
        if task and task.estimated_hours:
            # 根据任务的预估工时计算结束时间
            estimated_duration = timedelta(hours=task.estimated_hours)
            end_time = work_log_in.start_time + estimated_duration
        else:
            # 默认预估2小时
            end_time = work_log_in.start_time + timedelta(hours=2)
    elif not end_time:
        # 如果没有关联任务，默认预估2小时
        end_time = work_log_in.start_time + timedelta(hours=2)
    
    # 计算工作时长（小时）
    duration = (end_time - work_log_in.start_time).total_seconds() / 3600
    
    # 验证任务关联
    if work_log_in.task_id:
        from app.models.task import Task
        task = db.query(Task).filter(Task.id == work_log_in.task_id, Task.is_deleted == False).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联的任务不存在"
            )
        
        # 检查用户是否有权限为该任务创建工作日志
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该任务的负责人，无法创建工作日志"
            )
        
        # 如果工作日志关联了任务，自动设置团队和项目
        if not work_log_in.team_id:
            work_log_in.team_id = task.team_id
        if not work_log_in.project_id:
            work_log_in.project_id = task.project_id
    
    work_log = WorkLog(
        user_id=current_user.id,
        work_type=work_log_in.work_type,
        content=work_log_in.content,  # 直接使用content
        start_time=work_log_in.start_time,
        end_time=end_time,
        duration=duration,  # 直接使用duration
        remark=work_log_in.remark,
        tags=work_log_in.tags,
        attachments=work_log_in.attachments,
        project_id=work_log_in.project_id,
        task_id=work_log_in.task_id,
        team_id=work_log_in.team_id,
        progress_percentage=work_log_in.progress_percentage,
        issues_encountered=work_log_in.issues_encountered,
        solutions_applied=work_log_in.solutions_applied,
        blockers=work_log_in.blockers
    )
    
    db.add(work_log)
    db.commit()
    db.refresh(work_log)
    
    # 如果关联了任务，更新任务的实际工时
    if work_log_in.task_id:
        from app.models.task import Task
        task = db.query(Task).filter(Task.id == work_log_in.task_id).first()
        if task:
            task.actual_hours += duration
            db.add(task)
            db.commit()
    
    # 发送工作日志提交通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_worklog_submitted(
                            db, work_log.id, current_user.id, work_log.team_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送工作日志提交通知：worklog_id={work_log.id}")
    except Exception as e:
        print(f"发送工作日志提交通知失败: {e}")
        # 不影响工作日志创建，只记录错误
    
    # 转换工作日志数据，处理work_type映射
    converted_data = {
        'id': work_log.id,
        'user_id': work_log.user_id,
        'work_type': work_log.work_type,
        'content': work_log.content,
        'start_time': work_log.start_time,
        'end_time': work_log.end_time,
        'duration': work_log.duration,
        'remark': work_log.remark,
        'tags': work_log.tags,
        'attachments': work_log.attachments,
        'project_id': work_log.project_id,
        'task_id': work_log.task_id,
        'team_id': work_log.team_id,
        'progress_percentage': work_log.progress_percentage,
        'issues_encountered': work_log.issues_encountered,
        'solutions_applied': work_log.solutions_applied,
        'blockers': work_log.blockers,
        'created_at': work_log.created_at,
        'updated_at': work_log.updated_at,
        'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
    }
    
    # 处理work_type映射
    work_type_mapping = {
        'development': 'dev',
        'testing': 'test',
        'documentation': 'research',
        'bug_fix': 'dev',
        'other': 'dev'
    }
    if converted_data['work_type'] in work_type_mapping:
        converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
    
    # 添加关联字段
    if work_log.user:
        converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
    if work_log.team:
        converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
    if work_log.project:
        converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
    if work_log.task:
        converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
    
    return converted_data

@router.get("", response_model=WorkLogListResponse)
def read_work_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    work_type: Optional[str] = None,
    tags: Optional[str] = None,
    task_id: Optional[int] = None,  # 按任务ID筛选
    project_id: Optional[int] = None,  # 按项目ID筛选
    team_id: Optional[int] = None,  # 按团队ID筛选
) -> Any:
    """
    获取工作日志列表
    """
    query = db.query(WorkLog).filter(WorkLog.user_id == current_user.id)
    
    # 转换日期字符串为datetime对象
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(WorkLog.start_time >= start_datetime)
        except ValueError:
            pass  # 忽略无效的日期格式
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(WorkLog.end_time <= end_datetime)
        except ValueError:
            pass  # 忽略无效的日期格式
    
    if work_type:
        query = query.filter(WorkLog.work_type == work_type)
    if tags:
        tag_list = tags.split(",")
        for tag in tag_list:
            query = query.filter(WorkLog.tags.contains(tag))
    if task_id:
        query = query.filter(WorkLog.task_id == task_id)
    if project_id:
        query = query.filter(WorkLog.project_id == project_id)
    if team_id:
        query = query.filter(WorkLog.team_id == team_id)
    
    # 计算分页
    skip = (page - 1) * page_size
    total = query.count()
    pages = ceil(total / page_size) if total > 0 else 0
    
    work_logs = query.order_by(WorkLog.start_time.desc()).offset(skip).limit(page_size).all()
    
    # 转换工作日志数据，处理字段映射
    converted_work_logs = []
    for work_log in work_logs:
        # 创建转换后的数据字典
        converted_data = {
            'id': work_log.id,
            'user_id': work_log.user_id,
            'work_type': work_log.work_type,
            'content': work_log.content,  # 直接使用content
            'start_time': work_log.start_time,
            'end_time': work_log.end_time,
            'duration': work_log.duration,  # 直接使用duration
            'remark': work_log.remark,
            'tags': work_log.tags,
            'attachments': work_log.attachments,
            'project_id': work_log.project_id,
            'task_id': work_log.task_id,
            'team_id': work_log.team_id,
            'progress_percentage': work_log.progress_percentage,
            'issues_encountered': work_log.issues_encountered,
            'solutions_applied': work_log.solutions_applied,
            'blockers': work_log.blockers,
            'created_at': work_log.created_at,
            'updated_at': work_log.updated_at,
            'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
        }
        
        # 处理work_type映射
        work_type_mapping = {
            'development': 'dev',
            'testing': 'test',
            'documentation': 'research',
            'bug_fix': 'dev',
            'other': 'dev'
        }
        if converted_data['work_type'] in work_type_mapping:
            converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
        
        # 添加关联字段
        if work_log.user:
            converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
        if work_log.team:
            converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
        if work_log.project:
            converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
        if work_log.task:
            converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
        
        converted_work_logs.append(converted_data)
    
    return WorkLogListResponse(
        items=converted_work_logs,
        total=total,
        page=page,
        size=page_size,
        pages=pages
    )

@router.get("/{work_log_id}", response_model=WorkLogResponse)
def read_work_log(
    *,
    db: Session = Depends(get_db),
    work_log_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定工作日志
    """
    work_log = db.query(WorkLog).filter(WorkLog.id == work_log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    if work_log.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 转换工作日志数据，处理字段映射
    converted_data = {
        'id': work_log.id,
        'user_id': work_log.user_id,
        'work_type': work_log.work_type,
        'content': work_log.content,
        'start_time': work_log.start_time,
        'end_time': work_log.end_time,
        'duration': work_log.duration,
        'remark': work_log.remark,
        'tags': work_log.tags,
        'attachments': work_log.attachments,
        'project_id': work_log.project_id,
        'task_id': work_log.task_id,
        'team_id': work_log.team_id,
        'progress_percentage': work_log.progress_percentage,
        'issues_encountered': work_log.issues_encountered,
        'solutions_applied': work_log.solutions_applied,
        'blockers': work_log.blockers,
        'created_at': work_log.created_at,
        'updated_at': work_log.updated_at,
        'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
    }
    
    # 处理work_type映射
    work_type_mapping = {
        'development': 'dev',
        'testing': 'test',
        'documentation': 'research',
        'bug_fix': 'dev',
        'other': 'dev'
    }
    if converted_data['work_type'] in work_type_mapping:
        converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
    
    # 添加关联字段
    if work_log.user:
        converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
    if work_log.team:
        converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
    if work_log.project:
        converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
    if work_log.task:
        converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
    
    return converted_data

@router.put("/{work_log_id}", response_model=WorkLogResponse)
def update_work_log(
    *,
    db: Session = Depends(get_db),
    work_log_id: int,
    work_log_in: WorkLogUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新工作日志
    """
    work_log = db.query(WorkLog).filter(WorkLog.id == work_log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    if work_log.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    update_data = work_log_in.dict(exclude_unset=True)
    
    # 处理结束时间：如果没有设置结束时间，根据任务预估时间计算
    if "start_time" in update_data and "end_time" not in update_data:
        start_time = update_data["start_time"]
        if work_log.task_id:
            from app.models.task import Task
            task = db.query(Task).filter(Task.id == work_log.task_id, Task.is_deleted == False).first()
            if task and task.estimated_hours:
                # 根据任务的预估工时计算结束时间
                estimated_duration = timedelta(hours=task.estimated_hours)
                update_data["end_time"] = start_time + estimated_duration
            else:
                # 默认预估2小时
                update_data["end_time"] = start_time + timedelta(hours=2)
        else:
            # 如果没有关联任务，默认预估2小时
            update_data["end_time"] = start_time + timedelta(hours=2)
    
    # 如果更新了开始时间或结束时间，重新计算工作时长
    if "start_time" in update_data or "end_time" in update_data:
        start_time = update_data.get("start_time", work_log.start_time)
        end_time = update_data.get("end_time", work_log.end_time)
        update_data["duration"] = (end_time - start_time).total_seconds() / 3600
    
    for field, value in update_data.items():
        setattr(work_log, field, value)
    
    db.add(work_log)
    db.commit()
    db.refresh(work_log)
    
    # 发送工作日志提交通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_worklog_submitted(
                            db, work_log.id, current_user.id, work_log.team_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送工作日志提交通知：worklog_id={work_log.id}")
    except Exception as e:
        print(f"发送工作日志提交通知失败: {e}")
        # 不影响工作日志创建，只记录错误
    
    # 转换工作日志数据，处理work_type映射
    converted_data = {
        'id': work_log.id,
        'user_id': work_log.user_id,
        'work_type': work_log.work_type,
        'content': work_log.content,
        'start_time': work_log.start_time,
        'end_time': work_log.end_time,
        'duration': work_log.duration,
        'remark': work_log.remark,
        'tags': work_log.tags,
        'attachments': work_log.attachments,
        'project_id': work_log.project_id,
        'task_id': work_log.task_id,
        'team_id': work_log.team_id,
        'progress_percentage': work_log.progress_percentage,
        'issues_encountered': work_log.issues_encountered,
        'solutions_applied': work_log.solutions_applied,
        'blockers': work_log.blockers,
        'created_at': work_log.created_at,
        'updated_at': work_log.updated_at,
        'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
    }
    
    # 处理work_type映射
    work_type_mapping = {
        'development': 'dev',
        'testing': 'test',
        'documentation': 'research',
        'bug_fix': 'dev',
        'other': 'dev'
    }
    if converted_data['work_type'] in work_type_mapping:
        converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
    
    # 添加关联字段
    if work_log.user:
        converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
    if work_log.team:
        converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
    if work_log.project:
        converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
    if work_log.task:
        converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
    
    return converted_data

@router.delete("/{work_log_id}")
def delete_work_log(
    *,
    db: Session = Depends(get_db),
    work_log_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除工作日志
    """
    work_log = db.query(WorkLog).filter(WorkLog.id == work_log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    if work_log.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    db.delete(work_log)
    db.commit()
    return {"status": "success"}

@router.post("/{work_log_id}/comments", response_model=CommentResponse)
def create_comment(
    *,
    db: Session = Depends(get_db),
    work_log_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    添加评论
    """
    work_log = db.query(WorkLog).filter(WorkLog.id == work_log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    
    comment = Comment(
        work_log_id=work_log_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.post("/quick", response_model=WorkLogResponse)
def quick_create_work_log(
    *,
    db: Session = Depends(get_db),
    work_type: str,
    content: str,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    tags: Optional[str] = None,
    task_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    快速创建工作日志
    """
    # 处理结束时间：如果没有设置结束时间，根据任务预估时间计算
    if not end_time and task_id:
        from app.models.task import Task
        task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
        if task and task.estimated_hours:
            # 根据任务的预估工时计算结束时间
            estimated_duration = timedelta(hours=task.estimated_hours)
            end_time = start_time + estimated_duration
        else:
            # 默认预估2小时
            end_time = start_time + timedelta(hours=2)
    elif not end_time:
        # 如果没有关联任务，默认预估2小时
        end_time = start_time + timedelta(hours=2)
    
    # 计算工作时长
    duration = (end_time - start_time).total_seconds() / 3600
    
    # 验证任务关联
    if task_id:
        from app.models.task import Task
        task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联的任务不存在"
            )
        
        # 检查用户是否有权限为该任务创建工作日志
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该任务的负责人，无法创建工作日志"
            )
    
    work_log = WorkLog(
        user_id=current_user.id,
        work_type=work_type,
        content=content,  # 直接使用content
        start_time=start_time,
        end_time=end_time,
        duration=duration,  # 直接使用duration
        tags=tags,
        task_id=task_id,
        team_id=task.team_id if task else None,
        project_id=task.project_id if task else None
    )
    
    db.add(work_log)
    db.commit()
    db.refresh(work_log)
    
    # 如果关联了任务，更新任务的实际工时
    if task_id and task:
        task.actual_hours += duration
        db.add(task)
        db.commit()
    
    # 发送工作日志提交通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_worklog_submitted(
                            db, work_log.id, current_user.id, work_log.team_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送工作日志提交通知：worklog_id={work_log.id}")
    except Exception as e:
        print(f"发送工作日志提交通知失败: {e}")
        # 不影响工作日志创建，只记录错误
    
    # 转换工作日志数据，处理work_type映射
    converted_data = {
        'id': work_log.id,
        'user_id': work_log.user_id,
        'work_type': work_log.work_type,
        'content': work_log.content,
        'start_time': work_log.start_time,
        'end_time': work_log.end_time,
        'duration': work_log.duration,
        'remark': work_log.remark,
        'tags': work_log.tags,
        'attachments': work_log.attachments,
        'project_id': work_log.project_id,
        'task_id': work_log.task_id,
        'team_id': work_log.team_id,
        'progress_percentage': work_log.progress_percentage,
        'issues_encountered': work_log.issues_encountered,
        'solutions_applied': work_log.solutions_applied,
        'blockers': work_log.blockers,
        'created_at': work_log.created_at,
        'updated_at': work_log.updated_at,
        'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
    }
    
    # 处理work_type映射
    work_type_mapping = {
        'development': 'dev',
        'testing': 'test',
        'documentation': 'research',
        'bug_fix': 'dev',
        'other': 'dev'
    }
    if converted_data['work_type'] in work_type_mapping:
        converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
    
    # 添加关联字段
    if work_log.user:
        converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
    if work_log.team:
        converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
    if work_log.project:
        converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
    if work_log.task:
        converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
    
    return converted_data

@router.post("/voice", response_model=WorkLogResponse)
async def create_work_log_from_voice(
    *,
    db: Session = Depends(get_db),
    audio_file: UploadFile = File(...),
    work_type: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    通过语音创建工作日志
    """
    try:
        # 保存音频文件
        audio_path = f"temp/{audio_file.filename}"
        with open(audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # 语音识别
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            content = recognizer.recognize_google(audio, language='zh-CN')
        
        # 创建工作日志
        work_log = WorkLog(
            user_id=current_user.id,
            work_type=work_type,
            content=content,  # 改为content
            duration=0.5  # 默认时长
        )
        db.add(work_log)
        db.commit()
        db.refresh(work_log)
        
        # 发送工作日志提交通知
        try:
            from app.core.message_service import message_push_service
            import asyncio
            
            # 获取当前事件循环
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，使用call_soon_threadsafe
                    loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(
                            message_push_service.notify_worklog_submitted(
                                db, work_log.id, current_user.id, work_log.team_id
                            )
                        )
                    )
                else:
                    # 如果事件循环没有运行，直接运行
                    loop.run_until_complete(
                        message_push_service.notify_worklog_submitted(
                            db, work_log.id, current_user.id, work_log.team_id
                        )
                    )
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        message_push_service.notify_worklog_submitted(
                            db, work_log.id, current_user.id, work_log.team_id
                        )
                    )
                finally:
                    loop.close()
            
            print(f"已发送工作日志提交通知：worklog_id={work_log.id}")
        except Exception as e:
            print(f"发送工作日志提交通知失败: {e}")
            # 不影响工作日志创建，只记录错误
        
        # 转换工作日志数据，处理work_type映射
        converted_data = {
            'id': work_log.id,
            'user_id': work_log.user_id,
            'work_type': work_log.work_type,
            'content': work_log.content,
            'start_time': work_log.start_time,
            'end_time': work_log.end_time,
            'duration': work_log.duration,
            'remark': work_log.remark,
            'tags': work_log.tags,
            'attachments': work_log.attachments,
            'project_id': work_log.project_id,
            'task_id': work_log.task_id,
            'team_id': work_log.team_id,
            'progress_percentage': work_log.progress_percentage,
            'issues_encountered': work_log.issues_encountered,
            'solutions_applied': work_log.solutions_applied,
            'blockers': work_log.blockers,
            'created_at': work_log.created_at,
            'updated_at': work_log.updated_at,
            'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
        }
        
        # 处理work_type映射
        work_type_mapping = {
            'development': 'dev',
            'testing': 'test',
            'documentation': 'research',
            'bug_fix': 'dev',
            'other': 'dev'
        }
        if converted_data['work_type'] in work_type_mapping:
            converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
        
        # 添加关联字段
        if work_log.user:
            converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
        if work_log.team:
            converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
        if work_log.project:
            converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
        if work_log.task:
            converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
        
        return converted_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"语音识别失败: {str(e)}"
        )

@router.post("/copy/{work_log_id}", response_model=WorkLogResponse)
def copy_work_log(
    *,
    db: Session = Depends(get_db),
    work_log_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    复制已有的工作日志
    """
    # 获取原工作日志
    work_log = db.query(WorkLog).filter(WorkLog.id == work_log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    if work_log.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 创建新工作日志
    new_work_log = WorkLog(
        user_id=current_user.id,
        work_type=work_log.work_type,
        content=work_log.content,  # 直接使用content
        duration=work_log.duration,  # 直接使用duration
        tags=work_log.tags
    )
    db.add(new_work_log)
    db.commit()
    db.refresh(new_work_log)
    
    # 发送工作日志提交通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_worklog_submitted(
                            db, new_work_log.id, current_user.id, new_work_log.team_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, new_work_log.id, current_user.id, new_work_log.team_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, new_work_log.id, current_user.id, new_work_log.team_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送工作日志提交通知：worklog_id={new_work_log.id}")
    except Exception as e:
        print(f"发送工作日志提交通知失败: {e}")
        # 不影响工作日志创建，只记录错误
    
    # 转换工作日志数据，处理work_type映射
    converted_data = {
        'id': new_work_log.id,
        'user_id': new_work_log.user_id,
        'work_type': new_work_log.work_type,
        'content': new_work_log.content,
        'start_time': new_work_log.start_time,
        'end_time': new_work_log.end_time,
        'duration': new_work_log.duration,
        'remark': new_work_log.remark,
        'tags': new_work_log.tags,
        'attachments': new_work_log.attachments,
        'project_id': new_work_log.project_id,
        'task_id': new_work_log.task_id,
        'team_id': new_work_log.team_id,
        'progress_percentage': new_work_log.progress_percentage,
        'issues_encountered': new_work_log.issues_encountered,
        'solutions_applied': new_work_log.solutions_applied,
        'blockers': new_work_log.blockers,
        'created_at': new_work_log.created_at,
        'updated_at': new_work_log.updated_at,
        'title': new_work_log.content if new_work_log.content else f"工作日志 #{new_work_log.id}"
    }
    
    # 处理work_type映射
    work_type_mapping = {
        'development': 'dev',
        'testing': 'test',
        'documentation': 'research',
        'bug_fix': 'dev',
        'other': 'dev'
    }
    if converted_data['work_type'] in work_type_mapping:
        converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
    
    # 添加关联字段
    if new_work_log.user:
        converted_data['user_name'] = new_work_log.user.username if hasattr(new_work_log.user, 'username') else None
    if new_work_log.team:
        converted_data['team_name'] = new_work_log.team.name if hasattr(new_work_log.team, 'name') else None
    if new_work_log.project:
        converted_data['project_name'] = new_work_log.project.name if hasattr(new_work_log.project, 'name') else None
    if new_work_log.task:
        converted_data['task_title'] = new_work_log.task.title if hasattr(new_work_log.task, 'title') else None
    
    return converted_data

@router.get("/last", response_model=WorkLogResponse)
def get_last_work_log(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取最后一条工作日志
    """
    work_log = db.query(WorkLog).filter(
        WorkLog.user_id == current_user.id
    ).order_by(WorkLog.start_time.desc()).first()
    
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有找到工作日志"
        )
    
    # 发送工作日志提交通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_worklog_submitted(
                            db, work_log.id, current_user.id, work_log.team_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_log.id, current_user.id, work_log.team_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送工作日志提交通知：worklog_id={work_log.id}")
    except Exception as e:
        print(f"发送工作日志提交通知失败: {e}")
        # 不影响工作日志创建，只记录错误
    
    # 转换工作日志数据，处理字段映射
    converted_data = {
        'id': work_log.id,
        'user_id': work_log.user_id,
        'work_type': work_log.work_type,
        'content': work_log.content,  # 直接使用content
        'start_time': work_log.start_time,
        'end_time': work_log.end_time,
        'duration': work_log.duration,
        'remark': work_log.remark,
        'tags': work_log.tags,
        'attachments': work_log.attachments,
        'project_id': work_log.project_id,
        'task_id': work_log.task_id,
        'team_id': work_log.team_id,
        'progress_percentage': work_log.progress_percentage,
        'issues_encountered': work_log.issues_encountered,
        'solutions_applied': work_log.solutions_applied,
        'blockers': work_log.blockers,
        'created_at': work_log.created_at,
        'updated_at': work_log.updated_at,
        'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
    }
    
    # 处理work_type映射
    work_type_mapping = {
        'development': 'dev',
        'testing': 'test',
        'documentation': 'research',
        'bug_fix': 'dev',
        'other': 'dev'
    }
    if converted_data['work_type'] in work_type_mapping:
        converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
    
    # 添加关联字段
    if work_log.user:
        converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
    if work_log.team:
        converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
    if work_log.project:
        converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
    if work_log.task:
        converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
    
    return converted_data

@router.get("/templates/recommend", response_model=List[WorkLogCreate])
def recommend_templates(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    推荐工作日志模板
    """
    # 获取用户最近使用的工作类型
    recent_work_type = db.query(WorkLog.work_type).filter(
        WorkLog.user_id == current_user.id
    ).order_by(WorkLog.start_time.desc()).first()
    
    # 获取推荐模板
    templates = []
    
    # 1. 获取默认模板
    default_template = db.query(WorkLogTemplate).filter(
        WorkLogTemplate.user_id == current_user.id,
        WorkLogTemplate.is_default == True
    ).first()
    if default_template:
        templates.append(WorkLogCreate(
            work_type=default_template.work_type,
            content=default_template.content_template,
            duration=default_template.duration or 0.0,
            tags=default_template.tags
        ))
    
    # 2. 获取最近工作类型的常用模板
    if recent_work_type:
        recent_templates = db.query(WorkLogTemplate).filter(
            WorkLogTemplate.user_id == current_user.id,
            WorkLogTemplate.work_type == recent_work_type[0]
        ).order_by(WorkLogTemplate.use_count.desc()).limit(2).all()
        
        for template in recent_templates:
            if template != default_template:
                templates.append(WorkLogCreate(
                    work_type=template.work_type,
                    content=template.content_template,
                    duration=template.duration or 0.0,
                    tags=template.tags
                ))
    
    return templates

@router.get("/task/{task_id}", response_model=List[WorkLogResponse])
def get_task_work_logs(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取指定任务的工作日志
    """
    # 验证任务是否存在
    from app.models.task import Task
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限
    can_view = (
        task.assignee_id == current_user.id or
        task.creator_id == current_user.id
    )
    
    # 如果是团队成员，也可以查看
    if not can_view:
        from app.models.team_member import TeamMember
        team_member = db.query(TeamMember).filter(
            TeamMember.team_id == task.team_id,
            TeamMember.user_id == current_user.id
        ).first()
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限查看该任务的工作日志"
            )
    
    # 查询任务相关的工作日志
    work_logs = db.query(WorkLog).filter(
        WorkLog.task_id == task_id
    ).order_by(WorkLog.start_time.desc()).offset(skip).limit(limit).all()
    
    # 发送工作日志提交通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_worklog_submitted(
                            db, work_logs[0].id, current_user.id, work_logs[0].team_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_logs[0].id, current_user.id, work_logs[0].team_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, work_logs[0].id, current_user.id, work_logs[0].team_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送工作日志提交通知：worklog_id={work_logs[0].id}")
    except Exception as e:
        print(f"发送工作日志提交通知失败: {e}")
        # 不影响工作日志创建，只记录错误
    
    # 转换工作日志数据，处理字段映射
    converted_work_logs = []
    for work_log in work_logs:
        # 创建转换后的数据字典
        converted_data = {
            'id': work_log.id,
            'user_id': work_log.user_id,
            'work_type': work_log.work_type,
            'content': work_log.content,  # 直接使用content
            'start_time': work_log.start_time,
            'end_time': work_log.end_time,
            'duration': work_log.duration,
            'remark': work_log.remark,
            'tags': work_log.tags,
            'attachments': work_log.attachments,
            'project_id': work_log.project_id,
            'task_id': work_log.task_id,
            'team_id': work_log.team_id,
            'progress_percentage': work_log.progress_percentage,
            'issues_encountered': work_log.issues_encountered,
            'solutions_applied': work_log.solutions_applied,
            'blockers': work_log.blockers,
            'created_at': work_log.created_at,
            'updated_at': work_log.updated_at,
            'title': work_log.content if work_log.content else f"工作日志 #{work_log.id}"
        }
        
        # 处理work_type映射
        work_type_mapping = {
            'development': 'dev',
            'testing': 'test',
            'documentation': 'research',
            'bug_fix': 'dev',
            'other': 'dev'
        }
        if converted_data['work_type'] in work_type_mapping:
            converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
        
        # 添加关联字段
        if work_log.user:
            converted_data['user_name'] = work_log.user.username if hasattr(work_log.user, 'username') else None
        if work_log.team:
            converted_data['team_name'] = work_log.team.name if hasattr(work_log.team, 'name') else None
        if work_log.project:
            converted_data['project_name'] = work_log.project.name if hasattr(work_log.project, 'name') else None
        if work_log.task:
            converted_data['task_title'] = work_log.task.title if hasattr(work_log.task, 'title') else None
        
        converted_work_logs.append(converted_data)
    
    return converted_work_logs

@router.get("/task/{task_id}/summary")
def get_task_work_summary(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取任务工作汇总信息
    """
    # 验证任务是否存在
    from app.models.task import Task
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限
    can_view = (
        task.assignee_id == current_user.id or
        task.creator_id == current_user.id
    )
    
    # 如果是团队成员，也可以查看
    if not can_view:
        from app.models.team_member import TeamMember
        team_member = db.query(TeamMember).filter(
            TeamMember.team_id == task.team_id,
            TeamMember.user_id == current_user.id
        ).first()
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限查看该任务的工作汇总"
            )
    
    # 查询任务相关的工作日志统计
    from sqlalchemy import func
    
    # 总工时
    total_hours = db.query(func.sum(WorkLog.duration)).filter(
        WorkLog.task_id == task_id
    ).scalar() or 0.0
    
    # 工作日志数量
    work_log_count = db.query(func.count(WorkLog.id)).filter(
        WorkLog.task_id == task_id
    ).scalar() or 0
    
    # 按工作类型统计
    work_type_stats = db.query(
        WorkLog.work_type,
        func.count(WorkLog.id).label('count'),
        func.sum(WorkLog.duration).label('hours')
    ).filter(
        WorkLog.task_id == task_id
    ).group_by(WorkLog.work_type).all()
    
    # 按用户统计
    user_stats = db.query(
        WorkLog.user_id,
        func.count(WorkLog.id).label('count'),
        func.sum(WorkLog.duration).label('hours')
    ).filter(
        WorkLog.task_id == task_id
    ).group_by(WorkLog.user_id).all()
    
    return {
        "task_id": task_id,
        "task_title": task.title,
        "total_hours": total_hours,
        "work_log_count": work_log_count,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "work_type_stats": [
            {
                "work_type": stat.work_type,
                "count": stat.count,
                "hours": stat.hours or 0.0
            }
            for stat in work_type_stats
        ],
        "user_stats": [
            {
                "user_id": stat.user_id,
                "count": stat.count,
                "hours": stat.hours or 0.0
            }
            for stat in user_stats
        ]
    }

@router.put("/task/{task_id}/update-latest", response_model=WorkLogResponse)
def update_latest_task_work_log(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    work_log_update: WorkLogUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新任务的最新工作日志（补充工作详情）
    """
    # 验证任务是否存在
    from app.models.task import Task
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限
    can_update = (
        task.assignee_id == current_user.id or 
        task.creator_id == current_user.id
    )
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该任务的负责人"
        )
    
    # 查找该任务的最新工作日志
    latest_work_log = db.query(WorkLog).filter(
        WorkLog.task_id == task_id,
        WorkLog.user_id == current_user.id
    ).order_by(WorkLog.created_at.desc()).first()
    
    if not latest_work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该任务的工作日志"
        )
    
    # 更新工作日志
    update_data = work_log_update.dict(exclude_unset=True)
    
    # 如果更新了开始时间或结束时间，重新计算工作时长
    if "start_time" in update_data or "end_time" in update_data:
        start_time = update_data.get("start_time", latest_work_log.start_time)
        end_time = update_data.get("end_time", latest_work_log.end_time)
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds() / 3600
            update_data["duration"] = duration
    
    for field, value in update_data.items():
        setattr(latest_work_log, field, value)
    
    db.add(latest_work_log)
    db.commit()
    db.refresh(latest_work_log)
    
    # 发送工作日志提交通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_worklog_submitted(
                            db, latest_work_log.id, current_user.id, latest_work_log.team_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, latest_work_log.id, current_user.id, latest_work_log.team_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_worklog_submitted(
                        db, latest_work_log.id, current_user.id, latest_work_log.team_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送工作日志提交通知：worklog_id={latest_work_log.id}")
    except Exception as e:
        print(f"发送工作日志提交通知失败: {e}")
        # 不影响工作日志创建，只记录错误
    
    # 转换工作日志数据，处理work_type映射
    converted_data = {
        'id': latest_work_log.id,
        'user_id': latest_work_log.user_id,
        'work_type': latest_work_log.work_type,
        'content': latest_work_log.content,
        'start_time': latest_work_log.start_time,
        'end_time': latest_work_log.end_time,
        'duration': latest_work_log.duration,
        'remark': latest_work_log.remark,
        'tags': latest_work_log.tags,
        'attachments': latest_work_log.attachments,
        'project_id': latest_work_log.project_id,
        'task_id': latest_work_log.task_id,
        'team_id': latest_work_log.team_id,
        'progress_percentage': latest_work_log.progress_percentage,
        'issues_encountered': latest_work_log.issues_encountered,
        'solutions_applied': latest_work_log.solutions_applied,
        'blockers': latest_work_log.blockers,
        'created_at': latest_work_log.created_at,
        'updated_at': latest_work_log.updated_at,
        'title': latest_work_log.content if latest_work_log.content else f"工作日志 #{latest_work_log.id}"
    }
    
    # 处理work_type映射
    work_type_mapping = {
        'development': 'dev',
        'testing': 'test',
        'documentation': 'research',
        'bug_fix': 'dev',
        'other': 'dev'
    }
    if converted_data['work_type'] in work_type_mapping:
        converted_data['work_type'] = work_type_mapping[converted_data['work_type']]
    
    # 添加关联字段
    if latest_work_log.user:
        converted_data['user_name'] = latest_work_log.user.username if hasattr(latest_work_log.user, 'username') else None
    if latest_work_log.team:
        converted_data['team_name'] = latest_work_log.team.name if hasattr(latest_work_log.team, 'name') else None
    if latest_work_log.project:
        converted_data['project_name'] = latest_work_log.project.name if hasattr(latest_work_log.project, 'name') else None
    if latest_work_log.task:
        converted_data['task_title'] = latest_work_log.task.title if hasattr(latest_work_log.task, 'title') else None
    
    return converted_data 
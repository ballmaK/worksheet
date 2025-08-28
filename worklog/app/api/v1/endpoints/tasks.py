from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, case
from datetime import datetime, timedelta
import json
import os
import shutil
from pathlib import Path
import logging

from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.task import Task, TaskDependency, TaskComment, TaskAttachment, TaskStatus, TaskPriority, TaskType
from app.models.work_log import WorkLog, WorkLogType
from app.models.enums import TEAM_ADMIN, TEAM_MEMBER
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskCommentBase, TaskCommentResponse,
    TaskStatistics, TaskFilter, TaskQuickCreate
)
from app.models.project import Project
from app.crud import task_log
from app.models.task_log import TaskLog
from app.core.message_service import message_push_service

logger = logging.getLogger(__name__)

router = APIRouter()

# 快速创建任务接口
@router.post("/quick", response_model=TaskResponse)
def create_task_quick(
    task_in: TaskQuickCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """快速创建任务 - 只需要标题，其他字段使用默认值"""
    logger.info(f"开始快速创建任务，输入参数：{task_in}")
    
    # 确定团队ID
    team_id = task_in.team_id
    if not team_id:
        # 如果没有指定团队，使用用户的第一个团队
        member = db.query(TeamMember).filter(
            TeamMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您还没有加入任何团队，请先加入团队"
            )
        team_id = member.team_id
        logger.info(f"使用用户默认团队：team_id={team_id}")
    
    # 检查团队是否存在且用户是团队成员
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        logger.error(f"团队不存在：team_id={team_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )

    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        logger.error(f"用户不是团队成员：user_id={current_user.id}, team_id={team_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )

    # 确定负责人ID
    assignee_id = None
    if member.role == TEAM_ADMIN:
        # 管理员可以创建未分配的任务
        assignee_id = None
        logger.info("管理员创建任务，不指定负责人")
    else:
        # 非管理员创建任务时，默认负责人就是自己
        assignee_id = current_user.id
        logger.info(f"非管理员创建任务，默认负责人为自己：assignee_id={assignee_id}")

    # 创建任务 - 使用默认值
    task = Task(
        title=task_in.title,
        description="",  # 空描述
        team_id=team_id,
        project_id=None,  # 不指定项目
        assignee_id=assignee_id,  # 根据用户角色确定负责人
        creator_id=current_user.id,
        status=TaskStatus.PENDING,  # 默认待分配状态
        priority=task_in.priority,  # 使用传入的优先级
        due_date=None,  # 不设置截止日期
        estimated_hours=None,  # 不设置预估工时
        task_type=TaskType.OTHER,  # 默认其他类型
        tags=None,  # 不设置标签
        actual_hours=0,  # 新创建的任务，实际工时为0
        is_deleted=False
    )
    
    logger.info(f"准备保存快速创建的任务：{task.__dict__}")
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"任务已保存：id={task.id}")
    
    # 记录任务创建日志
    try:
        task_log.log_task_creation(db, task, current_user.id)
        logger.info(f"已记录任务创建日志：task_id={task.id}")
    except Exception as e:
        logger.error(f"记录任务创建日志失败：{str(e)}")
        # 不影响任务创建，只记录错误
    
    # 加载关联信息
    task.creator = current_user
    if task.assignee_id:
        task.assignee = db.query(User).filter(User.id == task.assignee_id).first()
        logger.info(f"已加载负责人信息：assignee_id={task.assignee_id}, username={task.assignee.username if task.assignee else None}")
    task.comments = []
    task.comment_count = 0

    # 发送任务创建通知
    try:
        # 直接发送通知，不使用后台线程
        from app.core.message_service import message_push_service
        import asyncio

        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_task_created(db, task, current_user.id)
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_task_created(db, task, current_user.id)
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_task_created(db, task, current_user.id)
                )
            finally:
                loop.close()

        logger.info(f"已发送任务创建通知：task_id={task.id}")
    except Exception as e:
        logger.error(f"发送任务创建通知失败: {e}")
        # 不影响任务创建，只记录错误
    
    return TaskResponse.from_orm(task)

# 任务管理接口
@router.post("", response_model=TaskResponse)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"开始创建任务，输入参数：{task_in}")
    
    # 检查团队是否存在且用户是团队成员
    team = db.query(Team).filter(Team.id == task_in.team_id).first()
    if not team:
        logger.error(f"团队不存在：team_id={task_in.team_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )

    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task_in.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        logger.error(f"用户不是团队成员：user_id={current_user.id}, team_id={task_in.team_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )

    # 如果指定了项目ID，检查项目是否存在且属于该团队
    if task_in.project_id:
        project = db.query(Project).filter(
            Project.id == task_in.project_id,
            Project.team_id == task_in.team_id
        ).first()
        if not project:
            logger.error(f"项目不存在或不属于指定团队：project_id={task_in.project_id}, team_id={task_in.team_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的项目不存在或不属于该团队"
            )

    # 如果指定了负责人，检查负责人是否是团队成员
    if task_in.assignee_id:
        assignee_member = db.query(TeamMember).filter(
            TeamMember.team_id == task_in.team_id,
            TeamMember.user_id == task_in.assignee_id
        ).first()
        if not assignee_member:
            logger.error(f"指定的负责人不是团队成员：assignee_id={task_in.assignee_id}, team_id={task_in.team_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的负责人不是团队成员"
            )

    # 创建任务
    task = Task(
        title=task_in.title,
        description=task_in.description,
        team_id=task_in.team_id,
        project_id=task_in.project_id,
        assignee_id=task_in.assignee_id,
        creator_id=current_user.id,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        estimated_hours=task_in.estimated_hours,
        task_type=task_in.task_type,
        tags=task_in.tags,
        actual_hours=0,  # 新创建的任务，实际工时为0
        is_deleted=False
    )
    
    logger.info(f"准备保存任务：{task.__dict__}")
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"任务已保存：id={task.id}")
    
    # 记录任务创建日志
    try:
        task_log.log_task_creation(db, task, current_user.id)
        logger.info(f"已记录任务创建日志：task_id={task.id}")
    except Exception as e:
        logger.error(f"记录任务创建日志失败：{str(e)}")
        # 不影响任务创建，只记录错误
    
    # 加载关联信息
    task.creator = current_user
    if task.assignee_id:
        task.assignee = db.query(User).filter(User.id == task.assignee_id).first()
        logger.info(f"已加载负责人信息：assignee_id={task.assignee_id}, username={task.assignee.username if task.assignee else None}")
    task.comments = []
    task.comment_count = 0

    # 发送任务创建通知
    try:
        # 直接发送通知，不使用后台线程
        from app.core.message_service import message_push_service
        import asyncio

        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_task_created(db, task, current_user.id)
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_task_created(db, task, current_user.id)
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_task_created(db, task, current_user.id)
                )
            finally:
                loop.close()

        logger.info(f"已发送任务创建通知：task_id={task.id}")
    except Exception as e:
        logger.error(f"发送任务创建通知失败: {e}")
        # 不影响任务创建，只记录错误
    
    return TaskResponse.from_orm(task)

@router.get("", response_model=TaskListResponse)
def get_tasks(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: Optional[int] = Query(None, description="团队ID"),
    project_id: Optional[int] = Query(None, description="项目ID"),
    status: Optional[str] = Query(None, description="任务状态"),
    priority: Optional[str] = Query(None, description="任务优先级"),
    assignee_id: Optional[int] = Query(None, description="负责人ID"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
) -> Any:
    """获取任务列表"""
    # 构建查询
    query = db.query(Task).filter(Task.is_deleted == False)
    
    # 如果指定了团队ID，检查用户是否是团队成员
    if team_id:
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该团队成员"
            )
        query = query.filter(Task.team_id == team_id)
        
        # 如果不是团队管理员，只能看到自己的任务
        if member.role != TEAM_ADMIN:
            query = query.filter(Task.assignee_id == current_user.id)
    else:
        # 如果没有指定团队，只查询用户所在团队的任务
        user_teams = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id
        ).subquery()
        query = query.filter(Task.team_id.in_(user_teams))
        
        # 添加调试日志
        logger.info(f"用户ID {current_user.id} 所在的团队查询")
        user_team_list = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id
        ).all()
        logger.info(f"用户所在团队: {[t[0] for t in user_team_list]}")
        
        # 检查用户是否是团队管理员
        user_admin_teams = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id,
            TeamMember.role == TEAM_ADMIN
        ).subquery()
        
        # 如果用户不是任何团队的管理员，只能查看自己的任务
        admin_teams_count = db.query(user_admin_teams).count()
        logger.info(f"用户是管理员的团队数量: {admin_teams_count}")
        
        if admin_teams_count == 0:
            query = query.filter(Task.assignee_id == current_user.id)
            logger.info("用户不是管理员，只能查看自己负责的任务")
        else:
            logger.info("用户是管理员，可以查看所有任务")
    
    # 如果指定了项目ID，检查用户是否有权限访问该项目
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查用户是否是项目所属团队的成员
        member = db.query(TeamMember).filter(
            TeamMember.team_id == project.team_id,
            TeamMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限访问该项目"
            )
        
        query = query.filter(Task.project_id == project_id)
        
        # 如果不是团队管理员，只能看到自己的任务
        if member.role != TEAM_ADMIN:
            query = query.filter(Task.assignee_id == current_user.id)
    
    # 应用筛选条件
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        # 直接使用assignee_id，不再需要特殊处理'me'
        query = query.filter(Task.assignee_id == assignee_id)
    if search:
        search_filter = or_(
            Task.title.contains(search),
            Task.description.contains(search)
        )
        query = query.filter(search_filter)
    
    # 计算总数
    total = query.count()
    
    # 分页
    tasks = query.order_by(desc(Task.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    # 添加调试日志
    logger.info(f"查询到 {len(tasks)} 个任务，总数: {total}")
    for task in tasks:
        logger.info(f"任务ID: {task.id}, 标题: {task.title}, 团队: {task.team_id}, 状态: {task.status}, 负责人: {task.assignee_id}, 创建者: {task.creator_id}")
    
    # 加载关联数据
    for task in tasks:
        # 加载创建者信息
        task.creator = db.query(User).filter(User.id == task.creator_id).first()
        
        # 加载负责人信息
        if task.assignee_id:
            task.assignee = db.query(User).filter(User.id == task.assignee_id).first()
        
        # 加载项目信息
        if task.project_id:
            task.project = db.query(Project).filter(Project.id == task.project_id).first()
        
        # 加载评论数量
        task.comment_count = db.query(TaskComment).filter(TaskComment.task_id == task.id).count()
        task.comments = []
    
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size
    
    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

# 统计相关路由 - 必须在 /{task_id} 路由之前
@router.get("/statistics", response_model=TaskStatistics)
def get_task_statistics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: Optional[int] = Query(None, description="团队ID"),
    project_id: Optional[int] = Query(None, description="项目ID"),
    assignee_id: Optional[int] = Query(None, description="负责人ID")
) -> Any:
    """获取任务统计信息"""
    # 打印入参用于调试
    logger.info("=" * 50)
    logger.info("统计接口被调用")
    logger.info(f"当前用户ID: {current_user.id}")
    logger.info(f"统计接口入参: team_id={team_id} (type: {type(team_id)}), project_id={project_id} (type: {type(project_id)}), assignee_id={assignee_id} (type: {type(assignee_id)})")
    logger.info("=" * 50)
    
    # 构建查询
    query = db.query(Task).filter(Task.is_deleted == False)
    
    # 如果指定了团队ID，检查用户是否是团队成员
    if team_id:
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该团队成员"
            )
        query = query.filter(Task.team_id == team_id)
        
        # 如果不是团队管理员，只能统计自己的任务
        if member.role != TEAM_ADMIN:
            query = query.filter(Task.assignee_id == current_user.id)
    else:
        # 如果没有指定团队，只统计用户所在团队的任务
        user_teams = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id
        ).subquery()
        query = query.filter(Task.team_id.in_(user_teams))
        
        # 添加调试日志
        logger.info(f"统计接口 - 用户ID {current_user.id} 所在的团队查询")
        user_team_list = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id
        ).all()
        logger.info(f"统计接口 - 用户所在团队: {[t[0] for t in user_team_list]}")
        
        # 检查用户是否是团队管理员
        user_admin_teams = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id,
            TeamMember.role == TEAM_ADMIN
        ).subquery()
        
        # 如果用户不是任何团队的管理员，只能统计自己的任务
        admin_teams_count = db.query(user_admin_teams).count()
        logger.info(f"统计接口 - 用户是管理员的团队数量: {admin_teams_count}")
        
        if admin_teams_count == 0:
            query = query.filter(Task.assignee_id == current_user.id)
            logger.info("统计接口 - 用户不是管理员，只能统计自己负责的任务")
        else:
            logger.info("统计接口 - 用户是管理员，可以统计所有任务")
    
    # 如果指定了项目ID，检查用户是否有权限访问该项目
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查用户是否是项目所属团队的成员
        member = db.query(TeamMember).filter(
            TeamMember.team_id == project.team_id,
            TeamMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限访问该项目"
            )
        
        query = query.filter(Task.project_id == project_id)
    
    # 如果指定了负责人ID
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    
    # 统计各状态的任务数量
    total_tasks = query.count()
    pending_tasks = query.filter(Task.status == 'pending').count()
    in_progress_tasks = query.filter(Task.status == 'in_progress').count()
    completed_tasks = query.filter(Task.status == 'completed').count()
    review_tasks = query.filter(Task.status == 'review').count()
    cancelled_tasks = query.filter(Task.status == 'cancelled').count()
    
    # 添加调试日志
    logger.info(f"统计结果 - 总数: {total_tasks}, 待分派: {pending_tasks}, 进行中: {in_progress_tasks}, 已完成: {completed_tasks}")
    
    # 统计逾期任务
    overdue_tasks = query.filter(
        and_(
            Task.due_date < datetime.now(),
            Task.status.in_(['pending', 'in_progress', 'review'])
        )
    ).count()
    
    # 统计工时
    total_estimated_hours = query.with_entities(func.sum(Task.estimated_hours)).scalar() or 0
    completed_hours = query.filter(Task.status == 'completed').with_entities(func.sum(Task.actual_hours)).scalar() or 0
    
    # 计算完成率
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return TaskStatistics(
        total=total_tasks,
        pending=pending_tasks,
        in_progress=in_progress_tasks,
        completed=completed_tasks,
        review=review_tasks,
        cancelled=cancelled_tasks,
        overdue=overdue_tasks,
        total_estimated_hours=total_estimated_hours,
        completed_hours=completed_hours,
        completion_rate=completion_rate
    )

@router.get("/statistics/team/{team_id}", response_model=TaskStatistics)
def get_team_task_statistics(
    *,
    db: Session = Depends(get_db),
    team_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取团队任务统计信息"""
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 构建查询
    query = db.query(Task).filter(
        Task.team_id == team_id,
        Task.is_deleted == False
    )
    
    # 统计各状态的任务数量
    total_tasks = query.count()
    pending_tasks = query.filter(Task.status == 'pending').count()
    in_progress_tasks = query.filter(Task.status == 'in_progress').count()
    completed_tasks = query.filter(Task.status == 'completed').count()
    
    # 统计逾期任务
    overdue_tasks = query.filter(
        and_(
            Task.due_date < datetime.now(),
            Task.status.in_(['pending', 'in_progress', 'review'])
        )
    ).count()
    
    # 统计工时
    total_estimated_hours = query.with_entities(func.sum(Task.estimated_hours)).scalar() or 0
    total_actual_hours = query.filter(Task.status == 'completed').with_entities(func.sum(Task.actual_hours)).scalar() or 0
    
    # 计算完成率
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return TaskStatistics(
        total=total_tasks,
        pending=pending_tasks,
        in_progress=in_progress_tasks,
        completed=completed_tasks,
        review=0,  # 团队统计中没有review状态
        cancelled=0,  # 团队统计中没有cancelled状态
        overdue=overdue_tasks,
        total_estimated_hours=total_estimated_hours,
        completed_hours=total_actual_hours,
        completion_rate=completion_rate
    )

@router.get("/statistics/project/{project_id}", response_model=TaskStatistics)
def get_project_task_statistics(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取项目任务统计信息"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否是项目所属团队的成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == project.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问该项目"
        )
    
    # 构建查询
    query = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False
    )
    
    # 统计各状态的任务数量
    total_tasks = query.count()
    pending_tasks = query.filter(Task.status == 'pending').count()
    in_progress_tasks = query.filter(Task.status == 'in_progress').count()
    completed_tasks = query.filter(Task.status == 'completed').count()
    review_tasks = query.filter(Task.status == 'review').count()
    cancelled_tasks = query.filter(Task.status == 'cancelled').count()
    
    # 统计逾期任务
    overdue_tasks = query.filter(
        and_(
            Task.due_date < datetime.now(),
            Task.status.in_(['pending', 'in_progress', 'review'])
        )
    ).count()
    
    # 统计工时
    total_estimated_hours = query.with_entities(func.sum(Task.estimated_hours)).scalar() or 0
    completed_hours = query.filter(Task.status == 'completed').with_entities(func.sum(Task.actual_hours)).scalar() or 0
    
    # 计算完成率
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return TaskStatistics(
        total=total_tasks,
        pending=pending_tasks,
        in_progress=in_progress_tasks,
        completed=completed_tasks,
        review=review_tasks,
        cancelled=cancelled_tasks,
        overdue=overdue_tasks,
        total_estimated_hours=total_estimated_hours,
        completed_hours=completed_hours,
        completion_rate=completion_rate
    )

# 单个任务相关路由
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 加载关联数据
    task.creator = db.query(User).filter(User.id == task.creator_id).first()
    
    if task.assignee_id:
        task.assignee = db.query(User).filter(User.id == task.assignee_id).first()
    
    task.comment_count = db.query(TaskComment).filter(TaskComment.task_id == task.id).count()
    task.comments = []
    
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 只有任务创建者、负责人或团队管理员可以更新任务
    can_update = (
        task.creator_id == current_user.id or
        task.assignee_id == current_user.id or
        member.role == TEAM_ADMIN
    )
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限更新此任务"
        )
    
    # 记录更新前的值
    old_status = task.status
    old_assignee_id = task.assignee_id
    
    # 添加调试日志
    logger.info(f"更新前状态：task_id={task_id}, old_status={old_status}, old_assignee_id={old_assignee_id}")
    
    # 更新任务
    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # 添加调试日志
    logger.info(f"更新后状态：task_id={task_id}, new_status={task.status}, new_assignee_id={task.assignee_id}")
    logger.info(f"更新数据：{update_data}")
    
    # 自动状态变更逻辑
    # 数据一致性检查和自动修正
    # 如果任务有负责人但状态是待分配，自动修正为已分配状态
    if (task.assignee_id is not None and task.status == TaskStatus.PENDING):
        task.status = TaskStatus.ASSIGNED
        logger.info(f"数据一致性修正：任务有负责人但状态为待分配，自动修正为已分配：task_id={task_id}")
    # 如果任务没有负责人但状态是已分配，自动修正为待分配状态
    elif (task.assignee_id is None and task.status == TaskStatus.ASSIGNED):
        task.status = TaskStatus.PENDING
        logger.info(f"数据一致性修正：任务无负责人但状态为已分配，自动修正为待分配：task_id={task_id}")
    # 如果任务当前是待分配状态且分配了负责人，自动改为已分配状态
    elif (old_status == TaskStatus.PENDING and 
          old_assignee_id is None and 
          task.assignee_id is not None):
        task.status = TaskStatus.ASSIGNED
        logger.info(f"任务状态从待分配改为已分配：task_id={task_id}")
    # 如果任务当前是已分配状态且清除了负责人，自动改为待分配状态
    elif (old_status == TaskStatus.ASSIGNED and 
          old_assignee_id is not None and 
          task.assignee_id is None):
        task.status = TaskStatus.PENDING
        logger.info(f"任务状态从已分配改为待分配：task_id={task_id}")
    # 如果用户明确设置了状态，优先使用用户设置的状态
    elif 'status' in update_data:
        # 用户明确设置了状态，不进行自动变更
        logger.info(f"用户明确设置任务状态：task_id={task_id}, status={task.status}")
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 记录状态变化日志
    try:
        if 'status' in update_data and old_status != task.status:
            task_log.log_task_status_change(
                db=db,
                task=task,
                user_id=current_user.id,
                old_status=old_status,
                new_status=task.status,
                reason=update_data.get('reason'),
                comment=update_data.get('comment')
            )
            logger.info(f"已记录任务状态变化：task_id={task.id}, {old_status} -> {task.status}")
        elif old_status != task.status:
            # 记录自动状态变更或数据一致性修正
            reason = "自动状态变更"
            comment = "根据负责人分配情况自动调整任务状态"
            if (old_status == TaskStatus.PENDING and task.status == TaskStatus.ASSIGNED and task.assignee_id is not None):
                reason = "数据一致性修正"
                comment = "任务有负责人但状态为待分配，自动修正为已分配"
            elif (old_status == TaskStatus.ASSIGNED and task.status == TaskStatus.PENDING and task.assignee_id is None):
                reason = "数据一致性修正"
                comment = "任务无负责人但状态为已分配，自动修正为待分配"
            
            task_log.log_task_status_change(
                db=db,
                task=task,
                user_id=current_user.id,
                old_status=old_status,
                new_status=task.status,
                reason=reason,
                comment=comment
            )
            logger.info(f"已记录{reason}：task_id={task.id}, {old_status} -> {task.status}")
    except Exception as e:
        logger.error(f"记录任务状态变化日志失败：{e}")
    
    # 记录分配变化日志
    try:
        if 'assignee_id' in update_data and old_assignee_id != task.assignee_id:
            task_log.log_task_assignment(
                db=db,
                task=task,
                user_id=current_user.id,
                old_assignee_id=old_assignee_id,
                new_assignee_id=task.assignee_id
            )
            logger.info(f"已记录任务分配变化：task_id={task.id}, {old_assignee_id} -> {task.assignee_id}")
    except Exception as e:
        logger.error(f"记录任务分配变化日志失败：{str(e)}")
    
    # 记录其他更新日志
    try:
        if len(update_data) > 0:
            changes = {k: v for k, v in update_data.items() if k not in ['status', 'assignee_id']}
            if changes:
                task_log.log_task_update(
                    db=db,
                    task=task,
                    user_id=current_user.id,
                    changes=changes,
                    description="更新了任务信息"
                )
                logger.info(f"已记录任务更新日志：task_id={task.id}")
    except Exception as e:
        logger.error(f"记录任务更新日志失败：{str(e)}")
    
    # 发送状态变更通知
    try:
        logger.info(f"检查是否需要发送状态变更通知：old_status={old_status}, new_status={task.status}, 是否相等={old_status == task.status}")
        if old_status != task.status:
            logger.info(f"状态发生变化，准备发送通知：{old_status.value} -> {task.status.value}")
            # 直接发送通知，不使用后台线程
            from app.core.message_service import message_push_service
            import asyncio
            
            # 获取当前事件循环
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，使用call_soon_threadsafe
                    loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(
                            message_push_service.notify_task_status_changed(
                                db, task, old_status.value, task.status.value, current_user.id
                            )
                        )
                    )
                else:
                    # 如果事件循环没有运行，直接运行
                    loop.run_until_complete(
                        message_push_service.notify_task_status_changed(
                            db, task, old_status.value, task.status.value, current_user.id
                        )
                    )
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_task_status_changed(
                        db, task, old_status.value, task.status.value, current_user.id
                    )
                )
            finally:
                loop.close()
            
            logger.info(f"已发送状态变更通知：{old_status.value} -> {task.status.value}")
        else:
            logger.info("状态没有发生变化，不发送通知")
    except Exception as e:
        logger.error(f"发送任务状态变更通知失败: {e}")
        # 不影响任务更新，只记录错误
    
    return task

@router.post("/{task_id}/assign")
def assign_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    assignee_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """分配任务给指定用户"""
    logger.info(f"开始分配任务：task_id={task_id}, assignee_id={assignee_id}")
    
    # 获取任务
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查当前用户是否有权限分配任务（必须是团队成员）
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 检查指定的负责人是否是团队成员
    assignee_member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == assignee_id
    ).first()
    if not assignee_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定的负责人不是团队成员"
        )
    
    # 更新任务
    old_assignee_id = task.assignee_id
    old_status = task.status
    
    task.assignee_id = assignee_id
    # 如果任务当前是待分配状态，自动改为已分配状态
    if task.status == TaskStatus.PENDING:
        task.status = TaskStatus.ASSIGNED
        logger.info(f"任务状态从待分配改为已分配：task_id={task_id}")
    
    db.commit()
    db.refresh(task)
    
    # 记录任务分配日志
    try:
        task_log.log_task_assignment(db, task, current_user.id, old_assignee_id, assignee_id)
        if old_status != task.status:
            task_log.log_task_status_change(db, task, current_user.id, old_status, task.status)
        logger.info(f"已记录任务分配日志：task_id={task_id}")
    except Exception as e:
        logger.error(f"记录任务分配日志失败：{str(e)}")
    
    # 发送任务分配通知
    try:
        logger.info(f"准备发送任务分配通知：task_id={task_id}, assignee_id={assignee_id}")
        # 直接发送通知，不使用后台线程
        from app.core.message_service import message_push_service
        import asyncio

        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_task_assigned(db, task, assignee_id, current_user.id)
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_task_assigned(db, task, assignee_id, current_user.id)
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_task_assigned(db, task, assignee_id, current_user.id)
                )
            finally:
                loop.close()

        logger.info(f"已发送任务分配通知：assignee_id={assignee_id}")
    except Exception as e:
        logger.error(f"发送任务分配通知失败: {e}")
        # 不影响任务分配，只记录错误
    
    return TaskResponse.from_orm(task)

@router.delete("/{task_id}")
def delete_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """删除任务（软删除）"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队管理员或任务创建者
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    can_delete = (
        task.creator_id == current_user.id or
        member.role == TEAM_ADMIN
    )
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限删除此任务"
        )
    
    # 软删除
    task.is_deleted = True
    db.add(task)
    db.commit()
    
    return {"message": "任务删除成功"}

# 任务评论接口
@router.post("/{task_id}/comments", response_model=TaskCommentResponse)
def create_task_comment(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    comment_in: TaskCommentBase,
    current_user: User = Depends(get_current_user)
) -> Any:
    """创建任务评论"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 创建评论
    comment = TaskComment(
        task_id=task_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # 发送任务评论通知
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
                        message_push_service.notify_task_comment_added(db, task, comment.id, current_user.id)
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_task_comment_added(db, task, comment.id, current_user.id)
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_task_comment_added(db, task, comment.id, current_user.id)
                )
            finally:
                loop.close()
        
        logger.info(f"已发送任务评论通知：comment_id={comment.id}")
    except Exception as e:
        logger.error(f"发送任务评论通知失败: {e}")
        # 不影响评论创建，只记录错误
    
    return comment

@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
def get_task_comments(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取任务评论列表"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).order_by(TaskComment.created_at.desc()).all()
    return comments

# 任务日志接口
@router.get("/{task_id}/logs")
def get_task_logs(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
) -> Any:
    """获取任务操作日志"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 获取任务日志
    logs = task_log.get_task_logs(db, task_id, limit, offset)
    return {"logs": logs, "total": len(logs)}

@router.get("/{task_id}/status-changes")
def get_task_status_changes(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
) -> Any:
    """获取任务状态变化历史"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 获取状态变化历史
    changes = task_log.get_task_status_changes(db, task_id, limit, offset)
    return {"status_changes": changes, "total": len(changes)}

@router.get("/{task_id}/activity")
def get_task_activity_logs(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
) -> Any:
    """获取任务完整活动日志"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 获取完整活动日志
    activities = task_log.get_task_activity_logs(db, task_id, limit, offset)
    return {"activities": activities, "total": len(activities)}

# 任务认领接口
@router.post("/{task_id}/claim")
def claim_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """认领任务"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能认领待分派的任务"
        )
    
    # 检查是否已被认领
    if task.assignee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务已被认领"
        )
    
    # 认领任务
    task.assignee_id = current_user.id
    task.status = TaskStatus.ASSIGNED
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 记录认领日志
    try:
        task_log.log_task_claim(
            db=db,
            task=task,
            user_id=current_user.id
        )
    except Exception as e:
        logger.error(f"记录任务认领日志失败：{str(e)}")
    
    # 转换为响应模型
    from app.schemas.task import TaskResponse
    # 确保加载关联数据
    db.refresh(task)
    task_response = TaskResponse.model_validate(task)
    
    return {"message": "任务认领成功", "task": task_response}

# 开始工作接口
@router.post("/{task_id}/start")
def start_task_work(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """开始任务工作"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限
    can_work = task.assignee_id == current_user.id
    if not can_work:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该任务的负责人"
        )
    
    # 检查任务状态
    if task.status not in [TaskStatus.ASSIGNED, TaskStatus.PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务状态不允许开始工作"
        )
    
    # 开始工作
    old_status = task.status
    task.status = TaskStatus.IN_PROGRESS
    task.started_at = func.now()
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 记录开始工作日志
    try:
        task_log.log_task_start(
            db=db,
            task=task,
            user_id=current_user.id
        )
        
        # 自动创建工作日志记录
        work_log = WorkLog(
            user_id=current_user.id,
            team_id=task.team_id,
            project_id=task.project_id,
            task_id=task.id,
            work_type=WorkLogType.DEVELOPMENT,  # 默认开发类型
            description=f"开始执行任务：{task.title}",
            details=f"任务状态从「{old_status}」变更为「{task.status}」",
            date=datetime.now(),
            start_time=task.started_at,
            end_time=None,  # 开始工作时结束时间为空，完成任务时再设置
            hours_spent=0.0,
            progress_percentage=0.0,
            work_status="in_progress"
        )
        
        db.add(work_log)
        db.commit()
        
    except Exception as e:
        logger.error(f"记录任务开始工作日志失败：{str(e)}")
    
    # 转换为响应模型
    from app.schemas.task import TaskResponse
    # 确保加载关联数据
    db.refresh(task)
    task_response = TaskResponse.model_validate(task)
    
    return {"message": "任务工作已开始", "task": task_response}

# 提交审核接口
@router.post("/{task_id}/submit-review")
def submit_task_for_review(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """提交任务审核"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限
    can_submit = task.assignee_id == current_user.id
    if not can_submit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该任务的负责人"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有进行中的任务可以提交审核"
        )
    
    # 提交审核
    task.status = TaskStatus.REVIEW
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 记录提交审核日志
    try:
        task_log.log_task_submit_review(
            db=db,
            task=task,
            user_id=current_user.id
        )
    except Exception as e:
        logger.error(f"记录任务提交审核日志失败：{str(e)}")
    
    # 转换为响应模型
    from app.schemas.task import TaskResponse
    # 确保加载关联数据
    db.refresh(task)
    task_response = TaskResponse.model_validate(task)
    
    return {"message": "任务已提交审核", "task": task_response}

# 审核通过接口
@router.post("/{task_id}/approve")
def approve_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """审核通过任务"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限（团队管理员或任务创建者）
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    can_approve = (
        member.role == TEAM_ADMIN or
        task.creator_id == current_user.id
    )
    if not can_approve:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限审核此任务"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待审核的任务可以审核通过"
        )
    
    # 审核通过
    task.status = TaskStatus.COMPLETED
    task.completed_at = func.now()
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 记录审核通过日志
    try:
        task_log.log_task_approve(
            db=db,
            task=task,
            user_id=current_user.id
        )
    except Exception as e:
        logger.error(f"记录任务审核通过日志失败：{str(e)}")
    
    # 转换为响应模型
    from app.schemas.task import TaskResponse
    # 确保加载关联数据
    db.refresh(task)
    task_response = TaskResponse.model_validate(task)
    
    return {"message": "任务审核通过", "task": task_response}

# 审核拒绝接口
@router.post("/{task_id}/reject")
def reject_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    reason: str = Form(..., description="拒绝原因"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """审核拒绝任务"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限（团队管理员或任务创建者）
    member = db.query(TeamMember).filter(
        TeamMember.team_id == task.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    can_reject = (
        member.role == TEAM_ADMIN or
        task.creator_id == current_user.id
    )
    if not can_reject:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限审核此任务"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待审核的任务可以审核拒绝"
        )
    
    # 审核拒绝，回到进行中状态
    task.status = TaskStatus.IN_PROGRESS
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 记录审核拒绝日志
    try:
        task_log.log_task_reject(
            db=db,
            task=task,
            user_id=current_user.id,
            reason=reason
        )
    except Exception as e:
        logger.error(f"记录任务审核拒绝日志失败：{str(e)}")
    
    # 转换为响应模型
    from app.schemas.task import TaskResponse
    # 确保加载关联数据
    db.refresh(task)
    task_response = TaskResponse.model_validate(task)
    
    return {"message": "任务审核拒绝", "task": task_response}

# 完成任务接口
@router.post("/{task_id}/complete")
def complete_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """完成任务"""
    # 检查任务是否存在
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查用户权限
    can_complete = task.assignee_id == current_user.id
    if not can_complete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该任务的负责人"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有进行中的任务才能完成"
        )
    
    # 完成任务
    old_status = task.status
    task.status = TaskStatus.COMPLETED
    task.completed_at = func.now()
    
    # 先提交以获取实际的时间值
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 计算实际工时
    if task.started_at is not None and task.completed_at is not None:
        duration = (task.completed_at - task.started_at).total_seconds() / 3600
        task.actual_hours = duration
        db.add(task)
        db.commit()
        db.refresh(task)
    
    # 记录完成工作日志
    try:
        # 更新之前的工作日志
        from app.models.work_log import WorkLog
        from datetime import datetime
        
        # 查找该任务的最新工作日志
        latest_work_log = db.query(WorkLog).filter(
            WorkLog.task_id == task.id,
            WorkLog.user_id == current_user.id
        ).order_by(WorkLog.created_at.desc()).first()
        
        if latest_work_log:
            # 更新现有工作日志
            latest_work_log.end_time = task.completed_at
            latest_work_log.hours_spent = task.actual_hours
            latest_work_log.progress_percentage = 100.0
            latest_work_log.work_status = "completed"
            latest_work_log.details = f"任务已完成，实际工时：{task.actual_hours:.1f}小时"
            db.add(latest_work_log)
        else:
            # 创建新的完成日志
            work_log = WorkLog(
                user_id=current_user.id,
                team_id=task.team_id,
                project_id=task.project_id,
                task_id=task.id,
                work_type=WorkLogType.DEVELOPMENT,
                description=f"完成任务：{task.title}",
                details=f"任务状态从「{old_status}」变更为「{task.status}」，实际工时：{task.actual_hours:.1f}小时",
                date=datetime.now(),
                start_time=task.started_at or task.completed_at,
                end_time=task.completed_at,
                hours_spent=task.actual_hours,
                progress_percentage=100.0,
                work_status="completed"
            )
            db.add(work_log)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"记录任务完成工作日志失败：{str(e)}")
    
    # 转换为响应模型
    from app.schemas.task import TaskResponse
    # 确保加载关联数据
    db.refresh(task)
    task_response = TaskResponse.model_validate(task)
    
    # 发送任务完成通知
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
                        message_push_service.notify_task_completed(db, task, current_user.id)
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_task_completed(db, task, current_user.id)
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_task_completed(db, task, current_user.id)
                )
            finally:
                loop.close()
        
        logger.info(f"已发送任务完成通知：task_id={task.id}")
    except Exception as e:
        logger.error(f"发送任务完成通知失败: {e}")
        # 不影响任务完成，只记录错误
    
    return {"message": "任务已完成", "task": task_response} 
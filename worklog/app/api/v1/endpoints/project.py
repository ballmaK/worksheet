from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.crud import project as project_crud
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.models.user import User
from app.models.team_member import TeamMember
from app.core.message_service import message_push_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=ProjectResponse)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user)
) -> ProjectResponse:
    """
    创建项目
    """
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == project_in.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队的成员，无法创建项目"
        )
    
    project = project_crud.create_project(db=db, project_in=project_in, creator_id=current_user.id)
    
    # 发送项目创建通知
    try:
        # 使用后台任务发送通知，避免阻塞
        import threading
        
        def send_project_notification():
            try:
                import asyncio
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(message_push_service.notify_project_created(db, project))
                loop.close()
            except Exception as e:
                logger.error(f"后台发送项目创建通知失败: {e}")
        
        # 在后台线程中执行
        thread = threading.Thread(target=send_project_notification)
        thread.daemon = True
        thread.start()
        logger.info(f"已启动后台任务发送项目创建通知：project_id={project.id}")
    except Exception as e:
        logger.error(f"发送项目创建通知失败: {e}")
        # 不影响项目创建，只记录错误
    
    return project

@router.get("")
def get_projects(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: Optional[int] = None,
    member_id: Optional[int] = None
):
    """
    获取项目列表，可选按团队或成员过滤
    """
    # 如果指定了member_id，检查权限
    if member_id and member_id != current_user.id:
        # 这里可以添加管理员权限检查
        pass
    
    projects = project_crud.get_projects(db=db, team_id=team_id, member_id=member_id or current_user.id)
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user)
) -> ProjectResponse:
    """
    获取项目详情
    """
    project = project_crud.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否有权限查看项目
    member = db.query(TeamMember).filter(
        TeamMember.team_id == project.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看该项目"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user)
) -> ProjectResponse:
    """
    更新项目
    """
    project = project_crud.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否有权限编辑项目
    if project.creator_id != current_user.id:
        # 检查是否是团队管理员
        member = db.query(TeamMember).filter(
            TeamMember.team_id == project.team_id,
            TeamMember.user_id == current_user.id,
            TeamMember.role == "team_admin"
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限编辑该项目"
            )
    
    project = project_crud.update_project(db=db, project=project, project_in=project_in)
    return project

@router.delete("/{project_id}")
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    删除项目
    """
    project = project_crud.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查用户是否有权限删除项目
    if project.creator_id != current_user.id:
        # 检查是否是团队管理员
        member = db.query(TeamMember).filter(
            TeamMember.team_id == project.team_id,
            TeamMember.user_id == current_user.id,
            TeamMember.role == "team_admin"
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限删除该项目"
            )
    
    project_crud.delete_project(db=db, project_id=project_id)
    return {"message": "项目已删除"} 
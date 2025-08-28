from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.team_member import TeamMember
from app.models.task import Task
from app.models.work_log import WorkLog

def create_project(db: Session, project_in: ProjectCreate, creator_id: int) -> Project:
    project = Project(
        team_id=project_in.team_id,
        name=project_in.name,
        description=project_in.description,
        status=project_in.status,
        start_date=project_in.start_date,
        end_date=project_in.end_date,
        progress=project_in.progress,
        creator_id=creator_id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).options(
        joinedload(Project.team),
        joinedload(Project.creator)
    ).filter(Project.id == project_id).first()

def get_projects(
    db: Session,
    team_id: Optional[int] = None,
    member_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    query = db.query(Project).options(
        joinedload(Project.team),
        joinedload(Project.creator)
    )
    
    if team_id:
        query = query.filter(Project.team_id == team_id)
    if member_id:
        team_ids = db.query(TeamMember.team_id).filter(TeamMember.user_id == member_id)
        query = query.filter(Project.team_id.in_(team_ids))
    
    projects = query.order_by(Project.created_at.desc()).all()
    
    # 转换为字典并添加统计信息
    result = []
    for project in projects:
        # 任务数量
        task_count = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id,
            Task.is_deleted == False
        ).scalar()
        
        # 成员数量（通过团队成员计算）
        member_count = db.query(func.count(TeamMember.id)).filter(
            TeamMember.team_id == project.team_id
        ).scalar()
        
        # 工作日志数量
        worklog_count = db.query(func.count(WorkLog.id)).filter(
            WorkLog.project_id == project.id
        ).scalar()
        
        # 转换为字典
        project_dict = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'team_id': project.team_id,
            'creator_id': project.creator_id,
            'status': project.status.value if hasattr(project.status, 'value') else str(project.status),
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'end_date': project.end_date.isoformat() if project.end_date else None,
            'progress': project.progress,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'team_name': project.team.name if project.team else "",
            'creator_name': project.creator.username if project.creator else "",
            'task_count': task_count,
            'member_count': member_count,
            'worklog_count': worklog_count
        }
        result.append(project_dict)
    
    return result

def update_project(
    db: Session,
    project: Project,
    project_in: ProjectUpdate
) -> Project:
    for field, value in project_in.dict(exclude_unset=True).items():
        setattr(project, field, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, project_id: int) -> None:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit() 
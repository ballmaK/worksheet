from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.enums import TEAM_ADMIN, TEAM_MEMBER
from app.schemas.team import TeamCreate, TeamUpdate
from datetime import datetime

def get_team(db: Session, team_id: int) -> Optional[Team]:
    return db.query(Team).filter(Team.id == team_id).first()

def get_teams(db: Session, skip: int = 0, limit: int = 100) -> List[Team]:
    return db.query(Team).offset(skip).limit(limit).all()

def create_team(db: Session, team: TeamCreate, owner_id: int) -> Team:
    """创建新团队，并将创建者设置为团队管理员"""
    db_team = Team(
        name=team.name,
        description=team.description,
        owner_id=owner_id
    )
    db.add(db_team)
    db.flush()  # 获取团队ID
    
    # 添加创建者为团队管理员
    team_member = TeamMember(
        team_id=db_team.id,
        user_id=owner_id,
        role=TEAM_ADMIN,
        joined_at=datetime.utcnow()
    )
    db.add(team_member)
    
    db.commit()
    db.refresh(db_team)
    return db_team

def update_team(db: Session, team_id: int, team: TeamUpdate) -> Optional[Team]:
    db_team = get_team(db, team_id)
    if db_team:
        update_data = team.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_team, field, value)
        db.commit()
        db.refresh(db_team)
    return db_team

def delete_team(db: Session, team_id: int) -> bool:
    db_team = get_team(db, team_id)
    if db_team:
        db.delete(db_team)
        db.commit()
        return True
    return False

def is_team_admin(db: Session, team_id: int, user_id: int) -> bool:
    """检查用户是否是团队管理员"""
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
        TeamMember.role == TEAM_ADMIN
    ).first()
    return member is not None 
from datetime import datetime
from sqlalchemy.orm import Session
from worklog.models.team_member import TeamMember

def add_team_member(db: Session, team_id: int, user_id: int, role: str) -> TeamMember:
    """添加团队成员"""
    # 检查用户是否已经是团队成员
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if existing_member:
        raise ValueError("用户已经是团队成员")
    
    # 创建新成员
    member = TeamMember(
        team_id=team_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.utcnow()
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    return member 
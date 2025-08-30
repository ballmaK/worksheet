from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.team_activity import TeamActivity
from app.schemas.team_activity import TeamActivityCreate, TeamActivityUpdate

def create_team_activity(db: Session, *, obj_in: TeamActivityCreate) -> TeamActivity:
    """创建团队活动"""
    db_obj = TeamActivity(
        team_id=obj_in.team_id,
        user_id=obj_in.user_id,
        activity_type=obj_in.activity_type,
        title=obj_in.title,
        content=obj_in.content,
        activity_metadata=obj_in.activity_metadata
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_team_activities(
    db: Session, 
    *, 
    team_id: int,
    skip: int = 0,
    limit: int = 100,
    activity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[TeamActivity]:
    """获取团队活动列表"""
    query = db.query(TeamActivity).filter(TeamActivity.team_id == team_id)
    
    if activity_type:
        query = query.filter(TeamActivity.activity_type == activity_type)
    
    if start_date:
        query = query.filter(TeamActivity.created_at >= start_date)
    
    if end_date:
        query = query.filter(TeamActivity.created_at <= end_date)
    
    return query.order_by(desc(TeamActivity.created_at)).offset(skip).limit(limit).all()

def get_team_activity(db: Session, *, id: int) -> Optional[TeamActivity]:
    """根据ID获取团队活动"""
    return db.query(TeamActivity).filter(TeamActivity.id == id).first()

def update_team_activity(
    db: Session, *, db_obj: TeamActivity, obj_in: TeamActivityUpdate
) -> TeamActivity:
    """更新团队活动"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_team_activity(db: Session, *, id: int) -> TeamActivity:
    """删除团队活动"""
    obj = db.query(TeamActivity).get(id)
    db.delete(obj)
    db.commit()
    return obj

def create_activity_log(
    db: Session,
    *,
    team_id: int,
    user_id: int,
    activity_type: str,
    title: str,
    content: Optional[str] = None,
    activity_metadata: Optional[Dict[str, Any]] = None
) -> TeamActivity:
    """创建活动日志的便捷方法"""
    activity_data = TeamActivityCreate(
        team_id=team_id,
        user_id=user_id,
        activity_type=activity_type,
        title=title,
        content=content,
        activity_metadata=activity_metadata
    )
    return create_team_activity(db, obj_in=activity_data)

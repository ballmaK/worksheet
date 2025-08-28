from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.work_log import WorkLog
from app.schemas.work_log import WorkLogCreate, WorkLogUpdate
from datetime import datetime

def create_worklog(db: Session, worklog_in: WorkLogCreate, user_id: int) -> WorkLog:
    worklog = WorkLog(
        user_id=user_id,
        team_id=worklog_in.team_id,
        project_id=worklog_in.project_id,
        title=worklog_in.title,
        content=worklog_in.content,
        start_time=worklog_in.start_time,
        end_time=worklog_in.end_time
    )
    db.add(worklog)
    db.commit()
    db.refresh(worklog)
    return worklog

def get_worklog(db: Session, worklog_id: int) -> Optional[WorkLog]:
    return db.query(WorkLog).filter(WorkLog.id == worklog_id).first()

def get_worklogs(
    db: Session,
    user_id: int,
    team_id: Optional[int] = None,
    project_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[WorkLog]:
    query = db.query(WorkLog).filter(WorkLog.user_id == user_id)
    
    if team_id:
        query = query.filter(WorkLog.team_id == team_id)
    if project_id:
        query = query.filter(WorkLog.project_id == project_id)
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(WorkLog.start_time >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(WorkLog.end_time <= end)
    
    return query.order_by(WorkLog.start_time.desc()).all()

def update_worklog(
    db: Session,
    worklog: WorkLog,
    worklog_in: WorkLogUpdate
) -> WorkLog:
    for field, value in worklog_in.dict(exclude_unset=True).items():
        setattr(worklog, field, value)
    db.add(worklog)
    db.commit()
    db.refresh(worklog)
    return worklog

def delete_worklog(db: Session, worklog_id: int) -> None:
    worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
    if worklog:
        db.delete(worklog)
        db.commit() 
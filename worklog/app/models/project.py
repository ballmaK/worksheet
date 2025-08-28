from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.enums import ProjectStatus

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.NOT_STARTED, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    progress = Column(Integer, default=0)  # 进度百分比 0-100
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 关联关系
    team = relationship("Team", back_populates="projects")
    creator = relationship("User", foreign_keys=[creator_id])
    worklogs = relationship("WorkLog", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan") 
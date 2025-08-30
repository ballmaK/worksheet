from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
from app.models.project import Project
from app.models.enums import TEAM_ADMIN, TEAM_MEMBER

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 修改关系定义
    team_members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    
    # 添加团队管理员关系
    admins = relationship(
        "User",
        secondary="team_members",
        primaryjoin="and_(Team.id==TeamMember.team_id, TeamMember.role=='team_admin')",
        viewonly=True
    )
    
    # 添加团队成员关系
    members = relationship(
        "User",
        secondary="team_members",
        viewonly=True
    )
    
    projects = relationship("Project", back_populates="team", cascade="all, delete-orphan")
    worklogs = relationship("WorkLog", back_populates="team", cascade="all, delete-orphan")
    invites = relationship("TeamInvite", back_populates="team", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="team", cascade="all, delete-orphan")
    


# 关联表定义放在模型之后
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class TeamActivity(Base):
    __tablename__ = "team_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # task_completed, member_joined, project_created, etc.
    title = Column(String(200), nullable=False)
    content = Column(Text)
    activity_metadata = Column(JSON)  # 存储活动相关的额外数据
    created_at = Column(DateTime, default=func.now())
    
    # 关系定义
    team = relationship("Team", back_populates="activities")
    user = relationship("User", back_populates="team_activities")

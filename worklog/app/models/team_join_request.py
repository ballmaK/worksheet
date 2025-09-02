from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class TeamJoinRequest(Base):
    __tablename__ = "team_join_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text)  # 申请留言
    status = Column(String(20), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    team = relationship("Team", back_populates="join_requests")
    user = relationship("User", back_populates="team_join_requests")

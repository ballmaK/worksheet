from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False, default="team_member")  # team_admin 或 team_member
    joined_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    team = relationship(
        "Team",
        back_populates="team_members"
    )
    user = relationship(
        "User",
        back_populates="team_memberships"
    )
    
    # 用户信息
    @property
    def username(self):
        return self.user.username if self.user else None
    
    @property
    def email(self):
        return self.user.email if self.user else None 
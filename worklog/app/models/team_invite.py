from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base
from app.models.user import User
from app.models.enums import TeamRole, InviteStatus

class TeamInvite(Base):
    __tablename__ = "team_invites"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    inviter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default=TeamRole.TEAM_MEMBER.value)
    token = Column(String(36), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False, default=InviteStatus.PENDING.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # 邀请过期时间

    # 关系
    team = relationship("Team", back_populates="invites")
    inviter = relationship("User", back_populates="sent_invites")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token:
            self.token = str(uuid.uuid4())
        if not self.expires_at:
            # 默认7天过期
            self.expires_at = datetime.utcnow() + timedelta(days=7) 
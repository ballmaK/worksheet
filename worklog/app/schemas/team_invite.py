from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.enums import TEAM_ADMIN, TEAM_MEMBER

class TeamInviteBase(BaseModel):
    email: EmailStr
    role: str = TEAM_MEMBER

class TeamInviteCreate(TeamInviteBase):
    pass

class TeamInviteUpdate(BaseModel):
    status: str

class TeamInviteInDB(TeamInviteBase):
    id: int
    team_id: int
    inviter_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TeamInviteResponse(TeamInviteInDB):
    inviter_name: str
    team_name: str 
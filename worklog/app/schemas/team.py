from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import TEAM_ADMIN, TEAM_MEMBER

from app.schemas.user import UserResponse

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class TeamInDB(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TeamResponse(TeamInDB):
    pass

# 新增：包含成员信息的团队详情响应
class TeamDetailResponse(TeamInDB):
    members: List['TeamMemberResponse'] = []

    class Config:
        from_attributes = True

class TeamMemberBase(BaseModel):
    role: str = TEAM_MEMBER

class TeamMemberCreate(TeamMemberBase):
    email: str

class TeamMemberUpdate(TeamMemberBase):
    pass

class TeamMemberInDB(TeamMemberBase):
    id: int
    team_id: int
    user_id: int
    joined_at: datetime

    class Config:
        from_attributes = True

class TeamMemberResponse(TeamMemberInDB):
    username: str
    email: str

    class Config:
        from_attributes = True

class TeamInviteBase(BaseModel):
    email: str
    role: str = TEAM_MEMBER

class TeamInviteCreate(TeamInviteBase):
    pass

class TeamInviteUpdate(BaseModel):
    status: str

class TeamInviteInDB(TeamInviteBase):
    id: int
    team_id: int
    inviter_id: int
    token: str
    status: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class TeamInviteResponse(TeamInviteInDB):
    pass 
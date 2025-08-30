from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class TeamActivityBase(BaseModel):
    activity_type: str
    title: str
    content: Optional[str] = None
    activity_metadata: Optional[Dict[str, Any]] = None

class TeamActivityCreate(TeamActivityBase):
    team_id: int
    user_id: int

class TeamActivityUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    activity_metadata: Optional[Dict[str, Any]] = None

class TeamActivityResponse(TeamActivityBase):
    id: int
    team_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamActivityInDB(TeamActivityResponse):
    pass

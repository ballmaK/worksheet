from typing import Optional
from pydantic import BaseModel, EmailStr, constr, validator, Field
from datetime import time

# 共享属性
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True

# 创建用户时的属性
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    team_id: Optional[int] = None
    invite_token: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        print(f"\n验证用户名: {v}")
        if not v.isalnum():
            print(f"用户名验证失败: 包含非字母数字字符")
            raise ValueError('用户名只能包含字母和数字')
        print(f"用户名验证通过")
        return v

    @validator('password')
    def validate_password(cls, v):
        print(f"\n验证密码: 长度={len(v)}")
        if len(v) < 6:
            print(f"密码验证失败: 长度不足6位")
            raise ValueError('密码长度必须至少为6个字符')
        print(f"密码验证通过")
        return v

    def dict(self, *args, **kwargs):
        print("\n调用 UserCreate.dict()")
        print(f"参数: args={args}, kwargs={kwargs}")
        result = super().dict(*args, **kwargs)
        print(f"返回结果: {result}")
        return result

# 更新用户时的属性
class UserUpdate(BaseModel):
    password: Optional[constr(min_length=8)] = None
    email: Optional[EmailStr] = None
    reminder_interval: Optional[int] = None
    work_hours_start: Optional[time] = None
    work_hours_end: Optional[time] = None
    notification_method: Optional[str] = None

# 数据库中的用户属性
class UserInDB(UserBase):
    id: int
    hashed_password: str
    role: str
    reminder_interval: int
    work_hours_start: time
    work_hours_end: time
    notification_method: str

    class Config:
        from_attributes = True

# 返回给API的用户属性
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Optional[str] = None
    reminder_interval: Optional[int] = None
    work_hours_start: Optional[time] = None
    work_hours_end: Optional[time] = None
    notification_method: Optional[str] = None

    class Config:
        from_attributes = True

# Token模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None 
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from sqlalchemy import func
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.team_member import TeamMember
from app.models.team_invite import TeamInvite
from app.models.enums import TEAM_ADMIN, TEAM_MEMBER
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserResponse, Token
from app.core import deps

router = APIRouter()

# 用户注册响应模型
class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    access_token: str
    token_type: str

@router.post("/register", response_model=UserRegisterResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    注册新用户
    """
    print("\n=== 开始用户注册流程 ===")
    print(f"原始请求参数:")
    print(f"调用 UserCreate.dict()")
    print(f"参数: args={user_in.__dict__.get('__args__', ())}, kwargs={user_in.__dict__.get('__kwargs__', {})}")
    print(f"返回结果: {user_in.dict()}")
    print(f"- user_in: {user_in.dict()}")
    
    print(f"\n请求参数:")
    print(f"- username: {user_in.username}")
    print(f"- email: {user_in.email}")
    print(f"- invite_token: {user_in.invite_token}")
    print(f"- password_length: {len(user_in.password)}")
    
    try:
        # 检查用户名是否已存在
        print("\n检查用户名是否已存在...")
        existing_user_by_username = db.query(User).filter(User.username == user_in.username).first()
        if existing_user_by_username:
            print(f"用户名已存在: {user_in.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        print("用户名检查通过")
    
        # 检查邮箱是否已存在（不区分大小写）
        print("\n检查邮箱是否已存在...")
        existing_user_by_email = db.query(User).filter(
            func.lower(User.email) == func.lower(user_in.email)
        ).first()
        if existing_user_by_email:
            print(f"邮箱已被注册: {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        print("邮箱检查通过")
    
        # 创建新用户
        print("\n开始创建用户对象...")
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
        )
        print(f"用户对象创建成功:")
        print(f"- id: {getattr(db_user, 'id', 'Not set')}")
        print(f"- username: {db_user.username}")
        print(f"- email: {db_user.email}")
        print(f"- hashed_password: {db_user.hashed_password[:10]}...")
        db.add(db_user)
        print("\n用户对象已添加到会话")
        db.flush()  # 获取用户ID但不提交事务
        print(f"用户ID生成: {db_user.id}")
        
        # 处理团队邀请
        if user_in.invite_token:
            print(f"\n处理团队邀请: invite_token={user_in.invite_token}")
            # 查找邀请记录
            invite = db.query(TeamInvite).filter(
                TeamInvite.token == user_in.invite_token,
                TeamInvite.email == user_in.email,
                TeamInvite.status == "pending",
                TeamInvite.expires_at > datetime.utcnow()
            ).first()
            if invite:
                print(f"找到邀请记录: invite_id={invite.id}, team_id={invite.team_id}, role={invite.role}")
                # 创建团队成员记录
                team_member = TeamMember(
                    team_id=invite.team_id,
                    user_id=db_user.id,
                    role=invite.role,
                    joined_at=datetime.utcnow()
                )
                db.add(team_member)
                print(f"创建团队成员记录: team_id={team_member.team_id}, user_id={team_member.user_id}, role={team_member.role}")
                # 更新邀请状态
                invite.status = "accepted"
                invite.updated_at = datetime.utcnow()
                db.add(invite)
                print(f"更新邀请状态为已接受: invite_id={invite.id}, status={invite.status}")
            else:
                print(f"未找到有效的邀请记录")
        
        # 提交事务
        print("\n开始提交事务...")
        db.commit()
        print("事务提交成功")
        db.refresh(db_user)
        print(f"用户注册成功: user_id={db_user.id}")
        print("=== 用户注册流程完成 ===\n")
        
        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": db_user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # 返回用户信息和令牌
        return {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException as he:
        # 直接重新抛出 HTTP 异常
        db.rollback()
        raise he
    except Exception as e:
        print("\n=== 注册过程发生错误 ===")
        print(f"错误类型: {type(e)}")
        print(f"错误信息: {str(e)}")
        import traceback
        print(f"错误堆栈:\n{traceback.format_exc()}")
        print("=== 错误信息结束 ===\n")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/token", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用户登录，支持使用用户名或邮箱登录
    """
    print("\n=== 开始用户登录流程 ===")
    print(f"登录请求参数:")
    print(f"- username: {form_data.username}")
    print(f"- password_length: {len(form_data.password)}")
    
    try:
        # 尝试使用用户名查找用户
        print("\n尝试使用用户名查找用户...")
        user = db.query(User).filter(User.username == form_data.username).first()
        
        # 如果用户名不存在，尝试使用邮箱查找
        if not user:
            print("用户名不存在，尝试使用邮箱查找...")
            user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user:
            print(f"用户不存在: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"找到用户: id={user.id}, username={user.username}, email={user.email}")
        
        # 验证密码
        print("\n开始验证密码...")
        if not verify_password(form_data.password, user.hashed_password):
            print(f"密码验证失败: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print("密码验证成功")
        
        # 创建访问令牌
        print("\n开始创建访问令牌...")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        print(f"访问令牌创建成功，过期时间: {access_token_expires}")
        
        print(f"\n登录成功: username={user.username}")
        print("=== 用户登录流程完成 ===\n")
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException as he:
        print(f"\n登录失败 (HTTP异常): {he.detail}")
        print("=== 用户登录流程失败 ===\n")
        raise he
    except Exception as e:
        print("\n=== 登录过程发生错误 ===")
        print(f"错误类型: {type(e)}")
        print(f"错误信息: {str(e)}")
        import traceback
        print(f"错误堆栈:\n{traceback.format_exc()}")
        print("=== 错误信息结束 ===\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取当前用户信息
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新当前用户信息
    """
    if user_in.password is not None:
        current_user.hashed_password = get_password_hash(user_in.password)
    if user_in.email is not None:
        current_user.email = user_in.email
    if user_in.reminder_interval is not None:
        current_user.reminder_interval = user_in.reminder_interval
    if user_in.work_hours_start is not None:
        current_user.work_hours_start = user_in.work_hours_start
    if user_in.work_hours_end is not None:
        current_user.work_hours_end = user_in.work_hours_end
    if user_in.notification_method is not None:
        current_user.notification_method = user_in.notification_method
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定用户信息（仅管理员）
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user 
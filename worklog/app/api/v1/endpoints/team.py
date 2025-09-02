from typing import Any, List, Dict, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from sqlalchemy import desc
from pydantic import BaseModel
import random
import asyncio

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.work_log import WorkLog
from app.models.team import Team
from app.models.team_member import TeamMember

from app.models.team_invite import TeamInvite
from app.models.project import Project
from app.models.enums import TEAM_ADMIN, TEAM_MEMBER
from app.core import deps
from app.schemas.work_log import WorkLogResponse
from app.schemas.team import (
    TeamBase, TeamCreate, TeamUpdate, TeamInDB, TeamResponse, TeamDetailResponse,
    TeamMemberBase, TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse,
    TeamInviteBase, TeamInviteCreate, TeamInviteResponse, TeamInviteUpdate
)


from app.core.email import send_invitation_email, send_invitation_verification_email

# 内联定义TeamProjectDetailResponse
class TeamProjectDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: str
    progress: int
    creator_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TeamWallResponse(BaseModel):
    items: List[WorkLogResponse]
    total: int
    page: int
    size: int
    pages: int

class WorkTypeStats(BaseModel):
    count: int
    total_duration: float

class UserWorkTypeStats(BaseModel):
    count: int
    total_duration: float

class UserStats(BaseModel):
    username: str
    count: int
    total_duration: float
    work_types: Dict[str, UserWorkTypeStats]

class TeamDailyReportResponse(BaseModel):
    date: date
    total_logs: int
    work_type_stats: Dict[str, WorkTypeStats]
    user_stats: Dict[int, UserStats]

# 验证邀请的请求模型
class VerifyInvitationRequest(BaseModel):
    email: str
    verification_code: str
    username: str = None  # 可选，如果用户不存在时需要提供
    password: str = None  # 可选，如果用户不存在时需要提供

# 验证邀请的响应模型
class VerifyInvitationResponse(BaseModel):
    message: str
    user_created: bool = False
    team_member_id: int = None

# 搜索团队的响应模型
class TeamSearchResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    member_count: int
    project_count: int
    is_public: bool = True  # 默认所有团队都是公开的

# 申请加入团队的请求模型
class JoinTeamRequest(BaseModel):
    message: Optional[str] = None  # 申请留言

# 申请加入团队的响应模型
class JoinTeamResponse(BaseModel):
    message: str
    application_id: Optional[int] = None

router = APIRouter()

# 团队管理接口
@router.post("", response_model=TeamResponse)
def create_team(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_in: TeamCreate
) -> Any:
    """
    创建新团队
    """
    print(f"开始创建团队: name={team_in.name}, description={team_in.description}")
    try:
        # 检查团队名是否已存在
        existing_team = db.query(Team).filter(Team.name == team_in.name).first()
        if existing_team:
            print(f"团队名称已存在: {team_in.name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="团队名称已存在"
            )

        # 创建团队
        team = Team(
            name=team_in.name,
            description=team_in.description
        )
        print(f"创建团队对象: id={team.id if hasattr(team, 'id') else 'None'}")
        db.add(team)
        db.flush()  # 获取团队ID
        print(f"团队ID生成: id={team.id}")
        
        # 添加创建者为团队管理员
        team_member = TeamMember(
            team_id=team.id,
            user_id=current_user.id,
            role=TEAM_ADMIN,
            joined_at=datetime.utcnow()
        )
        print(f"创建团队成员: team_id={team.id}, user_id={current_user.id}, role={TEAM_ADMIN}")
        db.add(team_member)
        
        try:
            print("开始提交事务...")
            db.commit()
            print("事务提交成功")
            
            # 重新查询团队，确保加载所有关系
            print("重新查询团队信息...")
            team = db.query(Team).filter(Team.id == team.id).first()
            if not team:
                print("错误：重新查询团队失败，未找到团队")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="创建团队后查询失败"
                )
            
            print(f"团队查询结果: id={team.id}, name={team.name}, members_count={len(team.team_members) if team.team_members else 0}")
            
            # 手动构建响应数据
            print("构建响应数据...")
            team_data = {
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "created_at": team.created_at,
                "updated_at": team.updated_at,
                "members": []
            }
            
            # 添加团队成员信息
            for member in team.team_members:
                member_data = {
                    "id": member.id,
                    "team_id": member.team_id,
                    "user_id": member.user_id,
                    "username": member.user.username,
                    "email": member.user.email,
                    "role": member.role,
                    "joined_at": member.joined_at
                }
                team_data["members"].append(member_data)
            
            print(f"响应数据构建完成: {team_data}")
            
            # 记录团队创建活动（暂时注释掉，因为不需要专门的活动记录）
            # try:
            #     # 这里可以记录团队创建活动到日志或数据库
            #     print(f"团队 {team.name} 创建成功")
            # except Exception as e:
            #     print(f"记录团队创建活动失败: {str(e)}")
            
            return TeamResponse(**team_data)
            
        except Exception as e:
            print(f"事务提交失败: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建团队失败: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建团队过程发生异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建团队失败: {str(e)}"
        )

@router.get("", response_model=List[TeamResponse])
def get_teams(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户所在的团队列表
    """
    # 使用join加载team_members关系
    teams = db.query(Team).join(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    # 确保每个团队都加载了team_members关系
    for team in teams:
        db.refresh(team)
        # 确保每个团队成员都有正确的角色
        for member in team.team_members:
            if member.role not in [TEAM_ADMIN, TEAM_MEMBER]:
                member.role = TEAM_MEMBER
    db.commit()
    
    # 转换为TeamResponse对象
    team_responses = []
    for team in teams:
        team_dict = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "members": [
                {
                    "id": member.id,
                    "team_id": member.team_id,
                    "user_id": member.user_id,
                    "username": member.user.username,
                    "email": member.user.email,
                    "role": member.role,
                    "joined_at": member.joined_at
                }
                for member in team.team_members
            ]
        }
        team_responses.append(TeamResponse(**team_dict))
    
    return team_responses

@router.get("/{team_id}", response_model=TeamDetailResponse)
def get_team(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int
) -> Any:
    """
    获取团队详情
    """
    # 使用joinedload预加载用户关系
    from sqlalchemy.orm import joinedload
    
    team = db.query(Team).options(
        joinedload(Team.team_members).joinedload(TeamMember.user)
    ).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    # 检查用户是否是团队成员
    if current_user not in [m.user for m in team.team_members]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 手动构建响应，包含成员信息
    team_data = {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
        "members": []
    }
    
    # 添加成员信息
    for team_member in team.team_members:
        if team_member.user:  # 确保用户关系已加载
            member_data = {
                "id": team_member.id,
                "team_id": team_member.team_id,
                "user_id": team_member.user_id,
                "role": team_member.role,
                "joined_at": team_member.joined_at,
                "username": team_member.user.username,
                "email": team_member.user.email
            }
            team_data["members"].append(member_data)
    
    return TeamDetailResponse(**team_data)

@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int,
    team_in: TeamUpdate
) -> Any:
    """
    更新团队信息
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    # 检查用户是否是团队管理员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role == TEAM_ADMIN
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是团队管理员"
        )
    # 更新团队信息
    team.name = team_in.name
    team.description = team_in.description
    db.add(team)
    db.commit()
    db.refresh(team)
    return TeamResponse.from_orm(team)

@router.post("/{team_id}/members", response_model=TeamMemberResponse)
def add_team_member(
    team_id: int,
    member: TeamMemberCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """添加团队成员"""
    # 检查团队是否存在
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    
    # 检查当前用户是否是团队管理员
    current_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not current_member or current_member.role != TEAM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队管理员可以添加成员"
        )
    
    # 检查用户是否已经是团队成员
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == member.user_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已经是团队成员"
        )
    
    # 创建新成员
    team_member = TeamMember(
        team_id=team_id,
        user_id=member.user_id,
        role=member.role,
        joined_at=datetime.utcnow()
    )
    
    db.add(team_member)
    db.commit()
    db.refresh(team_member)
    
    # 发送团队成员加入通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_team_member_joined(
                            db, team_id, member.user_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_team_member_joined(
                        db, team_id, member.user_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_team_member_joined(
                        db, team_id, member.user_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送团队成员加入通知：team_id={team_id}, user_id={member.user_id}")
    except Exception as e:
        print(f"发送团队成员加入通知失败: {e}")
        # 不影响成员加入流程，只记录错误
    
    # 记录成员加入活动（暂时注释掉，因为不需要专门的活动记录）
    # try:
    #     user = db.query(User).filter(User.id == member.user_id).first()
    #     print(f"用户 {user.username if user else '未知用户'} 加入团队成功")
    # except Exception as e:
    #     print(f"记录成员加入活动失败: {str(e)}")
    
    return team_member

@router.put("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
def update_member_role(
    team_id: int,
    member_id: int,
    role_update: TeamMemberUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """更新团队成员角色"""
    # 检查团队是否存在
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    
    # 检查当前用户是否是团队管理员
    current_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not current_member or current_member.role != TEAM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队管理员可以修改成员角色"
        )
    
    # 检查要修改的成员是否存在
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.id == member_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成员不存在"
        )
    
    # 不允许修改最后一个团队管理员的角色
    if member.role == TEAM_ADMIN:
        admin_count = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.role == TEAM_ADMIN
        ).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="团队必须至少保留一个管理员"
            )
    
    # 记录角色变更活动
    old_role = member.role
    user = db.query(User).filter(User.id == member.user_id).first()
    
    # 更新角色
    member.role = role_update.role
    db.commit()
    db.refresh(member)
    
    # 记录角色变更活动（暂时注释掉，因为不需要专门的活动记录）
    # try:
    #     print(f"用户 {user.username if user else '未知用户'} 角色从 {old_role} 变更为 {role_update.role}")
    # except Exception as e:
    #     print(f"记录角色变更活动失败: {str(e)}")
    
    return member

@router.delete("/{team_id}/members/{user_id}")
def remove_team_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int,
    user_id: int
) -> Any:
    """
    移除团队成员
    """
    # 检查团队是否存在
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    
    # 检查用户是否是团队管理员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role == TEAM_ADMIN
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是团队管理员"
        )
    
    # 检查要移除的用户是否是团队成员
    target_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不是团队成员"
        )
    
    # 移除团队成员
    db.delete(target_member)
    db.commit()
    
    # 发送团队成员离开通知
    try:
        from app.core.message_service import message_push_service
        import asyncio
        
        # 获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用call_soon_threadsafe
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        message_push_service.notify_team_member_left(
                            db, team_id, user_id
                        )
                    )
                )
            else:
                # 如果事件循环没有运行，直接运行
                loop.run_until_complete(
                    message_push_service.notify_team_member_left(
                        db, team_id, user_id
                    )
                )
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    message_push_service.notify_team_member_left(
                        db, team_id, user_id
                    )
                )
            finally:
                loop.close()
        
        print(f"已发送团队成员离开通知：team_id={team_id}, user_id={user_id}")
    except Exception as e:
        print(f"发送团队成员离开通知失败: {e}")
        # 不影响成员离开流程，只记录错误
    
    return {"message": "成员已从团队中移除"}

@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
def get_team_members(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int
) -> Any:
    """
    获取团队成员列表
    """
    from sqlalchemy.orm import joinedload
    
    # 使用joinedload预加载用户关系
    team = db.query(Team).options(
        joinedload(Team.team_members).joinedload(TeamMember.user)
    ).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    # 检查用户是否是团队成员
    if current_user.id not in [m.user_id for m in team.team_members]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 手动构建响应数据，确保包含用户信息
    members_response = []
    for member in team.team_members:
        if hasattr(member, 'user') and member.user:
            member_data = {
                "id": member.id,
                "team_id": member.team_id,
                "user_id": member.user_id,
                "username": member.user.username,
                "email": member.user.email,
                "role": member.role,
                "joined_at": member.joined_at
            }
            members_response.append(TeamMemberResponse(**member_data))
    
    return members_response

# 团队工作墙接口
@router.get("/team-wall", response_model=TeamWallResponse)
def get_team_wall(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    target_date: date = None,
    page: int = 1,
    size: int = 20
) -> Any:
    """
    获取团队工作墙
    - target_date: 目标日期，默认为今天
    - page: 页码，从1开始
    - size: 每页数量
    """
    if target_date is None:
        target_date = date.today()
    
    # 计算分页
    skip = (page - 1) * size
    
    # 查询当天的工作日志
    query = db.query(WorkLog).filter(
        WorkLog.created_at >= datetime.combine(target_date, datetime.min.time()),
        WorkLog.created_at <= datetime.combine(target_date, datetime.max.time())
    ).order_by(desc(WorkLog.created_at))
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    work_logs = query.offset(skip).limit(size).all()
    
    return {
        "items": work_logs,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/team-daily-report", response_model=TeamDailyReportResponse)
def get_team_daily_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    target_date: date = None
) -> Any:
    """
    获取团队日报
    - target_date: 目标日期，默认为今天
    """
    if target_date is None:
        target_date = date.today()
    
    # 查询当天的工作日志
    work_logs = db.query(WorkLog).filter(
        WorkLog.created_at >= datetime.combine(target_date, datetime.min.time()),
        WorkLog.created_at <= datetime.combine(target_date, datetime.max.time())
    ).all()
    
    # 按工作类型统计
    work_type_stats = {}
    for log in work_logs:
        if log.work_type not in work_type_stats:
            work_type_stats[log.work_type] = {
                "count": 0,
                "total_duration": 0
            }
        work_type_stats[log.work_type]["count"] += 1
        work_type_stats[log.work_type]["total_duration"] += log.duration
    
    # 按用户统计
    user_stats = {}
    for log in work_logs:
        if log.user_id not in user_stats:
            user_stats[log.user_id] = {
                "username": log.user.username,
                "count": 0,
                "total_duration": 0,
                "work_types": {}
            }
        user_stats[log.user_id]["count"] += 1
        user_stats[log.user_id]["total_duration"] += log.duration
        
        if log.work_type not in user_stats[log.user_id]["work_types"]:
            user_stats[log.user_id]["work_types"][log.work_type] = {
                "count": 0,
                "total_duration": 0
            }
        user_stats[log.user_id]["work_types"][log.work_type]["count"] += 1
        user_stats[log.user_id]["work_types"][log.work_type]["total_duration"] += log.duration
    
    return {
        "date": target_date,
        "total_logs": len(work_logs),
        "work_type_stats": work_type_stats,
        "user_stats": user_stats
    }

@router.post("/{team_id}/invite", response_model=Union[TeamMemberResponse, dict])
async def invite_team_member(
    team_id: int,
    invite_in: TeamInviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    邀请新成员加入团队（通过邮箱验证码）
    """
    print(f"开始邀请团队成员，团队ID: {team_id}, 当前用户ID: {current_user.id}")
    print(f"邀请请求数据: {invite_in.dict()}")
    
    # 检查用户是否是团队管理员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    print(f"检查用户 {current_user.id} 是否是团队 {team_id} 的管理员")
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    print(f"用户是团队成员，角色为: {member.role}")
    is_admin = member.role == TEAM_ADMIN
    print(f"用户是否是管理员: {is_admin}")
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队管理员可以邀请新成员"
        )
    
    # 检查团队是否存在
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    
    # 检查邮箱是否已存在用户
    print(f"正在查找邮箱为 {invite_in.email} 的用户")
    existing_user = db.query(User).filter(User.email == invite_in.email).first()
    
    if existing_user:
        # 检查用户是否已经是团队成员
        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == existing_user.id
        ).first()
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户已经是团队成员"
            )
        
        # 直接添加为团队成员
        team_member = TeamMember(
            team_id=team_id,
            user_id=existing_user.id,
            role=invite_in.role,
            joined_at=datetime.utcnow()
        )
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
        
        # 发送团队成员加入通知
        try:
            from app.core.message_service import message_push_service
            import asyncio
            
            # 获取当前事件循环
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，使用call_soon_threadsafe
                    loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(
                            message_push_service.notify_team_member_joined(
                                db, team_id, existing_user.id
                            )
                        )
                    )
                else:
                    # 如果事件循环没有运行，直接运行
                    loop.run_until_complete(
                        message_push_service.notify_team_member_joined(
                            db, team_id, existing_user.id
                        )
                    )
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        message_push_service.notify_team_member_joined(
                            db, team_id, existing_user.id
                        )
                    )
                finally:
                    loop.close()
                
                print(f"已发送团队成员加入通知：team_id={team_id}, user_id={existing_user.id}")
        except Exception as e:
            print(f"发送团队成员加入通知失败: {e}")
            # 不影响成员加入流程，只记录错误
        
        return TeamMemberResponse(
            id=team_member.id,
            team_id=team_member.team_id,
            user_id=team_member.user_id,
            username=existing_user.username,
            email=existing_user.email,
            role=team_member.role,
            joined_at=team_member.joined_at
        )
    else:
        print(f"未找到邮箱为 {invite_in.email} 的用户，发送验证码邀请邮件")
        
        # 检查是否有未过期的待处理邀请
        existing_invite = db.query(TeamInvite).filter(
            TeamInvite.team_id == team_id,
            TeamInvite.email == invite_in.email,
            TeamInvite.status == "pending",
            TeamInvite.expires_at > datetime.utcnow()
        ).first()
        
        if existing_invite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已有未过期的邀请，请等待邀请过期或重新发送"
            )
        
        try:
            # 生成6位数字验证码
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # 创建邀请记录
            team_invite = TeamInvite(
                team_id=team_id,
                inviter_id=current_user.id,
                email=invite_in.email,
                role=invite_in.role,
                token=verification_code,  # 使用验证码作为token
                status="pending",
                expires_at=datetime.utcnow() + timedelta(minutes=10)  # 10分钟后过期
            )
            db.add(team_invite)
            db.commit()
            db.refresh(team_invite)
            
            # 发送验证码邮件
            print(f"\n=== 邀请验证码邮件信息 ===")
            print(f"收件人: {invite_in.email}")
            print(f"团队名称: {team.name}")
            print(f"邀请人: {current_user.username}")
            print(f"验证码: {verification_code}")
            print(f"过期时间: {team_invite.expires_at}")
            print(f"===================\n")
            
            # 使用异步方式发送邮件
            await send_invitation_verification_email(
                email_to=invite_in.email,
                team_name=team.name,
                inviter_name=current_user.username,
                verification_code=verification_code
            )
            
            # 发送团队邀请通知
            try:
                from app.core.message_service import message_push_service
                import asyncio
                
                # 获取当前事件循环
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果事件循环正在运行，使用call_soon_threadsafe
                        loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(
                                message_push_service.notify_team_invitation(
                                    db, team_id, current_user.id, existing_user.id if existing_user else 0
                                )
                            )
                        )
                    else:
                        # 如果事件循环没有运行，直接运行
                        loop.run_until_complete(
                            message_push_service.notify_team_invitation(
                                db, team_id, current_user.id, existing_user.id if existing_user else 0
                            )
                        )
                except RuntimeError:
                    # 如果没有事件循环，创建一个新的
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            message_push_service.notify_team_invitation(
                                db, team_id, current_user.id, existing_user.id if existing_user else 0
                            )
                        )
                    finally:
                        loop.close()
                    
                    print(f"已发送团队邀请通知：team_id={team_id}")
            except Exception as e:
                print(f"发送团队邀请通知失败: {e}")
                # 不影响邀请流程，只记录错误
            
            return {
                "message": "邀请验证码已发送",
                "invite_id": team_invite.id
            }
        except Exception as e:
            db.rollback()
            print(f"发送验证码邮件失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"发送邀请失败: {str(e)}"
            )

@router.get("/{team_id}/invites", response_model=List[TeamInviteResponse])
async def get_team_invites(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取团队的邀请记录
    """
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    # 获取所有邀请记录（包括待处理和已处理的）
    invites = db.query(TeamInvite).filter(
        TeamInvite.team_id == team_id
    ).order_by(TeamInvite.created_at.desc()).all()
    
    # 转换为响应格式
    invite_responses = []
    for invite in invites:
        # 获取邀请人信息
        inviter = db.query(User).filter(User.id == invite.inviter_id).first()
        inviter_name = inviter.username if inviter else "未知用户"
        
        # 获取团队信息
        team = db.query(Team).filter(Team.id == invite.team_id).first()
        team_name = team.name if team else "未知团队"
        
        invite_responses.append(TeamInviteResponse(
            id=invite.id,
            team_id=invite.team_id,
            inviter_id=invite.inviter_id,
            email=invite.email,
            role=invite.role,
            status=invite.status,
            token=invite.token,
            created_at=invite.created_at,
            updated_at=invite.updated_at,
            expires_at=invite.expires_at
        ))
    
    return invite_responses

@router.delete("/{team_id}")
def delete_team(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int
) -> Any:
    """
    删除团队
    """
    print(f"开始删除团队: team_id={team_id}")
    try:
        # 查询团队
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            print(f"团队不存在: team_id={team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="团队不存在"
            )

        # 检查用户是否是团队管理员
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id,
            TeamMember.role == TEAM_ADMIN
        ).first()
        
        if not member:
            print(f"用户不是团队管理员: user_id={current_user.id}, team_id={team_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有团队管理员可以删除团队"
            )

        try:
            print("开始删除团队...")
            db.delete(team)
            db.commit()
            print(f"团队删除成功: team_id={team_id}")
            return {"message": "团队删除成功"}
        except Exception as e:
            print(f"删除团队失败: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除团队失败: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除团队过程发生异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除团队失败: {str(e)}"
        )

@router.post("/invite/verify", response_model=VerifyInvitationResponse)
def verify_invitation(
    *,
    db: Session = Depends(get_db),
    verify_data: VerifyInvitationRequest = Body(...)
) -> Any:
    """
    验证邀请码并加入团队
    """
    # 查找邀请记录
    invite = db.query(TeamInvite).filter(
        TeamInvite.email == verify_data.email,
        TeamInvite.token == verify_data.verification_code,
        TeamInvite.status == "pending"
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请不存在或验证码错误"
        )
    
    # 检查邀请是否过期
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        invite.status = "expired"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请已过期"
        )
    
    # 检查邮箱是否已存在用户
    existing_user = db.query(User).filter(User.email == verify_data.email).first()
    
    if existing_user:
        # 用户已存在，直接加入团队
        # 检查用户是否已经是团队成员
        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == invite.team_id,
            TeamMember.user_id == existing_user.id
        ).first()
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经是该团队成员"
            )
        
        # 创建团队成员记录
        team_member = TeamMember(
            team_id=invite.team_id,
            user_id=existing_user.id,
            role=invite.role,
            joined_at=datetime.utcnow()
        )
        
        # 更新邀请状态
        invite.status = "accepted"
        
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
        
        return VerifyInvitationResponse(
            message="邀请验证成功，已加入团队",
            user_created=False,
            team_member_id=team_member.id
        )
    else:
        # 用户不存在，需要创建新用户
        if not verify_data.username or not verify_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在，请提供用户名和密码创建账户"
            )
        
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == verify_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在，请选择其他用户名"
            )
        
        # 创建新用户
        from app.core.security import get_password_hash
        hashed_password = get_password_hash(verify_data.password)
        
        new_user = User(
            username=verify_data.username,
            email=verify_data.email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(new_user)
        db.flush()  # 获取用户ID
        
        # 创建团队成员记录
        team_member = TeamMember(
            team_id=invite.team_id,
            user_id=new_user.id,
            role=invite.role,
            joined_at=datetime.utcnow()
        )
        
        # 更新邀请状态
        invite.status = "accepted"
        
        db.add(team_member)
        db.commit()
        db.refresh(team_member)
        
        return VerifyInvitationResponse(
            message="账户创建成功，已加入团队",
            user_created=True,
            team_member_id=team_member.id
        )

@router.post("/invite/{invite_id}/resend")
async def resend_invite(
    *,
    db: Session = Depends(get_db),
    invite_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    重新发送邀请验证码
    """
    # 查找邀请记录
    invite = db.query(TeamInvite).filter(TeamInvite.id == invite_id).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请不存在"
        )
    
    # 检查用户是否是团队管理员
    team_member = db.query(TeamMember).filter(
        TeamMember.team_id == invite.team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role == TEAM_ADMIN
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队管理员可以重新发送邀请"
        )
    
    # 检查邀请状态
    if invite.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能重新发送待处理的邀请"
        )
    
    # 重新生成验证码和过期时间
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    invite.token = verification_code
    invite.expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    # 重新发送验证码邮件
    try:
        team = db.query(Team).filter(Team.id == invite.team_id).first()
        inviter = db.query(User).filter(User.id == invite.inviter_id).first()
        
        # 使用异步方式发送邮件
        await send_invitation_verification_email(
            email_to=invite.email,
            team_name=team.name if team else "未知团队",
            inviter_name=inviter.username if inviter else "未知用户",
            verification_code=verification_code
        )
        
        return {"message": "验证码重新发送成功"}
    except Exception as e:
        print(f"重新发送验证码邮件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重新发送验证码失败"
        ) 

# 新增的API接口



@router.get("/{team_id}/projects", response_model=List[TeamProjectDetailResponse])
def get_team_projects(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    keyword: Optional[str] = None
) -> Any:
    """
    获取团队项目列表
    """
    # 检查用户是否是团队成员
    team_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队的成员"
        )
    
    # 直接查询团队的项目
    query = db.query(Project).filter(Project.team_id == team_id)
    
    # 应用过滤条件
    if status:
        query = query.filter(Project.status == status)
    
    if keyword:
        query = query.filter(
            Project.name.contains(keyword) | Project.description.contains(keyword)
        )
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    projects = query.order_by(desc(Project.created_at)).offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for project in projects:
        creator = db.query(User).filter(User.id == project.creator_id).first()
        result.append(TeamProjectDetailResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status.value if project.status else "unknown",
            progress=project.progress,
            creator_name=creator.username if creator else "未知用户",
            start_date=project.start_date,
            end_date=project.end_date,
            created_at=project.created_at
        ))
    
    return result

@router.get("/{team_id}/statistics")
def get_team_statistics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int
) -> Any:
    """
    获取团队统计信息
    """
    # 检查用户是否是团队成员
    team_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队的成员"
        )
    
    # 统计成员数量
    member_count = db.query(TeamMember).filter(
        TeamMember.team_id == team_id
    ).count()
    
    # 统计项目数量
    project_count = db.query(Project).filter(
        Project.team_id == team_id
    ).count()
    
    # 统计工作日志数量
    worklog_count = db.query(WorkLog).filter(
        WorkLog.team_id == team_id
    ).count()
    
    # 统计任务数量
    from app.models.task import Task
    task_count = db.query(Task).filter(
        Task.team_id == team_id
    ).count()
    
    return {
        "member_count": member_count,
        "project_count": project_count,
        "worklog_count": worklog_count,
        "task_count": task_count
    }

@router.get("/search/public", response_model=List[TeamSearchResponse])
def search_public_teams(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    keyword: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Any:
    """
    搜索公开的团队（模糊搜索）
    """
    # 计算偏移量
    skip = (page - 1) * size
    
    # 基础查询：获取所有团队
    query = db.query(Team)
    
    # 应用关键词搜索
    if keyword:
        query = query.filter(
            Team.name.contains(keyword) | Team.description.contains(keyword)
        )
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    teams = query.order_by(desc(Team.created_at)).offset(skip).limit(size).all()
    
    # 构建响应数据
    result = []
    for team in teams:
        # 统计成员数量
        member_count = db.query(TeamMember).filter(
            TeamMember.team_id == team.id
        ).count()
        
        # 统计项目数量
        project_count = db.query(Project).filter(
            Project.team_id == team.id
        ).count()
        
        # 检查当前用户是否已经是团队成员
        is_member = db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == current_user.id
        ).first() is not None
        
        # 如果用户已经是团队成员，跳过
        if is_member:
            continue
            
        result.append(TeamSearchResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            created_at=team.created_at,
            member_count=member_count,
            project_count=project_count,
            is_public=True
        ))
    
    return result

@router.post("/{team_id}/join", response_model=JoinTeamResponse)
def join_team(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int,
    join_request: JoinTeamRequest
) -> Any:
    """
    申请加入团队
    """
    # 检查团队是否存在
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    
    # 检查用户是否已经是团队成员
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经是该团队的成员"
        )
    
    # 检查是否已经有待处理的申请
    from app.models.team_join_request import TeamJoinRequest
    existing_request = db.query(TeamJoinRequest).filter(
        TeamJoinRequest.team_id == team_id,
        TeamJoinRequest.user_id == current_user.id,
        TeamJoinRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经提交过加入申请，请等待管理员审核"
        )
    
    # 创建加入申请
    join_request_obj = TeamJoinRequest(
        team_id=team_id,
        user_id=current_user.id,
        message=join_request.message,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(join_request_obj)
    db.commit()
    db.refresh(join_request_obj)
    
    # 发送通知给团队管理员
    team_admins = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.role == TEAM_ADMIN
    ).all()
    
    for admin in team_admins:
        # 这里可以发送邮件通知管理员
        # 暂时只记录日志
        print(f"用户 {current_user.username} 申请加入团队 {team.name}，管理员 {admin.user_id} 需要审核")
    
    return JoinTeamResponse(
        message="申请已提交，请等待管理员审核",
        application_id=join_request_obj.id
    )

@router.get("/{team_id}/join-requests", response_model=List[dict])
def get_team_join_requests(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int
) -> Any:
    """
    获取团队的加入申请列表（仅团队管理员可访问）
    """
    # 检查用户是否是团队管理员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not member or member.role != TEAM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队管理员可以查看加入申请"
        )
    
    # 获取所有加入申请
    from app.models.team_join_request import TeamJoinRequest
    join_requests = db.query(TeamJoinRequest).filter(
        TeamJoinRequest.team_id == team_id
    ).all()
    
    # 构建响应数据
    result = []
    for request in join_requests:
        user = db.query(User).filter(User.id == request.user_id).first()
        result.append({
            "id": request.id,
            "user_id": request.user_id,
            "username": user.username if user else "未知用户",
            "email": user.email if user else "未知邮箱",
            "message": request.message,
            "status": request.status,
            "created_at": request.created_at,
            "updated_at": request.updated_at
        })
    
    return result

@router.put("/{team_id}/join-requests/{request_id}/approve")
def approve_join_request(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int,
    request_id: int
) -> Any:
    """
    批准加入申请（仅团队管理员可操作）
    """
    # 检查用户是否是团队管理员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not member or member.role != TEAM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队管理员可以批准加入申请"
        )
    
    # 获取加入申请
    from app.models.team_join_request import TeamJoinRequest
    join_request = db.query(TeamJoinRequest).filter(
        TeamJoinRequest.id == request_id,
        TeamJoinRequest.team_id == team_id
    ).first()
    
    if not join_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="加入申请不存在"
        )
    
    if join_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该申请已经被处理"
        )
    
    # 批准申请
    join_request.status = "approved"
    join_request.updated_at = datetime.utcnow()
    
    # 将用户添加为团队成员
    new_member = TeamMember(
        team_id=team_id,
        user_id=join_request.user_id,
        role=TEAM_MEMBER,
        joined_at=datetime.utcnow()
    )
    
    db.add(new_member)
    db.commit()
    
    return {"message": "申请已批准，用户已加入团队"}

@router.put("/{team_id}/join-requests/{request_id}/reject")
def reject_join_request(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int,
    request_id: int
) -> Any:
    """
    拒绝加入申请（仅团队管理员可操作）
    """
    # 检查用户是否是团队管理员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not member or member.role != TEAM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队管理员可以拒绝加入申请"
        )
    
    # 获取加入申请
    from app.models.team_join_request import TeamJoinRequest
    join_request = db.query(TeamJoinRequest).filter(
        TeamJoinRequest.id == request_id,
        TeamJoinRequest.team_id == team_id
    ).first()
    
    if not join_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="加入申请不存在"
        )
    
    if join_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该申请已经被处理"
        )
    
    # 拒绝申请
    join_request.status = "rejected"
    join_request.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "申请已拒绝"}

@router.get("/{team_id}/activities")
def get_team_activities(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    team_id: int,
    skip: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    activity_type: Optional[str] = Query(None, description="活动类型"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
) -> Any:
    """
    获取团队活动列表（基于现有数据聚合）
    """
    # 检查团队是否存在
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队不存在"
        )
    
    # 检查用户是否是团队成员
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该团队成员"
        )
    
    activities = []
    
    # 获取团队成员加入活动
    team_members = db.query(TeamMember).filter(
        TeamMember.team_id == team_id
    ).order_by(desc(TeamMember.joined_at)).offset(skip).limit(limit).all()
    
    for member in team_members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user:
            activities.append({
                "id": f"member_{member.id}",
                "team_id": team_id,
                "user_id": member.user_id,
                "activity_type": "member_joined",
                "title": f"新成员加入：{user.username}",
                "content": f"用户 {user.username} 加入了团队",
                "metadata": {
                    "joined_user_id": member.user_id,
                    "joined_user_name": user.username,
                    "role": member.role
                },
                "created_at": member.joined_at,
                "user": {
                    "id": user.id,
                    "username": user.username
                }
            })
    
    # 获取团队项目创建活动
    projects = db.query(Project).filter(
        Project.team_id == team_id
    ).order_by(desc(Project.created_at)).offset(skip).limit(limit).all()
    
    for project in projects:
        creator = db.query(User).filter(User.id == project.creator_id).first()
        if creator:
            activities.append({
                "id": f"project_{project.id}",
                "team_id": team_id,
                "user_id": project.creator_id,
                "activity_type": "project_created",
                "title": f"创建了新项目：{project.name}",
                "content": f"项目描述：{project.description or '无描述'}",
                "metadata": {
                    "project_id": project.id,
                    "project_name": project.name,
                    "project_status": project.status
                },
                "created_at": project.created_at,
                "user": {
                    "id": creator.id,
                    "username": creator.username
                }
            })
    
    # 获取工作日志活动
    work_logs = db.query(WorkLog).filter(
        WorkLog.team_id == team_id
    ).order_by(desc(WorkLog.created_at)).offset(skip).limit(limit).all()
    
    for work_log in work_logs:
        user = db.query(User).filter(User.id == work_log.user_id).first()
        if user:
            activities.append({
                "id": f"worklog_{work_log.id}",
                "team_id": team_id,
                "user_id": work_log.user_id,
                "activity_type": "work_log_submitted",
                "title": f"{user.username} 提交了工作日志",
                "content": work_log.content[:100] + "..." if len(work_log.content) > 100 else work_log.content,
                "metadata": {
                    "worklog_id": work_log.id,
                    "work_type": work_log.work_type,
                    "duration": work_log.duration
                },
                "created_at": work_log.created_at,
                "user": {
                    "id": user.id,
                    "username": user.username
                }
            })
    
    # 按时间倒序排列
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    # 应用分页
    paginated_activities = activities[skip:skip + limit]
    
    return paginated_activities
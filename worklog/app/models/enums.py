from enum import Enum

# 团队成员角色
TEAM_ADMIN = "team_admin"
TEAM_MEMBER = "team_member"

class TeamRole(str, Enum):
    """团队角色枚举"""
    TEAM_ADMIN = "team_admin"  # 团队管理员
    TEAM_MEMBER = "team_member"  # 普通成员

class InviteStatus(str, Enum):
    """邀请状态枚举"""
    PENDING = "pending"  # 待接受
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期

class ProjectStatus(str, Enum):
    """项目状态枚举"""
    NOT_STARTED = "not_started"  # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    ON_HOLD = "on_hold"  # 已暂停
    CANCELLED = "cancelled"  # 已取消 
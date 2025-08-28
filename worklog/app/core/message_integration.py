"""
消息系统集成示例
展示如何在现有功能中集成消息机制
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.core.message_service import message_service
from app.models.task import Task
from app.models.team import Team
from app.models.user import User

class MessageIntegration:
    """消息系统集成类"""
    
    @staticmethod
    def send_task_assigned_notification(
        db: Session,
        task: Task,
        assignee: User,
        assigner: Optional[User] = None
    ):
        """发送任务分配通知"""
        try:
            project_name = task.project.name if task.project else "未分配项目"
            due_date = task.due_date.strftime("%Y-%m-%d") if task.due_date else "无截止日期"
            
            message_service.send_task_assigned_message(
                db=db,
                task_title=task.title,
                project_name=project_name,
                priority=task.priority.value if task.priority else "normal",
                due_date=due_date,
                receiver_id=assignee.id,
                sender_id=assigner.id if assigner else None
            )
            
        except Exception as e:
            print(f"发送任务分配通知失败: {e}")
    
    @staticmethod
    def send_task_status_changed_notification(
        db: Session,
        task: Task,
        old_status: str,
        new_status: str,
        updater: User
    ):
        """发送任务状态变更通知"""
        try:
            # 获取任务相关用户
            users_to_notify = []
            
            # 任务负责人
            if task.assignee:
                users_to_notify.append(task.assignee)
            
            # 任务创建者（如果不是同一个人）
            if task.creator and task.creator.id != updater.id:
                users_to_notify.append(task.creator)
            
            # 发送通知给相关用户
            for user in users_to_notify:
                message_service.send_task_status_changed_message(
                    db=db,
                    task_title=task.title,
                    new_status=new_status,
                    updater_name=updater.username,
                    receiver_id=user.id,
                    sender_id=updater.id
                )
                
        except Exception as e:
            print(f"发送任务状态变更通知失败: {e}")
    
    @staticmethod
    def send_task_due_reminder(
        db: Session,
        task: Task
    ):
        """发送任务截止提醒"""
        try:
            if not task.assignee or not task.due_date:
                return
            
            from datetime import datetime, timedelta
            
            # 计算剩余时间
            now = datetime.now()
            time_diff = task.due_date - now
            
            if time_diff.days > 0:
                time_remaining = f"{time_diff.days}天"
            elif time_diff.seconds > 3600:
                time_remaining = f"{time_diff.seconds // 3600}小时"
            else:
                time_remaining = f"{time_diff.seconds // 60}分钟"
            
            message_service.send_task_due_reminder(
                db=db,
                task_title=task.title,
                due_date=task.due_date.strftime("%Y-%m-%d %H:%M"),
                time_remaining=time_remaining,
                receiver_id=task.assignee.id
            )
            
        except Exception as e:
            print(f"发送任务截止提醒失败: {e}")
    
    @staticmethod
    def send_team_invitation_notification(
        db: Session,
        team: Team,
        inviter: User,
        invitee_email: str
    ):
        """发送团队邀请通知"""
        try:
            # 查找被邀请用户
            invitee = db.query(User).filter(User.email == invitee_email).first()
            if not invitee:
                return
            
            message_service.send_team_invitation_message(
                db=db,
                team_name=team.name,
                inviter_name=inviter.username,
                receiver_id=invitee.id,
                sender_id=inviter.id
            )
            
        except Exception as e:
            print(f"发送团队邀请通知失败: {e}")
    
    @staticmethod
    def send_worklog_reminder(
        db: Session,
        user: User
    ):
        """发送工作日志提醒"""
        try:
            message_service.send_worklog_reminder(
                db=db,
                receiver_id=user.id
            )
            
        except Exception as e:
            print(f"发送工作日志提醒失败: {e}")
    
    @staticmethod
    def send_system_maintenance_notification(
        db: Session,
        maintenance_time: str,
        duration: str,
        impact: str
    ):
        """发送系统维护通知"""
        try:
            # 获取所有活跃用户
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                message_service.send_message(
                    db=db,
                    template_name="system_maintenance",
                    receiver_id=user.id,
                    variables={
                        "receiver_name": user.username,
                        "maintenance_time": maintenance_time,
                        "duration": duration,
                        "impact": impact
                    }
                )
                
        except Exception as e:
            print(f"发送系统维护通知失败: {e}")

# 全局集成实例
message_integration = MessageIntegration() 
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from jinja2 import Template

from app.crud.message import message_crud, message_template_crud
from app.schemas.message import MessageCreate, MessageTemplateCreate
from app.models.user import User
from app.core.notification import send_notification
from app.core.email import send_email
from app.models.message import Message, MessageTemplate
from app.models.team_member import TeamMember
from app.models.task import Task
from app.models.project import Project
from app.core.ws_manager import ws_manager
from app.schemas.message import MessageUpdate
from app.models.team import Team
from app.models.work_log import WorkLog
from app.models.enums import TEAM_ADMIN

logger = logging.getLogger(__name__)

class MessageService:
    """消息服务类"""
    
    def __init__(self):
        self.default_templates = {
            "task_assigned": {
                "name": "task_assigned",
                "title_template": "新任务分配：{{ task_title }}",
                "content_template": """
                <p>您好 {{ receiver_name }}，</p>
                <p>您有一个新任务被分配：</p>
                <ul>
                    <li><strong>任务标题：</strong>{{ task_title }}</li>
                    <li><strong>项目：</strong>{{ project_name }}</li>
                    <li><strong>优先级：</strong>{{ priority }}</li>
                    <li><strong>截止日期：</strong>{{ due_date }}</li>
                </ul>
                <p>请及时处理此任务。</p>
                """,
                "message_type": "task",
                "priority": "important",
                "variables": {}
            },
            "task_status_changed": {
                "name": "task_status_changed",
                "title_template": "任务状态变更：{{ task_title }}",
                "content_template": """
                <p>您好 {{ receiver_name }}，</p>
                <p>任务状态已更新：</p>
                <ul>
                    <li><strong>任务标题：</strong>{{ task_title }}</li>
                    <li><strong>新状态：</strong>{{ new_status }}</li>
                    <li><strong>更新人：</strong>{{ updater_name }}</li>
                    <li><strong>更新时间：</strong>{{ update_time }}</li>
                </ul>
                """,
                "message_type": "task",
                "priority": "normal",
                "variables": {}
            },
            "task_due_reminder": {
                "name": "task_due_reminder",
                "title_template": "任务截止提醒：{{ task_title }}",
                "content_template": """
                <p>您好 {{ receiver_name }}，</p>
                <p>您有一个任务即将到期：</p>
                <ul>
                    <li><strong>任务标题：</strong>{{ task_title }}</li>
                    <li><strong>截止日期：</strong>{{ due_date }}</li>
                    <li><strong>剩余时间：</strong>{{ time_remaining }}</li>
                </ul>
                <p>请尽快完成此任务。</p>
                """,
                "message_type": "task",
                "priority": "urgent",
                "variables": {}
            },
            "team_invitation": {
                "name": "team_invitation",
                "title_template": "团队邀请：{{ team_name }}",
                "content_template": """
                <p>您好 {{ receiver_name }}，</p>
                <p>您收到了一个团队邀请：</p>
                <ul>
                    <li><strong>团队名称：</strong>{{ team_name }}</li>
                    <li><strong>邀请人：</strong>{{ inviter_name }}</li>
                    <li><strong>邀请时间：</strong>{{ invite_time }}</li>
                </ul>
                <p>请及时处理此邀请。</p>
                """,
                "message_type": "team",
                "priority": "important",
                "variables": {}
            },
            "worklog_reminder": {
                "name": "worklog_reminder",
                "title_template": "工作日志提醒",
                "content_template": """
                <p>您好 {{ receiver_name }}，</p>
                <p>现在是记录工作日志的时间了。</p>
                <p>提醒时间：{{ reminder_time }}</p>
                <p>请及时记录您的工作内容。</p>
                """,
                "message_type": "worklog",
                "priority": "normal",
                "variables": {}
            },
            "system_maintenance": {
                "name": "system_maintenance",
                "title_template": "系统维护通知",
                "content_template": """
                <p>您好 {{ receiver_name }}，</p>
                <p>系统将进行维护：</p>
                <ul>
                    <li><strong>维护时间：</strong>{{ maintenance_time }}</li>
                    <li><strong>预计时长：</strong>{{ duration }}</li>
                    <li><strong>影响范围：</strong>{{ impact }}</li>
                </ul>
                <p>给您带来的不便，敬请谅解。</p>
                """,
                "message_type": "system",
                "priority": "important",
                "variables": {}
            }
        }
    
    def initialize_templates(self, db: Session):
        """初始化默认消息模板"""
        for template_data in self.default_templates.values():
            existing = message_template_crud.get_by_name(db, template_data["name"])
            if not existing:
                template_obj = MessageTemplateCreate(**template_data)
                message_template_crud.create(db, obj_in=template_obj)
                logger.info(f"Created default template: {template_data['name']}")
    
    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """渲染消息模板"""
        try:
            template = Template(template_content)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return template_content
    
    def send_message(
        self,
        db: Session,
        template_name: str,
        recipients: List[int],
        variables: Dict[str, Any],
        sender_id: Optional[int] = None,
        message_data: Optional[Dict[str, Any]] = None
    ):
        """发送消息"""
        try:
            # 获取模板
            template = message_template_crud.get_by_name(db, template_name)
            if not template:
                logger.error(f"Template not found: {template_name}")
                return None
            
            # 渲染模板
            title = self.render_template(template.title_template, variables)
            content = self.render_template(template.content_template, variables)
            
            # 创建消息
            message_data_obj = MessageCreate(
                title=title,
                content=content,
                message_type=template.message_type,
                priority=template.priority,
                recipients=recipients,
                sender_id=sender_id,
                message_data=message_data or {}
            )
            
            message = message_crud.create(db, obj_in=message_data_obj)
            
            # 发送通知
            self._send_notifications(db, message, template)
            
            logger.info(f"Message sent: {message.id} to users {recipients}")
            return message
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def _send_notifications(self, db: Session, message, template):
        """发送多渠道通知"""
        try:
            # WebSocket实时通知
            if template.send_via_websocket:
                self._send_websocket_notification(message)
                message.sent_via_websocket = True
            
            # 邮件通知
            if template.send_via_email:
                self._send_email_notification(message)
                message.sent_via_email = True
            
            # 桌面通知
            if template.send_via_desktop:
                self._send_desktop_notification(message)
                message.sent_via_desktop = True
            
            # 更新消息状态
            db.add(message)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def _send_websocket_notification(self, message):
        """发送WebSocket通知"""
        # TODO: 实现WebSocket通知
        # 这里需要集成WebSocket服务
        pass
    
    def _send_email_notification(self, message):
        """发送邮件通知"""
        try:
            # 获取接收者信息
            receiver = message.receiver
            if not receiver or not receiver.email:
                return
            
            # 这里需要异步调用邮件发送
            # await send_email(
            #     email_to=receiver.email,
            #     subject_template=message.title,
            #     html_template=message.content
            # )
            
        except Exception as e:
            logger.error(f"Email notification error: {e}")
    
    def _send_desktop_notification(self, message):
        """发送桌面通知"""
        # TODO: 实现桌面通知
        # 这里需要集成桌面通知服务
        pass
    
    def send_task_assigned_message(
        self,
        db: Session,
        task_title: str,
        project_name: str,
        priority: str,
        due_date: str,
        receiver_id: int,
        sender_id: Optional[int] = None
    ):
        """发送任务分配消息"""
        variables = {
            "task_title": task_title,
            "project_name": project_name,
            "priority": priority,
            "due_date": due_date,
            "receiver_name": "用户"  # 这里应该获取实际的用户名
        }
        
        return self.send_message(
            db=db,
            template_name="task_assigned",
            recipients=[receiver_id],
            variables=variables,
            sender_id=sender_id,
            message_data={"task_title": task_title, "project_name": project_name}
        )
    
    def send_task_status_changed_message(
        self,
        db: Session,
        task_title: str,
        new_status: str,
        updater_name: str,
        receiver_id: int,
        sender_id: Optional[int] = None
    ):
        """发送任务状态变更消息"""
        variables = {
            "task_title": task_title,
            "new_status": new_status,
            "updater_name": updater_name,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "receiver_name": "用户"
        }
        
        return self.send_message(
            db=db,
            template_name="task_status_changed",
            recipients=[receiver_id],
            variables=variables,
            sender_id=sender_id,
            message_data={"task_title": task_title, "new_status": new_status}
        )
    
    def send_task_due_reminder(
        self,
        db: Session,
        task_title: str,
        due_date: str,
        time_remaining: str,
        receiver_id: int
    ):
        """发送任务截止提醒"""
        variables = {
            "task_title": task_title,
            "due_date": due_date,
            "time_remaining": time_remaining,
            "receiver_name": "用户"
        }
        
        return self.send_message(
            db=db,
            template_name="task_due_reminder",
            recipients=[receiver_id],
            variables=variables,
            message_data={"task_title": task_title, "due_date": due_date}
        )
    
    def send_team_invitation_message(
        self,
        db: Session,
        team_name: str,
        inviter_name: str,
        receiver_id: int,
        sender_id: int
    ):
        """发送团队邀请消息"""
        variables = {
            "team_name": team_name,
            "inviter_name": inviter_name,
            "invite_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "receiver_name": "用户"
        }
        
        return self.send_message(
            db=db,
            template_name="team_invitation",
            recipients=[receiver_id],
            variables=variables,
            sender_id=sender_id,
            message_data={"team_name": team_name}
        )
    
    def send_worklog_reminder(
        self,
        db: Session,
        receiver_id: int
    ):
        """发送工作日志提醒"""
        variables = {
            "receiver_name": "用户",
            "reminder_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.send_message(
            db=db,
            template_name="worklog_reminder",
            recipients=[receiver_id],
            variables=variables
        )

# 全局消息服务实例
message_service = MessageService()

class MessagePushService:
    """消息推送服务 - 扩展版本"""
    
    @staticmethod
    async def send_task_notification(
        db: Session,
        task: Task,
        notification_type: str,
        recipients: List[int],
        extra_data: Optional[Dict] = None
    ):
        """发送任务相关通知"""
        try:
            # 获取任务相关信息
            creator = db.query(User).filter(User.id == task.creator_id).first()
            assignee = db.query(User).filter(User.id == task.assignee_id).first() if task.assignee_id else None
            
            # 构建消息内容
            message_data = {
                "type": "task_notification",
                "notification_type": notification_type,
                "task_id": task.id,
                "task_title": task.title,
                "task_status": task.status if task.status else None,
                "creator_name": creator.username if creator else "未知用户",
                "assignee_name": assignee.username if assignee else None,
                "timestamp": datetime.now().isoformat(),
                "extra_data": extra_data or {}
            }
            
            # 发送WebSocket消息
            await ws_manager.send_team_message(recipients, message_data)
            
            # 保存到数据库
            message_create = MessageCreate(
                title=f"任务通知: {task.title}",
                content=json.dumps(message_data, ensure_ascii=False),
                message_type="task",
                sender_id=task.creator_id,
                recipients=recipients,
                message_data=message_data
            )
            
            message_crud.create(db, obj_in=message_create)
            logger.info(f"任务通知已发送: {notification_type} - 任务ID: {task.id}")
            
        except Exception as e:
            logger.error(f"发送任务通知失败: {e}")
    
    @staticmethod
    async def send_project_notification(
        db: Session,
        project: Project,
        notification_type: str,
        recipients: List[int],
        extra_data: Optional[Dict] = None
    ):
        """发送项目相关通知"""
        try:
            # 获取项目创建者信息
            creator = db.query(User).filter(User.id == project.creator_id).first()
            
            # 构建消息内容
            message_data = {
                "type": "project_notification",
                "notification_type": notification_type,
                "project_id": project.id,
                "project_name": project.name,
                "creator_name": creator.username if creator else "未知用户",
                "timestamp": datetime.now().isoformat(),
                "extra_data": extra_data or {}
            }
            
            # 发送WebSocket消息
            await ws_manager.send_team_message(recipients, message_data)
            
            # 保存到数据库
            message_create = MessageCreate(
                title=f"项目通知: {project.name}",
                content=json.dumps(message_data, ensure_ascii=False),
                message_type="project",
                sender_id=project.creator_id,
                recipients=recipients,
                message_data=message_data
            )
            
            message_crud.create(db, obj_in=message_create)
            logger.info(f"项目通知已发送: {notification_type} - 项目ID: {project.id}")
            
        except Exception as e:
            logger.error(f"发送项目通知失败: {e}")
    
    @staticmethod
    async def send_team_notification(
        db: Session,
        team_id: int,
        notification_type: str,
        sender_id: int,
        recipients: List[int],
        extra_data: Optional[Dict] = None
    ):
        """发送团队相关通知"""
        try:
            # 获取发送者信息
            sender = db.query(User).filter(User.id == sender_id).first()
            
            # 构建消息内容
            message_data = {
                "type": "team_notification",
                "notification_type": notification_type,
                "team_id": team_id,
                "sender_name": sender.username if sender else "未知用户",
                "timestamp": datetime.now().isoformat(),
                "extra_data": extra_data or {}
            }
            
            # 发送WebSocket消息
            await ws_manager.send_team_message(recipients, message_data)
            
            # 保存到数据库
            message_create = MessageCreate(
                title=f"团队通知: {notification_type}",
                content=json.dumps(message_data, ensure_ascii=False),
                message_type="team",
                sender_id=sender_id,
                recipients=recipients,
                message_data=message_data
            )
            
            message_crud.create(db, obj_in=message_create)
            logger.info(f"团队通知已发送: {notification_type} - 团队ID: {team_id}")
            
        except Exception as e:
            logger.error(f"发送团队通知失败: {e}")
    
    @staticmethod
    async def send_system_notification(
        db: Session,
        title: str,
        content: str,
        recipients: List[int],
        notification_type: str = "system",
        extra_data: Optional[Dict] = None
    ):
        """发送系统通知"""
        try:
            # 构建消息内容
            message_data = {
                "type": "system_notification",
                "notification_type": notification_type,
                "title": title,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "extra_data": extra_data or {}
            }
            
            # 发送WebSocket消息
            await ws_manager.send_team_message(recipients, message_data)
            
            # 保存到数据库
            message_create = MessageCreate(
                title=title,
                content=content,
                message_type="system",
                sender_id=1,  # 系统用户ID
                recipients=recipients,
                message_data=message_data
            )
            
            message_crud.create(db, obj_in=message_create)
            logger.info(f"系统通知已发送: {title}")
            
        except Exception as e:
            logger.error(f"发送系统通知失败: {e}")
    
    @staticmethod
    async def send_worklog_notification(
        db: Session,
        worklog_id: int,
        notification_type: str,
        recipients: List[int],
        extra_data: Optional[Dict] = None
    ):
        """发送工作日志相关通知"""
        try:
            # 获取工作日志信息
            worklog = db.query(WorkLog).filter(WorkLog.id == worklog_id).first()
            if not worklog:
                logger.error(f"工作日志不存在: {worklog_id}")
                return
            
            user = db.query(User).filter(User.id == worklog.user_id).first()
            
            # 构建消息内容
            message_data = {
                "type": "worklog_notification",
                "notification_type": notification_type,
                "worklog_id": worklog_id,
                "user_name": user.username if user else "未知用户",
                "timestamp": datetime.now().isoformat(),
                "extra_data": extra_data or {}
            }
            
            # 发送WebSocket消息
            await ws_manager.send_team_message(recipients, message_data)
            
            # 保存到数据库
            message_create = MessageCreate(
                title=f"工作日志通知: {notification_type}",
                content=json.dumps(message_data, ensure_ascii=False),
                message_type="worklog",
                sender_id=worklog.user_id,
                recipients=recipients,
                message_data=message_data
            )
            
            message_crud.create(db, obj_in=message_create)
            logger.info(f"工作日志通知已发送: {notification_type} - 工作日志ID: {worklog_id}")
            
        except Exception as e:
            logger.error(f"发送工作日志通知失败: {e}")
    
    @staticmethod
    def get_team_member_ids(db: Session, team_id: int, exclude_user_id: Optional[int] = None) -> List[int]:
        """获取团队成员ID列表"""
        query = db.query(TeamMember.user_id).filter(TeamMember.team_id == team_id)
        if exclude_user_id:
            query = query.filter(TeamMember.user_id != exclude_user_id)
        return [row[0] for row in query.all()]
    
    @staticmethod
    def get_task_related_users(db: Session, task: Task, exclude_user_id: Optional[int] = None) -> List[int]:
        """获取任务相关用户ID列表（创建者、负责人、团队成员）"""
        user_ids = set()
        
        # 添加创建者
        if task.creator_id and task.creator_id != exclude_user_id:
            user_ids.add(task.creator_id)
        
        # 添加负责人
        if task.assignee_id and task.assignee_id != exclude_user_id:
            user_ids.add(task.assignee_id)
        
        # 添加团队成员（除操作者外）
        team_member_ids = MessagePushService.get_team_member_ids(db, task.team_id, exclude_user_id)
        user_ids.update(team_member_ids)
        
        return list(user_ids)
    
    # ==================== 任务相关通知方法 ====================
    
    @staticmethod
    async def notify_task_created(db: Session, task: Task, creator_id: int):
        """通知任务创建"""
        # 获取团队成员（除创建者外）
        recipients = MessagePushService.get_team_member_ids(db, task.team_id, creator_id)
        await MessagePushService.send_task_notification(
            db, task, "task_created", recipients,
            {"creator_id": creator_id}
        )
    
    @staticmethod
    async def notify_task_assigned(db: Session, task: Task, assignee_id: int, assigner_id: int):
        """通知任务分配"""
        # 主要通知被分配者
        recipients = [assignee_id]
        
        # 可选：通知任务创建者（如果创建者不是分配者）
        if task.creator_id != assigner_id and task.creator_id != assignee_id:
            recipients.append(task.creator_id)
        
        await MessagePushService.send_task_notification(
            db, task, "task_assigned", recipients,
            {"assignee_id": assignee_id, "assigner_id": assigner_id}
        )
    
    @staticmethod
    async def notify_task_status_changed(db: Session, task: Task, old_status: str, new_status: str, operator_id: int):
        """通知任务状态变更"""
        # 获取任务相关用户（除操作者外）
        recipients = MessagePushService.get_task_related_users(db, task, operator_id)
        
        await MessagePushService.send_task_notification(
            db, task, "task_status_changed", recipients,
            {"old_status": old_status, "new_status": new_status, "operator_id": operator_id}
        )
    
    @staticmethod
    async def notify_task_completed(db: Session, task: Task, completer_id: int):
        """通知任务完成"""
        # 通知任务创建者和团队管理员
        recipients = []
        
        # 添加创建者（如果不是完成者）
        if task.creator_id != completer_id:
            recipients.append(task.creator_id)
        
        # 添加团队管理员
        admin_ids = db.query(TeamMember.user_id).filter(
            TeamMember.team_id == task.team_id,
            TeamMember.role == TEAM_ADMIN
        ).all()
        for admin_id in admin_ids:
            if admin_id[0] != completer_id and admin_id[0] not in recipients:
                recipients.append(admin_id[0])
        
        await MessagePushService.send_task_notification(
            db, task, "task_completed", recipients,
            {"completer_id": completer_id}
        )
    
    @staticmethod
    async def notify_task_comment_added(db: Session, task: Task, comment_id: int, commenter_id: int):
        """通知任务评论"""
        # 获取任务相关用户（除评论者外）
        recipients = MessagePushService.get_task_related_users(db, task, commenter_id)
        
        await MessagePushService.send_task_notification(
            db, task, "task_comment_added", recipients,
            {"comment_id": comment_id, "commenter_id": commenter_id}
        )
    
    @staticmethod
    async def notify_task_due_reminder(db: Session, task: Task, days_remaining: int):
        """通知任务截止日期提醒"""
        # 只通知任务负责人
        if task.assignee_id:
            await MessagePushService.send_task_notification(
                db, task, "task_due_reminder", [task.assignee_id],
                {"days_remaining": days_remaining}
            )
    
    # ==================== 团队相关通知方法 ====================
    
    @staticmethod
    async def notify_team_invitation(db: Session, team_id: int, inviter_id: int, invitee_id: int):
        """通知团队邀请"""
        # 通知被邀请者
        await MessagePushService.send_team_notification(
            db, team_id, "team_invitation", inviter_id, [invitee_id],
            {"inviter_id": inviter_id, "invitee_id": invitee_id}
        )
    
    @staticmethod
    async def notify_team_member_joined(db: Session, team_id: int, new_member_id: int):
        """通知团队成员加入"""
        # 通知现有团队成员
        recipients = MessagePushService.get_team_member_ids(db, team_id, new_member_id)
        await MessagePushService.send_team_notification(
            db, team_id, "team_member_joined", new_member_id, recipients,
            {"new_member_id": new_member_id}
        )
    
    @staticmethod
    async def notify_team_member_left(db: Session, team_id: int, leaving_member_id: int):
        """通知团队成员离开"""
        # 通知剩余团队成员
        recipients = MessagePushService.get_team_member_ids(db, team_id, leaving_member_id)
        await MessagePushService.send_team_notification(
            db, team_id, "team_member_left", leaving_member_id, recipients,
            {"leaving_member_id": leaving_member_id}
        )
    
    # ==================== 项目相关通知方法 ====================
    
    @staticmethod
    async def notify_project_created(db: Session, project: Project, creator_id: int):
        """通知项目创建"""
        # 通知团队成员（除创建者外）
        recipients = MessagePushService.get_team_member_ids(db, project.team_id, creator_id)
        await MessagePushService.send_project_notification(
            db, project, "project_created", recipients,
            {"creator_id": creator_id}
        )
    
    @staticmethod
    async def notify_project_status_changed(db: Session, project: Project, old_status: str, new_status: str, operator_id: int):
        """通知项目状态变更"""
        # 通知项目成员（除操作者外）
        recipients = MessagePushService.get_team_member_ids(db, project.team_id, operator_id)
        await MessagePushService.send_project_notification(
            db, project, "project_status_changed", recipients,
            {"old_status": old_status, "new_status": new_status, "operator_id": operator_id}
        )
    
    # ==================== 工作日志相关通知方法 ====================
    
    @staticmethod
    async def notify_worklog_reminder(db: Session, user_id: int, team_id: int):
        """通知工作日志提醒"""
        await MessagePushService.send_worklog_notification(
            db, 0, "worklog_reminder", [user_id],
            {"team_id": team_id}
        )
    
    @staticmethod
    async def notify_worklog_submitted(db: Session, worklog_id: int, submitter_id: int, team_id: int):
        """通知工作日志提交"""
        # 通知团队管理员
        admin_ids = db.query(TeamMember.user_id).filter(
            TeamMember.team_id == team_id,
            TeamMember.role == TEAM_ADMIN
        ).all()
        
        recipients = [admin_id[0] for admin_id in admin_ids if admin_id[0] != submitter_id]
        
        await MessagePushService.send_worklog_notification(
            db, worklog_id, "worklog_submitted", recipients,
            {"submitter_id": submitter_id, "team_id": team_id}
        )
    
    # ==================== 系统通知方法 ====================
    
    @staticmethod
    async def notify_system_maintenance(db: Session, title: str, content: str, affected_users: List[int]):
        """通知系统维护"""
        await MessagePushService.send_system_notification(
            db, title, content, affected_users, "system_maintenance"
        )
    
    @staticmethod
    async def notify_permission_changed(db: Session, user_id: int, permission_type: str, details: str):
        """通知权限变更"""
        await MessagePushService.send_system_notification(
            db, "权限变更通知", details, [user_id], "permission_changed",
            {"permission_type": permission_type}
        )

# 创建全局实例
message_push_service = MessagePushService() 
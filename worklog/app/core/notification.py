import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.models.user import User
from app.models.reminder import Reminder
from app.core.email import send_email

async def send_notification(user: User, reminder: Reminder, notification_method: str):
    """
    发送通知
    """
    if notification_method == "email":
        await send_email_notification(user, reminder)
    elif notification_method == "system":
        await send_system_notification(user, reminder)
    elif notification_method == "dingtalk":
        await send_dingtalk_notification(user, reminder)

async def send_email_notification(user: User, reminder: Reminder):
    """
    发送邮件通知
    """
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        return
    
    subject = "工作日志提醒"
    html = f"""
    <p>您好 {user.username}，</p>
    <p>现在是记录工作日志的时间了。</p>
    <p>提醒时间：{reminder.scheduled_at}</p>
    <p>提醒类型：{reminder.reminder_type}</p>
    <p>{reminder.message or "请及时记录您的工作内容。"}</p>
    <p>此致</p>
    <p>WorkLog Pro 团队</p>
    """
    
    try:
        await send_email(
            email_to=user.email,
            subject_template=subject,
            html_template=html
        )
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")

async def send_system_notification(user: User, reminder: Reminder):
    """
    发送系统通知
    """
    # TODO: 实现系统通知
    # 这里可以使用WebSocket或其他实时通知机制
    pass

async def send_dingtalk_notification(user: User, reminder: Reminder):
    """
    发送钉钉通知
    """
    # TODO: 实现钉钉通知
    # 这里需要调用钉钉的API
    pass 
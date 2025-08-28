from typing import Any, Dict, Optional
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailSchema(BaseModel):
    email: EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
    MAIL_STARTTLS=settings.SMTP_TLS,  # 使用配置中的 TLS 设置
    MAIL_SSL_TLS=not settings.SMTP_TLS,  # 如果使用 TLS，则不使用 SSL
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True   # 验证SSL证书
)

async def send_email(
    email_to: str,
    subject: str,
    body: str,
    html: str = None
) -> None:
    """
    发送邮件
    """
    try:
        logger.info(f"开始发送邮件到: {email_to}")
        logger.info(f"邮件主题: {subject}")
        logger.info(f"邮件服务器配置: host={settings.SMTP_HOST}, port={settings.SMTP_PORT}, user={settings.SMTP_USER}")
        logger.info(f"TLS设置: SMTP_TLS={settings.SMTP_TLS}, SSL_TLS={not settings.SMTP_TLS}")
        
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            html=html,
            subtype="html"
        )
        
        logger.info("创建 FastMail 实例")
        fm = FastMail(conf)
        
        logger.info("开始发送邮件...")
        await fm.send_message(message)
        logger.info(f"邮件发送成功: {email_to}")
        
    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {str(e)}")
        raise

async def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - 密码重置"
    link = f"{settings.SERVER_HOST}/reset-password?token={token}"
    html = f"""
    <p>您好，</p>
    <p>您收到这封邮件是因为您（或其他人）请求重置密码。</p>
    <p>请点击下面的链接重置密码：</p>
    <p><a href="{link}">{link}</a></p>
    <p>如果您没有请求重置密码，请忽略此邮件。</p>
    <p>此致，</p>
    <p>{project_name}团队</p>
    """
    await send_email(email_to=email_to, subject=subject, body=html)

async def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - 新账户创建"
    html = f"""
    <p>您好 {username}，</p>
    <p>您的账户已创建成功。</p>
    <p>您的登录信息如下：</p>
    <p>用户名：{username}</p>
    <p>密码：{password}</p>
    <p>请登录后立即修改密码。</p>
    <p>此致，</p>
    <p>{project_name}团队</p>
    """
    await send_email(email_to=email_to, subject=subject, body=html)

async def send_invitation_email(email_to: str, team_name: str, inviter_name: str, team_id: int, token: str) -> None:
    """
    发送团队邀请邮件
    """
    project_name = settings.PROJECT_NAME
    subject = f"邀请加入{team_name}团队"
    invite_link = f"{settings.FRONTEND_URL}/register?token={token}"
    print(f"邀请链接: {invite_link}")
    html = f"""
    <p>您好，</p>
    <p>{inviter_name}邀请您加入{team_name}团队。</p>
    <p>请点击以下链接接受邀请：</p>
    <p><a href="{invite_link}">接受邀请</a></p>
    <p>如果您没有请求加入该团队，请忽略此邮件。</p>
    <p>此链接将在24小时后失效。</p>
    <p>谢谢！</p>
    <p>{project_name}团队</p>
    """
    await send_email(email_to=email_to, subject=subject, body=html)

async def send_invitation_verification_email(email_to: str, team_name: str, inviter_name: str, verification_code: str) -> None:
    """
    发送团队邀请验证码邮件
    """
    project_name = settings.PROJECT_NAME
    subject = f"邀请加入{team_name}团队 - 验证码"
    verify_link = f"{settings.FRONTEND_URL}/verify-invitation?email={email_to}&inviter={inviter_name}&team_name={team_name}"
    html = f"""
    <p>您好，</p>
    <p>{inviter_name}邀请您加入{team_name}团队。</p>
    <p>您的邀请验证码是：</p>
    <h2 style="color: #409eff; font-size: 24px; text-align: center; padding: 20px; background-color: #f5f7fa; border-radius: 8px; margin: 20px 0;">
        {verification_code}
    </h2>
    <p>请在10分钟内使用此验证码完成邀请验证。</p>
    <p>您也可以点击以下链接直接进入验证页面：</p>
    <p><a href="{verify_link}">验证邀请</a></p>
    <p>如果您没有请求加入该团队，请忽略此邮件。</p>
    <p>谢谢！</p>
    <p>{project_name}团队</p>
    """
    await send_email(email_to=email_to, subject=subject, body=html) 
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from app.core.email import send_invitation_email
from app.core.config import settings

@pytest.mark.asyncio
async def test_send_invitation_email():
    """测试发送团队邀请邮件"""
    try:
        await send_invitation_email(
            email_to="378975390@qq.com",
            team_name="测试团队",
            inviter_name="测试用户"
        )
    except Exception as e:
        pytest.fail(f"发送邀请邮件失败: {str(e)}")

@pytest.mark.asyncio
async def test_send_invitation_email_invalid_email():
    """测试发送邀请邮件到无效邮箱"""
    with pytest.raises(Exception) as exc_info:
        await send_invitation_email(
            email_to="invalid_email",
            team_name="测试团队",
            inviter_name="测试用户"
        )
    assert "Invalid email" in str(exc_info.value)

@pytest.mark.asyncio
async def test_send_invitation_email_empty_team_name():
    """测试发送邀请邮件时团队名称为空"""
    with pytest.raises(ValueError) as exc_info:
        await send_invitation_email(
            email_to="378975390@qq.com",
            team_name="",
            inviter_name="测试用户"
        )
    assert "Team name cannot be empty" in str(exc_info.value)

@pytest.mark.asyncio
async def test_send_invitation_email_empty_inviter():
    """测试发送邀请邮件时邀请人为空"""
    with pytest.raises(ValueError) as exc_info:
        await send_invitation_email(
            email_to="378975390@qq.com",
            team_name="测试团队",
            inviter_name=""
        )
    assert "Inviter name cannot be empty" in str(exc_info.value)

@pytest.mark.asyncio
async def test_send_invitation_email_smtp_config():
    """测试SMTP配置是否正确"""
    assert settings.SMTP_TLS, "SMTP TLS should be enabled"
    assert settings.SMTP_PORT, "SMTP port should be configured"
    assert settings.SMTP_HOST, "SMTP host should be configured"
    assert settings.SMTP_USER, "SMTP user should be configured"
    assert settings.SMTP_PASSWORD, "SMTP password should be configured"
    assert settings.EMAILS_FROM_EMAIL, "From email should be configured"
    assert settings.EMAILS_FROM_NAME, "From name should be configured"

if __name__ == "__main__":
    pytest.main(["-v", "test_email.py"]) 
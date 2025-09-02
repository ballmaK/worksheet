#!/usr/bin/env python3
"""
163邮箱配置快速设置脚本
帮助用户快速配置163邮箱SMTP设置
"""

import os
import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_smtp_connection(smtp_host, smtp_port, smtp_user, smtp_password):
    """测试SMTP连接"""
    print_section("🔍 SMTP连接测试")
    
    try:
        print(f"🔄 尝试连接到 {smtp_host}:{smtp_port}...")
        
        # 创建SMTP连接
        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        server.set_debuglevel(1)  # 启用调试输出
        
        # 发送EHLO
        server.ehlo()
        print("✅ EHLO命令成功")
        
        # 登录
        server.login(smtp_user, smtp_password)
        print("✅ 登录成功")
        
        # 关闭连接
        server.quit()
        print("✅ SMTP连接测试成功")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ 认证失败: {e}")
        print("请检查用户名和授权码是否正确")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ 连接失败: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接异常: {e}")
        return False

def send_test_email(smtp_host, smtp_port, smtp_user, smtp_password, test_email):
    """发送测试邮件"""
    print_section("📤 测试邮件发送")
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = test_email
        msg['Subject'] = "WorkLog Pro - 163邮箱配置测试"
        
        body = f"""
        <html>
        <body>
        <h2>163邮箱配置测试成功！</h2>
        <p>如果您收到这封邮件，说明163邮箱SMTP配置正确。</p>
        <p>发送时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>发件人: {smtp_user}</p>
        <p>此致，</p>
        <p>WorkLog Pro 团队</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # 发送邮件
        print(f"🔄 尝试发送测试邮件到 {test_email}...")
        
        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        server.login(smtp_user, smtp_password)
        
        text = msg.as_string()
        server.sendmail(smtp_user, test_email, text)
        server.quit()
        
        print("✅ 测试邮件发送成功！")
        print(f"请检查邮箱 {test_email} 是否收到测试邮件")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def setup_163_config():
    """设置163邮箱配置"""
    print_section("📧 163邮箱配置设置")
    
    print("🚀 欢迎使用163邮箱配置向导！")
    print("本脚本将帮助您配置WorkLog Pro的163邮箱邮件服务。")
    
    # 获取用户输入
    print("\n📝 请提供以下信息:")
    
    # 邮箱地址
    email = input("163邮箱地址 (例如: zkzk-11@163.com): ").strip()
    if not email or '@163.com' not in email:
        print("❌ 请输入有效的163邮箱地址")
        return False
    
    # 授权码
    auth_code = input("163邮箱授权码 (16位字符): ").strip()
    if not auth_code or len(auth_code) != 16:
        print("❌ 授权码必须是16位字符")
        return False
    
    # 发件人名称
    from_name = input("发件人显示名称 (默认: WorkLog Pro): ").strip()
    if not from_name:
        from_name = "WorkLog Pro"
    
    print_section("🔧 配置信息确认")
    print(f"邮箱地址: {email}")
    print(f"授权码: {'*' * len(auth_code)}")
    print(f"发件人名称: {from_name}")
    
    confirm = input("\n确认以上配置信息？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 配置已取消")
        return False
    
    # 测试SMTP连接
    if not test_smtp_connection('smtp.163.com', 465, email, auth_code):
        print("❌ SMTP连接测试失败，请检查配置")
        return False
    
    # 询问是否发送测试邮件
    print_section("📤 测试邮件发送")
    send_test = input("是否发送测试邮件？(y/N): ").strip().lower()
    
    if send_test == 'y':
        test_email = input("请输入测试收件人邮箱地址: ").strip()
        if not test_email:
            print("❌ 未输入测试邮箱地址")
            return False
        
        if not send_test_email('smtp.163.com', 465, email, auth_code, test_email):
            print("❌ 测试邮件发送失败")
            return False
    
    print_section("📋 Railway环境变量配置")
    print("请在Railway平台的项目设置中添加以下环境变量:")
    print()
    
    config_vars = {
        'SMTP_HOST': 'smtp.163.com',
        'SMTP_PORT': '465',
        'SMTP_USER': email,
        'SMTP_PASSWORD': auth_code,
        'EMAILS_FROM_EMAIL': email,
        'EMAILS_FROM_NAME': from_name,
        'SMTP_TLS': 'false'
    }
    
    for var, value in config_vars.items():
        print(f"{var}={value}")
    
    print_section("📚 配置步骤说明")
    print("1. 登录Railway平台")
    print("2. 进入您的WorkLog Pro项目")
    print("3. 点击'Settings'标签")
    print("4. 在'Variables'部分添加上述环境变量")
    print("5. 重新部署应用")
    
    print_section("⚠️  重要提醒")
    print("• 确保您的163邮箱已开启SMTP服务")
    print("• 授权码不是登录密码")
    print("• 配置完成后需要重新部署应用")
    print("• 部署后检查启动日志确认配置正确")
    
    print_section("✅ 配置完成")
    print("环境变量配置完成后，请重新部署应用。")
    print("应用启动时会显示邮件配置信息，请检查是否正确。")
    
    return True

def main():
    """主函数"""
    print("🔧 WorkLog Pro 163邮箱配置向导")
    print("=" * 60)
    
    try:
        success = setup_163_config()
        if success:
            print("\n🎉 配置向导完成！")
            print("请按照上述步骤在Railway平台设置环境变量。")
        else:
            print("\n❌ 配置向导失败")
            return 1
    except KeyboardInterrupt:
        print("\n\n🛑 配置被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 配置过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

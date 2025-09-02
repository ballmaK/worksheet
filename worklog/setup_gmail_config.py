#!/usr/bin/env python3
"""
Gmail邮箱配置快速设置脚本
帮助用户快速配置Gmail SMTP设置
"""

import os
import sys

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def setup_gmail_config():
    """设置Gmail配置"""
    print_section("📧 Gmail邮箱配置设置")
    
    print("🚀 欢迎使用Gmail邮箱配置向导！")
    print("本脚本将帮助您配置WorkLog Pro的Gmail邮件服务。")
    
    # 获取用户输入
    print("\n📝 请提供以下信息:")
    
    # 邮箱地址
    email = input("Gmail邮箱地址 (例如: ballmai1ly@gmail.com): ").strip()
    if not email or '@gmail.com' not in email:
        print("❌ 请输入有效的Gmail邮箱地址")
        return False
    
    # 应用专用密码
    app_password = input("应用专用密码 (16位字符): ").strip()
    if not app_password or len(app_password) != 16:
        print("❌ 应用专用密码必须是16位字符")
        return False
    
    # 发件人名称
    from_name = input("发件人显示名称 (默认: WorkLog Pro): ").strip()
    if not from_name:
        from_name = "WorkLog Pro"
    
    print_section("🔧 配置信息确认")
    print(f"邮箱地址: {email}")
    print(f"应用专用密码: {'*' * len(app_password)}")
    print(f"发件人名称: {from_name}")
    
    confirm = input("\n确认以上配置信息？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 配置已取消")
        return False
    
    print_section("📋 Railway环境变量配置")
    print("请在Railway平台的项目设置中添加以下环境变量:")
    print()
    
    config_vars = {
        'SMTP_HOST': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SMTP_USER': email,
        'SMTP_PASSWORD': app_password,
        'EMAILS_FROM_EMAIL': email,
        'EMAILS_FROM_NAME': from_name,
        'SMTP_TLS': 'true'
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
    print("• 确保您的Gmail账户已开启2步验证")
    print("• 应用专用密码不是登录密码")
    print("• 配置完成后需要重新部署应用")
    print("• 部署后检查启动日志确认配置正确")
    
    print_section("✅ 配置完成")
    print("环境变量配置完成后，请重新部署应用。")
    print("应用启动时会显示邮件配置信息，请检查是否正确。")
    
    return True

def main():
    """主函数"""
    print("🔧 WorkLog Pro Gmail邮箱配置向导")
    print("=" * 60)
    
    try:
        success = setup_gmail_config()
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

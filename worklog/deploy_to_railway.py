#!/usr/bin/env python3
"""
Railway 部署辅助脚本
用于生成环境变量配置和部署检查
"""

import os
import secrets
import sys

def generate_secret_key():
    """生成安全的密钥"""
    return secrets.token_urlsafe(32)

def create_env_template():
    """创建环境变量模板文件"""
    env_template = f"""# Railway 部署环境变量配置
# 请根据实际情况修改这些值

# 数据库配置
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=work_log

# 安全配置
SECRET_KEY={generate_secret_key()}

# Redis 配置（可选）
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# 邮件配置（可选）
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@163.com
EMAILS_FROM_NAME=WorkLog Pro

# 钉钉配置（可选）
DINGTALK_APP_KEY=your-dingtalk-app-key
DINGTALK_APP_SECRET=your-dingtalk-app-secret

# 提醒配置
DEFAULT_REMINDER_INTERVAL=30
WORK_HOURS_START=09:00
WORK_HOURS_END=18:00
"""
    
    with open('.env.railway', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("✅ 已创建 .env.railway 文件")
    print("请根据实际情况修改其中的配置值")

def check_deployment_files():
    """检查部署必需文件"""
    required_files = [
        'railway.json',
        'nixpacks.toml', 
        'Procfile',
        'runtime.txt',
        'requirements.txt',
        'main.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少以下部署文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ 所有部署文件检查通过")
        return True

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("建议使用Python 3.9或更高版本")
        return False

def main():
    """主函数"""
    print("🚀 Railway 部署检查工具")
    print("=" * 50)
    
    # 检查部署文件
    files_ok = check_deployment_files()
    
    # 检查Python版本
    python_ok = check_python_version()
    
    # 创建环境变量模板
    create_env_template()
    
    print("\n📋 部署步骤:")
    print("1. 注册 Railway 账户: https://railway.app/")
    print("2. 连接您的 GitHub 仓库")
    print("3. 选择 worklog 目录作为部署目录")
    print("4. 在 Railway 中配置环境变量（参考 .env.railway 文件）")
    print("5. 添加 MySQL 数据库服务")
    print("6. 部署完成后运行数据库迁移")
    
    if files_ok and python_ok:
        print("\n✅ 您的项目已准备好部署到 Railway!")
    else:
        print("\n❌ 请先解决上述问题再部署")

if __name__ == "__main__":
    main()

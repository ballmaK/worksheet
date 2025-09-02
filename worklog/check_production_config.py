#!/usr/bin/env python3
"""
生产环境配置检查脚本
用于验证邮件、数据库等关键配置是否正确
"""

import os
import sys
from pathlib import Path

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_email_config():
    """检查邮件配置"""
    print_section("📧 邮件配置检查")
    
    # 检查环境变量
    email_vars = {
        'SMTP_HOST': os.getenv('SMTP_HOST'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
        'EMAILS_FROM_EMAIL': os.getenv('EMAILS_FROM_EMAIL'),
        'EMAILS_FROM_NAME': os.getenv('EMAILS_FROM_NAME'),
        'SMTP_TLS': os.getenv('SMTP_TLS')
    }
    
    print("环境变量检查:")
    for var, value in email_vars.items():
        if value:
            if 'PASSWORD' in var:
                print(f"  ✅ {var}: {'*' * len(value)}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")
    
    # 检查配置完整性
    required_vars = ['SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD', 'EMAILS_FROM_EMAIL']
    missing_vars = [var for var in required_vars if not email_vars[var]]
    
    if missing_vars:
        print(f"\n⚠️  缺少必需的邮件配置: {', '.join(missing_vars)}")
        print("请在 Railway 平台设置相应的环境变量")
        return False
    
    # Gmail特定配置检查
    if email_vars['SMTP_HOST'] == 'smtp.gmail.com':
        print("\n🔍 Gmail配置检查:")
        
        # 检查端口
        if email_vars['SMTP_PORT'] and email_vars['SMTP_PORT'] != '587':
            print(f"  ⚠️  Gmail推荐使用端口587，当前端口: {email_vars['SMTP_PORT']}")
        
        # 检查TLS设置
        if email_vars['SMTP_TLS'] and email_vars['SMTP_TLS'].lower() != 'true':
            print("  ⚠️  Gmail必须启用TLS (SMTP_TLS=true)")
        
        # 检查邮箱格式
        if email_vars['SMTP_USER'] and not email_vars['SMTP_USER'].endswith('@gmail.com'):
            print("  ⚠️  Gmail邮箱地址格式不正确")
    
    print("\n✅ 邮件配置完整")
    return True

def check_database_config():
    """检查数据库配置"""
    print_section("🗄️  数据库配置检查")
    
    db_vars = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_NAME': os.getenv('DB_NAME')
    }
    
    print("环境变量检查:")
    for var, value in db_vars.items():
        if value:
            if 'PASSWORD' in var:
                print(f"  ✅ {var}: {'*' * len(value)}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: 未设置（使用默认值）")
    
    # 检查关键配置
    if not db_vars['DB_HOST'] or not db_vars['DB_PASSWORD']:
        print("\n⚠️  缺少关键的数据库配置")
        return False
    else:
        print("\n✅ 数据库配置完整")
        return True

def check_environment():
    """检查环境信息"""
    print_section("🌍 环境信息")
    
    env_vars = {
        'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT'),
        'PORT': os.getenv('PORT'),
        'NODE_ENV': os.getenv('NODE_ENV'),
        'PYTHON_VERSION': os.getenv('PYTHON_VERSION')
    }
    
    print("环境变量:")
    for var, value in env_vars.items():
        if value:
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: 未设置")
    
    # 判断是否为生产环境
    is_production = bool(os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('MYSQLHOST'))
    print(f"\n环境类型: {'🚀 生产环境' if is_production else '🔧 开发环境'}")

def check_config_files():
    """检查配置文件"""
    print_section("📁 配置文件检查")
    
    config_files = [
        'app/core/config.py',
        'app/core/config_production.py',
        'main.py'
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✅ {config_file}: 存在")
        else:
            print(f"  ❌ {config_file}: 不存在")

def main():
    """主函数"""
    print("🔍 WorkLog Pro 生产环境配置检查工具")
    print("=" * 60)
    
    # 检查环境
    check_environment()
    
    # 检查配置文件
    check_config_files()
    
    # 检查邮件配置
    email_ok = check_email_config()
    
    # 检查数据库配置
    db_ok = check_database_config()
    
    # 总结
    print_section("📊 检查结果总结")
    
    if email_ok and db_ok:
        print("🎉 所有配置检查通过！")
        print("✅ 邮件配置: 完整")
        print("✅ 数据库配置: 完整")
        print("\n🚀 可以正常部署到生产环境")
    else:
        print("⚠️  配置检查发现问题:")
        if not email_ok:
            print("❌ 邮件配置: 不完整")
        if not db_ok:
            print("❌ 数据库配置: 不完整")
        print("\n🔧 请根据上述提示修复配置问题")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

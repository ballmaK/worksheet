#!/usr/bin/env python3
"""
Railway环境诊断脚本
用于详细检查环境变量和数据库连接问题
"""

import os
import sys
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_environment_variables():
    """检查所有相关环境变量"""
    print_section("环境变量检查")
    
    # 所有可能的环境变量
    env_vars = {
        "Railway环境": [
            "RAILWAY_ENVIRONMENT",
            "RAILWAY_PROJECT_ID",
            "RAILWAY_SERVICE_ID"
        ],
        "MySQL配置": [
            "MYSQLHOST", "MYSQLPORT", "MYSQLUSER", 
            "MYSQLPASSWORD", "MYSQLDATABASE"
        ],
        "共享MySQL变量": [
            "MYSQL_DATABASE", "MYSQL_PUBLIC_URL", 
            "MYSQL_ROOT_PASSWORD", "MYSQL_URL"
        ],
        "通用数据库变量": [
            "DB_HOST", "DB_PORT", "DB_USER", 
            "DB_PASSWORD", "DB_NAME"
        ],
        "应用配置": [
            "PORT", "SECRET_KEY", "NODE_ENV"
        ]
    }
    
    for category, variables in env_vars.items():
        print(f"\n📋 {category}:")
        for var in variables:
            value = os.getenv(var)
            if value:
                if "PASSWORD" in var or "SECRET" in var:
                    print(f"  ✅ {var}: {'*' * len(value)}")
                else:
                    print(f"  ✅ {var}: {value}")
            else:
                print(f"  ❌ {var}: 未设置")

def check_railway_services():
    """检查Railway服务连接"""
    print_section("Railway服务检查")
    
    # 检查是否有Railway CLI
    try:
        result = subprocess.run(
            ["railway", "--version"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Railway CLI: {result.stdout.strip()}")
        else:
            print("❌ Railway CLI: 未安装或不可用")
    except FileNotFoundError:
        print("❌ Railway CLI: 未安装")
    
    # 检查当前项目
    try:
        result = subprocess.run(
            ["railway", "status"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Railway项目状态: 已连接")
            print(result.stdout)
        else:
            print("❌ Railway项目状态: 未连接")
    except FileNotFoundError:
        print("❌ 无法检查Railway项目状态")

def determine_database_config():
    """确定数据库配置"""
    print_section("数据库配置分析")
    
    # 检查Railway MySQL变量
    mysql_host = os.getenv("MYSQLHOST")
    mysql_port = os.getenv("MYSQLPORT")
    mysql_user = os.getenv("MYSQLUSER")
    mysql_password = os.getenv("MYSQLPASSWORD")
    mysql_database = os.getenv("MYSQLDATABASE")
    
    # 检查共享MySQL变量
    mysql_database_alt = os.getenv("MYSQL_DATABASE")
    
    # 检查通用变量
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    
    print("🔍 配置来源分析:")
    
    if mysql_host and mysql_host != "your-mysql-host":
        print("  🎯 使用Railway MySQL变量")
        config = {
            "host": mysql_host,
            "port": mysql_port or "3306",
            "user": mysql_user or "root",
            "password": mysql_password or "",
            "database": mysql_database or mysql_database_alt or "railway"
        }
    elif db_host and db_host != "localhost":
        print("  🎯 使用通用数据库变量")
        config = {
            "host": db_host,
            "port": db_port or "3306",
            "user": db_user or "root",
            "password": db_password or "",
            "database": db_name or "work_log"
        }
    else:
        print("  ❌ 未找到有效的数据库配置")
        config = {
            "host": "localhost",
            "port": "3306",
            "user": "root",
            "password": "",
            "database": "work_log"
        }
    
    print(f"\n📊 最终配置:")
    print(f"  主机: {config['host']}")
    print(f"  端口: {config['port']}")
    print(f"  用户: {config['user']}")
    print(f"  数据库: {config['database']}")
    print(f"  密码: {'*' * len(config['password']) if config['password'] else '未设置'}")
    
    return config

def test_database_connection(config):
    """测试数据库连接"""
    print_section("数据库连接测试")
    
    # 构建数据库URL
    database_url = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset=utf8mb4"
    print(f"🔗 数据库URL: {database_url.replace(config['password'], '*' * len(config['password']) if config['password'] else '')}")
    
    try:
        print("\n🔄 正在连接数据库...")
        engine = create_engine(database_url, echo=False, connect_timeout=10)
        
        with engine.connect() as conn:
            # 测试基本连接
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ 基本连接测试: 成功 (结果: {row[0]})")
            
            # 检查数据库版本
            result = conn.execute(text("SELECT VERSION() as version"))
            row = result.fetchone()
            print(f"✅ MySQL版本: {row[0]}")
            
            # 检查当前数据库
            result = conn.execute(text("SELECT DATABASE() as current_db"))
            row = result.fetchone()
            print(f"✅ 当前数据库: {row[0]}")
            
            # 检查表
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            if tables:
                print(f"✅ 发现 {len(tables)} 个表:")
                for table in tables:
                    print(f"    - {table[0]}")
            else:
                print("ℹ️  数据库中没有表")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def check_network_connectivity(config):
    """检查网络连接"""
    print_section("网络连接检查")
    
    try:
        # 尝试ping主机
        print(f"🔄 检查到 {config['host']} 的网络连接...")
        
        # 使用telnet或nc检查端口
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((config['host'], int(config['port'])))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {config['port']} 可访问")
        else:
            print(f"❌ 端口 {config['port']} 不可访问 (错误码: {result})")
            
    except Exception as e:
        print(f"❌ 网络检查失败: {e}")

def main():
    """主函数"""
    print("🚀 Railway环境诊断工具")
    print("=" * 60)
    
    # 检查环境变量
    check_environment_variables()
    
    # 检查Railway服务
    check_railway_services()
    
    # 确定数据库配置
    config = determine_database_config()
    
    # 检查网络连接
    check_network_connectivity(config)
    
    # 测试数据库连接
    connection_ok = test_database_connection(config)
    
    # 总结
    print_section("诊断总结")
    
    if connection_ok:
        print("🎉 数据库连接成功！")
        print("\n📋 建议:")
        print("1. 检查环境变量是否正确设置")
        print("2. 确保Railway MySQL服务正常运行")
        print("3. 验证服务间的网络连接")
    else:
        print("❌ 数据库连接失败！")
        print("\n🔧 故障排除建议:")
        print("1. 检查Railway MySQL服务是否已添加到项目")
        print("2. 验证环境变量是否正确设置")
        print("3. 确保后端服务能够访问MySQL服务")
        print("4. 检查防火墙和网络设置")
        print("5. 查看Railway控制台中的服务日志")

if __name__ == "__main__":
    main()

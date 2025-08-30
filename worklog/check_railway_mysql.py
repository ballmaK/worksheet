#!/usr/bin/env python3
"""
Railway MySQL配置检查脚本
专门用于检查Railway MySQL服务的配置
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_railway_mysql_variables():
    """检查Railway MySQL环境变量"""
    print_section("Railway MySQL环境变量检查")
    
    # Railway MySQL变量
    mysql_vars = {
        "MYSQL_DATABASE": "数据库名称",
        "MYSQL_PUBLIC_URL": "公共连接URL",
        "MYSQL_ROOT_PASSWORD": "root密码",
        "MYSQL_URL": "私有连接URL",
        "MYSQLDATABASE": "数据库名称（别名）",
        "MYSQLHOST": "MySQL主机",
        "MYSQLPASSWORD": "MySQL密码",
        "MYSQLPORT": "MySQL端口",
        "MYSQLUSER": "MySQL用户"
    }
    
    print("📋 Railway MySQL变量:")
    for var, description in mysql_vars.items():
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var:
                print(f"  ✅ {var} ({description}): {'*' * len(value)}")
            else:
                print(f"  ✅ {var} ({description}): {value}")
        else:
            print(f"  ❌ {var} ({description}): 未设置")

def check_template_variables():
    """检查模板变量"""
    print_section("模板变量检查")
    
    template_vars = [
        "MYSQL_DATABASE", "MYSQL_PUBLIC_URL", "MYSQL_ROOT_PASSWORD",
        "MYSQL_URL", "MYSQLDATABASE", "MYSQLHOST", "MYSQLPASSWORD",
        "MYSQLPORT", "MYSQLUSER"
    ]
    
    print("🔍 检查模板变量:")
    for var in template_vars:
        value = os.getenv(var)
        if value and "${{" in str(value):
            print(f"  ⚠️  {var}: 包含模板变量 {value}")
        elif value:
            print(f"  ✅ {var}: 已解析为实际值")
        else:
            print(f"  ❌ {var}: 未设置")

def build_database_config():
    """构建数据库配置"""
    print_section("数据库配置构建")
    
    # 获取环境变量
    mysql_host = os.getenv("MYSQLHOST")
    mysql_port = os.getenv("MYSQLPORT", "3306")
    mysql_user = os.getenv("MYSQLUSER", "root")
    mysql_password = os.getenv("MYSQLPASSWORD")
    mysql_database = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE", "worklog")
    
    print("🔧 配置构建过程:")
    print(f"  主机: {mysql_host}")
    print(f"  端口: {mysql_port}")
    print(f"  用户: {mysql_user}")
    print(f"  数据库: {mysql_database}")
    print(f"  密码: {'*' * len(mysql_password) if mysql_password else '未设置'}")
    
    # 检查配置有效性
    if not mysql_host or "${{" in str(mysql_host):
        print("  ❌ 主机配置无效或包含模板变量")
        return None
    
    if not mysql_password or "${{" in str(mysql_password):
        print("  ❌ 密码配置无效或包含模板变量")
        return None
    
    config = {
        "host": mysql_host,
        "port": mysql_port,
        "user": mysql_user,
        "password": mysql_password,
        "database": mysql_database
    }
    
    print("  ✅ 配置构建成功")
    return config

def test_database_connection(config):
    """测试数据库连接"""
    if not config:
        print("❌ 无法测试连接：配置无效")
        return False
    
    print_section("数据库连接测试")
    
    # 构建数据库URL
    database_url = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset=utf8mb4"
    print(f"🔗 数据库URL: {database_url.replace(config['password'], '*' * len(config['password']))}")
    
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

def main():
    """主函数"""
    print("🚀 Railway MySQL配置检查工具")
    print("=" * 60)
    
    # 检查Railway MySQL变量
    check_railway_mysql_variables()
    
    # 检查模板变量
    check_template_variables()
    
    # 构建数据库配置
    config = build_database_config()
    
    # 测试数据库连接
    if config:
        connection_ok = test_database_connection(config)
    else:
        connection_ok = False
    
    # 总结
    print_section("检查总结")
    
    if connection_ok:
        print("🎉 Railway MySQL配置正确，连接成功！")
        print("\n📋 建议:")
        print("1. 配置已正确设置")
        print("2. 数据库连接正常")
        print("3. 可以正常使用数据库")
    else:
        print("❌ Railway MySQL配置有问题！")
        print("\n🔧 故障排除建议:")
        print("1. 检查Railway MySQL服务是否已添加到项目")
        print("2. 确认环境变量已正确解析（不包含模板变量）")
        print("3. 验证服务间的网络连接")
        print("4. 检查MySQL服务是否正在运行")
        print("5. 查看Railway控制台中的服务日志")

if __name__ == "__main__":
    main()

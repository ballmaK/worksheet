#!/usr/bin/env python3
"""
测试本地MySQL数据库连接
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

def test_mysql_connection():
    """测试MySQL连接"""
    
    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "lHg03712")
    DB_NAME = os.getenv("DB_NAME", "work_log")
    
    # 构建数据库URL
    database_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    
    print("🔍 测试本地MySQL连接...")
    print(f"📡 主机: {DB_HOST}")
    print(f"🔌 端口: {DB_PORT}")
    print(f"👤 用户: {DB_USER}")
    print(f"🗄️  数据库: {DB_NAME}")
    print(f"🔗 连接URL: {database_url.replace(DB_PASSWORD, '***')}")
    
    try:
        # 创建引擎
        engine = create_engine(database_url, echo=False)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ MySQL连接成功！")
            
            # 检查数据库是否存在
            result = conn.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result.fetchall()]
            
            if DB_NAME in databases:
                print(f"✅ 数据库 '{DB_NAME}' 已存在")
            else:
                print(f"⚠️  数据库 '{DB_NAME}' 不存在，需要创建")
                return False
                
        return True
        
    except OperationalError as e:
        print(f"❌ MySQL连接失败: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 确保MySQL服务正在运行")
        print("2. 检查用户名和密码是否正确")
        print("3. 检查端口是否正确（默认3306）")
        print("4. 确保数据库已创建")
        return False
        
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy错误: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def create_database_if_not_exists():
    """如果数据库不存在则创建"""
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "lHg03712")
    DB_NAME = os.getenv("DB_NAME", "work_log")
    
    # 连接到MySQL服务器（不指定数据库）
    server_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}?charset=utf8mb4"
    
    try:
        engine = create_engine(server_url, echo=False)
        
        with engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result.fetchall()]
            
            if DB_NAME not in databases:
                print(f"📝 创建数据库 '{DB_NAME}'...")
                conn.execute(text(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                print(f"✅ 数据库 '{DB_NAME}' 创建成功！")
            else:
                print(f"✅ 数据库 '{DB_NAME}' 已存在")
                
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 本地MySQL数据库连接测试")
    print("=" * 50)
    
    # 首先尝试创建数据库
    if create_database_if_not_exists():
        # 然后测试连接
        if test_mysql_connection():
            print("\n🎉 本地MySQL配置正确，可以启动应用！")
            sys.exit(0)
        else:
            print("\n💡 请检查MySQL配置后重试")
            sys.exit(1)
    else:
        print("\n💡 无法连接到MySQL服务器，请确保MySQL已安装并运行")
        sys.exit(1)


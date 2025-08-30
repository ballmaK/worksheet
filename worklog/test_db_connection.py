#!/usr/bin/env python3
"""
测试数据库连接的脚本
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def test_db_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    
    # 构建数据库URL
    database_url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    print(f"数据库URL: {database_url.replace(settings.DB_PASSWORD, '***')}")
    
    try:
        # 创建引擎
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # 启用连接前ping
            pool_recycle=3600,   # 1小时后回收连接
            pool_timeout=30,     # 连接超时30秒
            max_overflow=10,     # 最大溢出连接数
            pool_size=5          # 连接池大小
        )
        
        # 测试连接
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ 数据库连接成功!")
            
            # 测试查询用户表
            result = connection.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"✅ 用户表查询成功，用户数量: {user_count}")
            
            # 测试查询团队表
            result = connection.execute(text("SELECT COUNT(*) FROM teams"))
            team_count = result.scalar()
            print(f"✅ 团队表查询成功，团队数量: {team_count}")
            
            # 测试查询团队成员表
            result = connection.execute(text("SELECT COUNT(*) FROM team_members"))
            member_count = result.scalar()
            print(f"✅ 团队成员表查询成功，成员数量: {member_count}")
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    return True

def test_team_queries():
    """测试团队相关查询"""
    print("\n=== 测试团队相关查询 ===")
    
    database_url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # 测试团队查询
            result = db.execute(text("""
                SELECT t.id, t.name, t.description, COUNT(tm.id) as member_count
                FROM teams t
                LEFT JOIN team_members tm ON t.id = tm.team_id
                GROUP BY t.id, t.name, t.description
            """))
            
            teams = result.fetchall()
            print(f"✅ 团队查询成功，找到 {len(teams)} 个团队:")
            for team in teams:
                print(f"  - 团队ID: {team[0]}, 名称: {team[1]}, 成员数: {team[3]}")
                
    except Exception as e:
        print(f"❌ 团队查询失败: {e}")

if __name__ == "__main__":
    if test_db_connection():
        test_team_queries()
    else:
        print("数据库连接失败，无法进行后续测试")

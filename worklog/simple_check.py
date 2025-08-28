#!/usr/bin/env python3
"""
简单的数据库检查脚本
"""
import pymysql
from app.core.config import settings

def check_database():
    try:
        # 直接连接数据库
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查用户表
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"用户表中共有 {user_count} 条记录")
            
            if user_count > 0:
                # 查询所有用户
                cursor.execute("SELECT id, username, email, role, created_at FROM users")
                users = cursor.fetchall()
                
                print("\n用户列表:")
                for user in users:
                    print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}, 创建时间: {user[4]}")
            
            # 检查特定用户
            test_email = "zkzk-11@163.com"
            cursor.execute("SELECT id, username, email FROM users WHERE email = %s OR username = %s", (test_email, test_email))
            user = cursor.fetchone()
            
            if user:
                print(f"\n找到用户: ID={user[0]}, 用户名={user[1]}, 邮箱={user[2]}")
            else:
                print(f"\n用户 '{test_email}' 不存在")
                
        connection.close()
        
    except Exception as e:
        print(f"数据库连接或查询出错: {e}")

if __name__ == "__main__":
    check_database() 
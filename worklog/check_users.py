#!/usr/bin/env python3
"""
检查数据库中的用户情况
"""
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def check_users():
    db = SessionLocal()
    try:
        # 查询所有用户
        users = db.query(User).all()
        print(f"数据库中共有 {len(users)} 个用户:")
        
        if users:
            for user in users:
                print(f"  ID: {user.id}")
                print(f"  用户名: {user.username}")
                print(f"  邮箱: {user.email}")
                print(f"  角色: {user.role}")
                print(f"  是否激活: {user.is_active}")
                print(f"  创建时间: {user.created_at}")
                print("  ---")
        else:
            print("  数据库中没有用户")
            
        # 检查特定用户是否存在
        test_email = "zkzk-11@163.com"
        test_username = "zkzk-11@163.com"
        
        user_by_email = db.query(User).filter(User.email == test_email).first()
        user_by_username = db.query(User).filter(User.username == test_username).first()
        
        print(f"\n检查用户 '{test_email}':")
        print(f"  按邮箱查找: {'存在' if user_by_email else '不存在'}")
        print(f"  按用户名查找: {'存在' if user_by_username else '不存在'}")
        
        if not user_by_email and not user_by_username:
            print(f"\n用户 '{test_email}' 不存在，需要先注册")
            
    except Exception as e:
        print(f"检查用户时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 
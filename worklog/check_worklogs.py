#!/usr/bin/env python3
"""
检查工作日志数据的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_worklogs():
    # 创建数据库连接
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            # 检查用户
            result = conn.execute(text("SELECT id, username FROM users"))
            users = result.fetchall()
            print(f"用户数量: {len(users)}")
            for user in users:
                print(f"  用户ID: {user[0]}, 用户名: {user[1]}")
            
            # 检查工作日志
            result = conn.execute(text("SELECT id, user_id, work_type, description, start_time, end_time, team_id, project_id, task_id FROM work_logs"))
            worklogs = result.fetchall()
            print(f"\n工作日志数量: {len(worklogs)}")
            
            if worklogs:
                for worklog in worklogs:
                    print(f"  工作日志ID: {worklog[0]}")
                    print(f"    用户ID: {worklog[1]}")
                    print(f"    工作类型: {worklog[2]}")
                    print(f"    描述: {worklog[3]}")
                    print(f"    开始时间: {worklog[4]}")
                    print(f"    结束时间: {worklog[5]}")
                    print(f"    团队ID: {worklog[6]}")
                    print(f"    项目ID: {worklog[7]}")
                    print(f"    任务ID: {worklog[8]}")
                    print("    ---")
            else:
                print("  没有找到工作日志数据")
                
    except Exception as e:
        print(f"检查数据时出错: {e}")

if __name__ == "__main__":
    check_worklogs() 
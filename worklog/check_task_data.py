#!/usr/bin/env python3
"""
检查任务数据和用户团队关系的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember
from app.core.config import TEAM_ADMIN

def check_task_data():
    """检查任务数据和用户团队关系"""
    db = SessionLocal()
    
    try:
        print("=== 检查任务数据 ===")
        
        # 检查所有任务
        tasks = db.query(Task).filter(Task.is_deleted == False).all()
        print(f"数据库中共有 {len(tasks)} 个任务")
        
        for task in tasks:
            print(f"任务ID: {task.id}, 标题: {task.title}, 团队: {task.team_id}, 状态: {task.status}, 负责人: {task.assignee_id}, 创建者: {task.creator_id}")
        
        print("\n=== 检查用户团队关系 ===")
        
        # 检查用户2的团队关系
        user_id = 2
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            print(f"用户: {user.username} (ID: {user.id})")
            
            # 检查用户所在的团队
            memberships = db.query(TeamMember).filter(TeamMember.user_id == user_id).all()
            print(f"用户所在的团队数量: {len(memberships)}")
            
            for member in memberships:
                team = db.query(Team).filter(Team.id == member.team_id).first()
                role_name = "管理员" if member.role == TEAM_ADMIN else "成员"
                print(f"  团队: {team.name if team else 'Unknown'} (ID: {member.team_id}), 角色: {role_name}")
        
        print("\n=== 检查团队1的任务 ===")
        
        # 检查团队1的任务
        team_tasks = db.query(Task).filter(Task.team_id == 1, Task.is_deleted == False).all()
        print(f"团队1共有 {len(team_tasks)} 个任务")
        
        for task in team_tasks:
            print(f"  任务ID: {task.id}, 标题: {task.title}, 状态: {task.status}, 负责人: {task.assignee_id}")
        
        print("\n=== 检查用户2负责的任务 ===")
        
        # 检查用户2负责的任务
        assigned_tasks = db.query(Task).filter(Task.assignee_id == user_id, Task.is_deleted == False).all()
        print(f"用户2负责的任务数量: {len(assigned_tasks)}")
        
        for task in assigned_tasks:
            print(f"  任务ID: {task.id}, 标题: {task.title}, 团队: {task.team_id}, 状态: {task.status}")
        
        print("\n=== 检查用户2创建的任务 ===")
        
        # 检查用户2创建的任务
        created_tasks = db.query(Task).filter(Task.creator_id == user_id, Task.is_deleted == False).all()
        print(f"用户2创建的任务数量: {len(created_tasks)}")
        
        for task in created_tasks:
            print(f"  任务ID: {task.id}, 标题: {task.title}, 团队: {task.team_id}, 状态: {task.status}, 负责人: {task.assignee_id}")
        
    except Exception as e:
        print(f"检查数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_task_data() 
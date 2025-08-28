#!/usr/bin/env python3
"""
测试所有通知场景
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.team import Team
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.project import Project
from app.models.work_log import WorkLog
from app.core.message_service import message_push_service

async def test_all_notifications():
    """测试所有通知场景"""
    db = SessionLocal()
    
    try:
        print("=== 开始测试所有通知场景 ===\n")
        
        # 获取测试用户
        users = db.query(User).limit(3).all()
        if len(users) < 2:
            print("❌ 需要至少2个用户来测试通知")
            return
        
        user1, user2 = users[0], users[1]
        print(f"使用测试用户: {user1.username}, {user2.username}\n")
        
        # 1. 测试任务创建通知
        print("1. 测试任务创建通知...")
        test_task = Task(
            title="测试任务 - 通知测试",
            description="这是一个用于测试通知的任务",
            creator_id=user1.id,
            assignee_id=user2.id,
            team_id=1,
            project_id=1,
            priority=TaskPriority.HIGH.value,
            status=TaskStatus.PENDING.value
        )
        db.add(test_task)
        db.flush()
        
        await message_push_service.notify_task_created(db, test_task, user1.id)
        print("✅ 任务创建通知已发送\n")
        
        # 2. 测试任务分配通知
        print("2. 测试任务分配通知...")
        await message_push_service.notify_task_assigned(db, test_task, user2.id, user1.id)
        print("✅ 任务分配通知已发送\n")
        
        # 3. 测试任务状态变更通知
        print("3. 测试任务状态变更通知...")
        test_task.status = TaskStatus.IN_PROGRESS.value
        db.add(test_task)
        db.flush()
        
        await message_push_service.notify_task_status_changed(
            db, test_task, TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value, user2.id
        )
        print("✅ 任务状态变更通知已发送\n")
        
        # 4. 测试任务完成通知
        print("4. 测试任务完成通知...")
        test_task.status = TaskStatus.COMPLETED.value
        db.add(test_task)
        db.flush()
        
        await message_push_service.notify_task_completed(db, test_task, user2.id)
        print("✅ 任务完成通知已发送\n")
        
        # 5. 测试任务评论通知
        print("5. 测试任务评论通知...")
        await message_push_service.notify_task_comment_added(db, test_task, 1, user1.id)
        print("✅ 任务评论通知已发送\n")
        
        # 6. 测试任务截止提醒
        print("6. 测试任务截止提醒...")
        test_task.due_date = "2024-12-31"
        db.add(test_task)
        db.flush()
        
        await message_push_service.notify_task_due_reminder(db, test_task, 3)
        print("✅ 任务截止提醒已发送\n")
        
        # 7. 测试项目创建通知
        print("7. 测试项目创建通知...")
        test_project = Project(
            name="测试项目 - 通知测试",
            description="这是一个用于测试通知的项目",
            creator_id=user1.id,
            team_id=1
        )
        db.add(test_project)
        db.flush()
        
        await message_push_service.notify_project_created(db, test_project, user1.id)
        print("✅ 项目创建通知已发送\n")
        
        # 8. 测试项目状态变更通知
        print("8. 测试项目状态变更通知...")
        test_project.status = "in_progress"
        db.add(test_project)
        db.flush()
        
        await message_push_service.notify_project_status_changed(
            db, test_project, "planning", "in_progress", user1.id
        )
        print("✅ 项目状态变更通知已发送\n")
        
        # 9. 测试团队邀请通知
        print("9. 测试团队邀请通知...")
        await message_push_service.notify_team_invitation(db, 1, user1.id, user2.id)
        print("✅ 团队邀请通知已发送\n")
        
        # 10. 测试团队成员加入通知
        print("10. 测试团队成员加入通知...")
        await message_push_service.notify_team_member_joined(db, 1, user2.id)
        print("✅ 团队成员加入通知已发送\n")
        
        # 11. 测试团队成员离开通知
        print("11. 测试团队成员离开通知...")
        await message_push_service.notify_team_member_left(db, 1, user2.id)
        print("✅ 团队成员离开通知已发送\n")
        
        # 12. 测试工作日志提交通知
        print("12. 测试工作日志提交通知...")
        test_worklog = WorkLog(
            user_id=user1.id,
            work_type="feature",
            content="测试工作日志内容",
            start_time="2024-01-01T09:00:00",
            end_time="2024-01-01T11:00:00",
            duration=2.0,
            team_id=1,
            project_id=1
        )
        db.add(test_worklog)
        db.flush()
        
        await message_push_service.notify_worklog_submitted(db, test_worklog.id, user1.id, 1)
        print("✅ 工作日志提交通知已发送\n")
        
        # 13. 测试工作日志提醒
        print("13. 测试工作日志提醒...")
        await message_push_service.notify_worklog_reminder(db, user2.id, 1)
        print("✅ 工作日志提醒已发送\n")
        
        # 14. 测试系统维护通知
        print("14. 测试系统维护通知...")
        await message_push_service.notify_system_maintenance(
            db, "系统维护通知", "系统将于今晚进行维护，预计2小时", [user1.id, user2.id]
        )
        print("✅ 系统维护通知已发送\n")
        
        # 15. 测试权限变更通知
        print("15. 测试权限变更通知...")
        await message_push_service.notify_permission_changed(
            db, user2.id, "team_admin", "您已被提升为团队管理员"
        )
        print("✅ 权限变更通知已发送\n")
        
        print("=== 所有通知场景测试完成 ===")
        print("✅ 共测试了15种通知场景")
        print("📧 请检查前端是否收到相应的通知")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_all_notifications()) 
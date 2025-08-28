#!/usr/bin/env python3
"""
测试任务状态变更时自动生成工作日志的功能
"""

import sys
import os
sys.path.append('.')

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.task import Task, TaskStatus
from app.models.work_log import WorkLog
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember
from datetime import datetime

def test_worklog_auto_generation():
    """测试自动生成工作日志功能"""
    db = SessionLocal()
    
    try:
        # 获取测试用户和团队
        user = db.query(User).first()
        team = db.query(Team).first()
        
        if not user or not team:
            print("❌ 需要先创建用户和团队")
            return
        
        # 检查用户是否是团队成员
        member = db.query(TeamMember).filter(
            TeamMember.user_id == user.id,
            TeamMember.team_id == team.id
        ).first()
        
        if not member:
            print("❌ 用户不是团队成员")
            return
        
        print(f"✅ 测试用户: {user.username}")
        print(f"✅ 测试团队: {team.name}")
        
        # 创建测试任务
        task = Task(
            title="测试自动工作日志任务",
            description="这是一个测试任务，用于验证自动生成工作日志功能",
            team_id=team.id,
            creator_id=user.id,
            assignee_id=user.id,
            status=TaskStatus.PENDING,
            priority="medium",
            task_type="feature"
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        print(f"✅ 创建测试任务: {task.title} (ID: {task.id})")
        print(f"   初始状态: {task.status}")
        
        # 测试1: 开始工作
        print("\n🔄 测试1: 开始工作")
        old_status = task.status
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 检查是否自动生成了工作日志
        work_logs = db.query(WorkLog).filter(
            WorkLog.task_id == task.id,
            WorkLog.user_id == user.id
        ).all()
        
        if work_logs:
            print(f"✅ 自动生成了 {len(work_logs)} 条工作日志")
            for log in work_logs:
                print(f"   - {log.description} (状态: {log.work_status})")
        else:
            print("❌ 没有自动生成工作日志")
        
        # 测试2: 完成任务
        print("\n🔄 测试2: 完成任务")
        old_status = task.status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        # 计算工时
        if task.started_at and task.completed_at:
            duration = (task.completed_at - task.started_at).total_seconds() / 3600
            task.actual_hours = duration
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 检查工作日志是否更新
        work_logs = db.query(WorkLog).filter(
            WorkLog.task_id == task.id,
            WorkLog.user_id == user.id
        ).all()
        
        print(f"✅ 任务完成，实际工时: {task.actual_hours:.1f}小时")
        print(f"✅ 共有 {len(work_logs)} 条工作日志")
        
        for log in work_logs:
            print(f"   - {log.description}")
            print(f"     状态: {log.work_status}")
            print(f"     工时: {log.hours_spent:.1f}小时")
            print(f"     进度: {log.progress_percentage}%")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_worklog_auto_generation() 
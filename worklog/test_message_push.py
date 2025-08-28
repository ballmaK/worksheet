#!/usr/bin/env python3
"""
消息推送功能测试脚本
"""
import asyncio
import json
import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.message_service import message_push_service
from app.models.user import User
from app.models.team import Team
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.project import Project

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_message_push():
    """测试消息推送功能"""
    db = SessionLocal()
    try:
        logger.info("开始测试消息推送功能...")
        
        # 获取测试用户
        user = db.query(User).first()
        if not user:
            logger.error("没有找到测试用户")
            return
        
        logger.info(f"使用测试用户: {user.username} (ID: {user.id})")
        
        # 获取用户所在团队
        team = db.query(Team).first()
        if not team:
            logger.error("没有找到测试团队")
            return
        
        logger.info(f"使用测试团队: {team.name} (ID: {team.id})")
        
        # 测试1: 发送系统通知
        logger.info("测试1: 发送系统通知")
        await message_push_service.send_system_notification(
            db=db,
            title="系统测试通知",
            content="这是一条系统测试通知消息",
            recipients=[user.id],
            notification_type="test"
        )
        
        # 测试2: 创建测试任务并发送通知
        logger.info("测试2: 创建测试任务并发送通知")
        test_task = Task(
            title="测试任务",
            description="这是一个用于测试消息推送的任务",
            team_id=team.id,
            creator_id=user.id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.OTHER,
            actual_hours=0,
            is_deleted=False
        )
        db.add(test_task)
        db.commit()
        db.refresh(test_task)
        
        await message_push_service.notify_task_created(db, test_task)
        
        # 测试3: 发送任务分配通知
        logger.info("测试3: 发送任务分配通知")
        await message_push_service.notify_task_assigned(db, test_task, user.id)
        
        # 测试4: 发送任务状态变更通知
        logger.info("测试4: 发送任务状态变更通知")
        test_task.status = TaskStatus.IN_PROGRESS
        db.commit()
        await message_push_service.notify_task_status_changed(
            db, test_task, "pending", "in_progress"
        )
        
        # 测试5: 创建测试项目并发送通知
        logger.info("测试5: 创建测试项目并发送通知")
        test_project = Project(
            name="测试项目",
            description="这是一个用于测试消息推送的项目",
            team_id=team.id,
            creator_id=user.id,
            status="in_progress"
        )
        db.add(test_project)
        db.commit()
        db.refresh(test_project)
        
        await message_push_service.notify_project_created(db, test_project)
        
        logger.info("所有测试完成！")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_message_push()) 
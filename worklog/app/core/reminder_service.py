#!/usr/bin/env python3
"""
提醒服务
用于发送定时通知，如工作日志提醒、任务截止提醒等
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.task import Task
from app.models.work_log import WorkLog
from app.core.message_service import message_push_service

logger = logging.getLogger(__name__)

class ReminderService:
    """提醒服务"""
    
    @staticmethod
    async def send_worklog_reminders():
        """发送工作日志提醒"""
        try:
            db = SessionLocal()
            
            # 获取所有活跃用户
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                # 检查用户今天是否已经提交了工作日志
                today = datetime.now().date()
                existing_worklog = db.query(WorkLog).filter(
                    WorkLog.user_id == user.id,
                    WorkLog.created_at >= today
                ).first()
                
                if not existing_worklog:
                    # 获取用户所在的团队
                    user_teams = db.query(TeamMember).filter(
                        TeamMember.user_id == user.id
                    ).all()
                    
                    for team_member in user_teams:
                        await message_push_service.notify_worklog_reminder(
                            db, user.id, team_member.team_id
                        )
                        logger.info(f"已发送工作日志提醒给用户 {user.username}")
            
            db.close()
            
        except Exception as e:
            logger.error(f"发送工作日志提醒失败: {e}")
    
    @staticmethod
    async def send_task_due_reminders():
        """发送任务截止提醒"""
        try:
            db = SessionLocal()
            
            # 获取即将到期的任务（3天内）
            three_days_later = datetime.now() + timedelta(days=3)
            tasks = db.query(Task).filter(
                Task.due_date <= three_days_later,
                Task.due_date >= datetime.now(),
                Task.status != "completed",
                Task.is_deleted == False
            ).all()
            
            for task in tasks:
                if task.assignee_id:
                    # 计算剩余天数
                    days_remaining = (task.due_date - datetime.now()).days
                    
                    await message_push_service.notify_task_due_reminder(
                        db, task, days_remaining
                    )
                    logger.info(f"已发送任务截止提醒：任务 {task.title}，剩余 {days_remaining} 天")
            
            db.close()
            
        except Exception as e:
            logger.error(f"发送任务截止提醒失败: {e}")
    
    @staticmethod
    async def send_daily_summary():
        """发送每日总结"""
        try:
            db = SessionLocal()
            
            # 获取所有团队
            teams = db.query(Team).all()
            
            for team in teams:
                # 获取团队成员
                members = db.query(TeamMember).filter(
                    TeamMember.team_id == team.id
                ).all()
                
                if members:
                    # 统计今日工作日志
                    today = datetime.now().date()
                    worklog_count = db.query(WorkLog).filter(
                        WorkLog.team_id == team.id,
                        WorkLog.created_at >= today
                    ).count()
                    
                    # 统计今日完成任务
                    completed_tasks = db.query(Task).filter(
                        Task.team_id == team.id,
                        Task.status == "completed",
                        Task.completed_at >= today
                    ).count()
                    
                    # 发送每日总结给团队管理员
                    admin_members = [m for m in members if m.role == "admin"]
                    for admin in admin_members:
                        await message_push_service.send_system_notification(
                            db,
                            f"团队 {team.name} 每日总结",
                            f"今日工作日志：{worklog_count} 条\n今日完成任务：{completed_tasks} 个",
                            [admin.user_id],
                            "daily_summary"
                        )
            
            db.close()
            
        except Exception as e:
            logger.error(f"发送每日总结失败: {e}")
    
    @staticmethod
    async def run_all_reminders():
        """运行所有提醒"""
        logger.info("开始运行定时提醒...")
        
        await asyncio.gather(
            ReminderService.send_worklog_reminders(),
            ReminderService.send_task_due_reminders(),
            ReminderService.send_daily_summary()
        )
        
        logger.info("定时提醒运行完成")

# 创建全局实例
reminder_service = ReminderService() 
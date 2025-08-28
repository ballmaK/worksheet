#!/usr/bin/env python3
"""
重新创建工作日志表，确保枚举值正确
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.work_log import WorkLog
from sqlalchemy import text, drop, create
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_worklog_table():
    """重新创建工作日志表"""
    db = SessionLocal()
    try:
        # 备份现有数据
        logger.info("备份现有工作日志数据...")
        result = db.execute(text("SELECT * FROM work_logs"))
        backup_data = result.fetchall()
        logger.info(f"备份了 {len(backup_data)} 条记录")
        
        # 删除现有表
        logger.info("删除现有工作日志表...")
        db.execute(text("DROP TABLE IF EXISTS work_logs"))
        
        # 重新创建表
        logger.info("重新创建工作日志表...")
        WorkLog.__table__.create(db.bind)
        
        # 恢复数据（如果有的话）
        if backup_data:
            logger.info("恢复工作日志数据...")
            for row in backup_data:
                # 转换枚举值
                work_type = row.work_type
                if work_type in ['dev', 'development']:
                    work_type = 'feature'
                elif work_type in ['test', 'testing', 'bug_fix']:
                    work_type = 'bug'
                elif work_type == 'design':
                    work_type = 'improvement'
                
                # 插入数据
                db.execute(text("""
                    INSERT INTO work_logs (
                        user_id, team_id, project_id, task_id, work_type, 
                        content, details, date, start_time, end_time, 
                        duration, progress_percentage, work_status, 
                        issues_encountered, solutions_applied, blockers, 
                        remark, created_at, updated_at, tags, attachments
                    ) VALUES (
                        :user_id, :team_id, :project_id, :task_id, :work_type,
                        :content, :details, :date, :start_time, :end_time,
                        :duration, :progress_percentage, :work_status,
                        :issues_encountered, :solutions_applied, :blockers,
                        :remark, :created_at, :updated_at, :tags, :attachments
                    )
                """), {
                    'user_id': row.user_id,
                    'team_id': row.team_id,
                    'project_id': row.project_id,
                    'task_id': row.task_id,
                    'work_type': work_type,
                    'content': row.content,
                    'details': row.details,
                    'date': row.date,
                    'start_time': row.start_time,
                    'end_time': row.end_time,
                    'duration': row.duration,
                    'progress_percentage': row.progress_percentage,
                    'work_status': row.work_status,
                    'issues_encountered': row.issues_encountered,
                    'solutions_applied': row.solutions_applied,
                    'blockers': row.blockers,
                    'remark': row.remark,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at,
                    'tags': row.tags,
                    'attachments': row.attachments
                })
            
            logger.info("数据恢复完成")
        
        # 提交更改
        db.commit()
        logger.info("工作日志表重新创建完成！")
        
        # 验证新的枚举值
        logger.info("验证新的枚举值...")
        result = db.execute(text("SELECT work_type, COUNT(*) as count FROM work_logs GROUP BY work_type"))
        for row in result:
            logger.info(f"类型: {row.work_type}, 数量: {row.count}")
        
    except Exception as e:
        logger.error(f"重新创建表失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    recreate_worklog_table() 
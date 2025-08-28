#!/usr/bin/env python3
"""
简单检查工作日志状态数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from sqlalchemy import text
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_worklog_status():
    """检查工作日志状态数据"""
    db = SessionLocal()
    try:
        # 查看当前工作日志状态分布
        logger.info("查看当前工作日志状态分布...")
        result = db.execute(text("""
            SELECT work_status, COUNT(*) as count 
            FROM work_logs 
            GROUP BY work_status
        """))
        
        for row in result:
            logger.info(f"状态: {row.work_status}, 数量: {row.count}")
        
        # 查看具体的工作日志记录
        logger.info("查看具体的工作日志记录...")
        result = db.execute(text("""
            SELECT id, work_status, work_type, content, created_at 
            FROM work_logs 
            ORDER BY created_at DESC 
            LIMIT 5
        """))
        
        for row in result:
            logger.info(f"ID: {row.id}, 状态: {row.work_status}, 类型: {row.work_type}, 内容: {row.content[:50]}...")
        
        # 检查是否有NULL值
        result = db.execute(text("""
            SELECT COUNT(*) as null_count 
            FROM work_logs 
            WHERE work_status IS NULL
        """))
        
        null_count = result.fetchone().null_count
        logger.info(f"NULL状态值数量: {null_count}")
        
        logger.info("检查完成！")
        
    except Exception as e:
        logger.error(f"检查工作日志状态时出错: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    check_worklog_status() 
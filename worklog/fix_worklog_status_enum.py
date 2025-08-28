#!/usr/bin/env python3
"""
修复工作日志状态枚举值
将数据库中的大写状态值更新为小写
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

def fix_worklog_status_enum():
    """修复工作日志状态枚举值"""
    db = SessionLocal()
    try:
        # 查看当前的数据
        logger.info("查看当前工作日志状态分布...")
        result = db.execute(text("""
            SELECT work_status, COUNT(*) as count 
            FROM work_logs 
            GROUP BY work_status
        """))
        
        for row in result:
            logger.info(f"状态: {row.work_status}, 数量: {row.count}")
        
        # 更新大写状态值为小写
        logger.info("开始更新工作日志状态枚举值...")
        
        # 更新大写状态值为小写
        result = db.execute(text("""
            UPDATE work_logs 
            SET work_status = 'in_progress' 
            WHERE work_status = 'IN_PROGRESS'
        """))
        logger.info(f"更新 IN_PROGRESS -> in_progress: {result.rowcount} 条记录")
        
        result = db.execute(text("""
            UPDATE work_logs 
            SET work_status = 'completed' 
            WHERE work_status = 'COMPLETED'
        """))
        logger.info(f"更新 COMPLETED -> completed: {result.rowcount} 条记录")
        
        result = db.execute(text("""
            UPDATE work_logs 
            SET work_status = 'blocked' 
            WHERE work_status = 'BLOCKED'
        """))
        logger.info(f"更新 BLOCKED -> blocked: {result.rowcount} 条记录")
        
        result = db.execute(text("""
            UPDATE work_logs 
            SET work_status = 'on_hold' 
            WHERE work_status = 'ON_HOLD'
        """))
        logger.info(f"更新 ON_HOLD -> on_hold: {result.rowcount} 条记录")
        
        # 提交更改
        db.commit()
        logger.info("数据库更新完成！")
        
        # 验证结果
        logger.info("验证更新结果...")
        result = db.execute(text("""
            SELECT work_status, COUNT(*) as count 
            FROM work_logs 
            GROUP BY work_status
        """))
        
        for row in result:
            logger.info(f"状态: {row.work_status}, 数量: {row.count}")
            
    except Exception as e:
        logger.error(f"修复工作日志状态枚举值时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_worklog_status_enum() 
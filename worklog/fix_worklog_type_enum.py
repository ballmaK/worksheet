#!/usr/bin/env python3
"""
修复工作日志类型枚举值
将数据库中的 'dev' 更新为 'development'
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.work_log import WorkLog
from sqlalchemy import text
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_worklog_type_enum():
    """修复工作日志类型枚举值"""
    db = SessionLocal()
    try:
        # 查看当前的数据
        logger.info("查看当前工作日志类型分布...")
        result = db.execute(text("""
            SELECT work_type, COUNT(*) as count 
            FROM work_logs 
            GROUP BY work_type
        """))
        
        for row in result:
            logger.info(f"类型: {row.work_type}, 数量: {row.count}")
        
        # 更新 'dev' 为 'development'
        logger.info("开始更新 'dev' 为 'development'...")
        result = db.execute(text("""
            UPDATE work_logs 
            SET work_type = 'development' 
            WHERE work_type = 'dev'
        """))
        
        updated_count = result.rowcount
        logger.info(f"更新了 {updated_count} 条记录")
        
        # 查看更新后的数据
        logger.info("查看更新后的工作日志类型分布...")
        result = db.execute(text("""
            SELECT work_type, COUNT(*) as count 
            FROM work_logs 
            GROUP BY work_type
        """))
        
        for row in result:
            logger.info(f"类型: {row.work_type}, 数量: {row.count}")
        
        # 提交更改
        db.commit()
        logger.info("修复完成！")
        
    except Exception as e:
        logger.error(f"修复失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_worklog_type_enum() 
#!/usr/bin/env python3
"""
测试枚举修复是否有效
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.work_log import WorkLog, WorkLogType, WorkLogStatus
from sqlalchemy import text
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enum_fix():
    """测试枚举修复"""
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
        
        # 查看当前工作日志类型分布
        logger.info("查看当前工作日志类型分布...")
        result = db.execute(text("""
            SELECT work_type, COUNT(*) as count 
            FROM work_logs 
            GROUP BY work_type
        """))
        
        for row in result:
            logger.info(f"类型: {row.work_type}, 数量: {row.count}")
        
        # 尝试创建一个新的工作日志来测试默认值
        logger.info("测试创建新工作日志...")
        test_work_log = WorkLog(
            user_id=1,  # 假设用户ID为1
            content="测试工作日志",
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        logger.info(f"默认work_type: {test_work_log.work_type}")
        logger.info(f"默认work_status: {test_work_log.work_status}")
        
        logger.info("枚举修复测试完成！")
        
    except Exception as e:
        logger.error(f"测试枚举修复时出错: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    test_enum_fix() 
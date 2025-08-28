#!/usr/bin/env python3
"""
统一工作日志类型枚举值
将旧的枚举值更新为新的统一枚举值
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

def fix_worklog_type_enum_unified():
    """统一工作日志类型枚举值"""
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
        
        # 更新旧的枚举值为新的统一枚举值
        logger.info("开始更新工作日志类型枚举值...")
        
        # 映射关系：旧值 -> 新值
        enum_mapping = {
            'dev': 'feature',           # 开发 -> 功能开发
            'development': 'feature',   # 开发 -> 功能开发
            'test': 'bug',              # 测试 -> Bug修复
            'testing': 'bug',           # 测试 -> Bug修复
            'bug_fix': 'bug',           # Bug修复 -> Bug修复
            'design': 'improvement',    # 设计 -> 改进优化
            'documentation': 'documentation',  # 文档 -> 文档工作
            'meeting': 'meeting',       # 会议 -> 会议
            'research': 'research',     # 调研 -> 调研
            'other': 'other'            # 其他 -> 其他
        }
        
        total_updated = 0
        for old_value, new_value in enum_mapping.items():
            if old_value != new_value:  # 只更新需要修改的值
                result = db.execute(text("""
                    UPDATE work_logs 
                    SET work_type = :new_value 
                    WHERE work_type = :old_value
                """), {"new_value": new_value, "old_value": old_value})
                
                updated_count = result.rowcount
                if updated_count > 0:
                    logger.info(f"更新 {old_value} -> {new_value}: {updated_count} 条记录")
                    total_updated += updated_count
        
        logger.info(f"总共更新了 {total_updated} 条记录")
        
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
        logger.info("枚举值统一完成！")
        
    except Exception as e:
        logger.error(f"修复失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_worklog_type_enum_unified() 
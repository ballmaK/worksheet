#!/usr/bin/env python3
"""
数据库修复脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_database():
    """修复数据库问题"""
    print("开始修复数据库...")
    
    # 创建数据库连接
    database_url = settings.SQLALCHEMY_DATABASE_URL
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        try:
            # 修复任务状态字段
            print("修复任务状态字段...")
            conn.execute(text("""
                ALTER TABLE tasks MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'
            """))
            print("✓ 任务状态字段修复完成")
            
            # 提交更改
            conn.commit()
            print("✓ 数据库修复完成")
            
        except Exception as e:
            print(f"✗ 修复失败: {e}")
            conn.rollback()

if __name__ == "__main__":
    fix_database() 
#!/usr/bin/env python3
"""
修复任务状态字段长度问题的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_task_status_field():
    """修复任务状态字段长度"""
    # 创建数据库连接
    if settings.USE_SQLITE:
        database_url = f"sqlite:///{settings.SQLITE_DB_PATH}"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
    else:
        database_url = settings.DATABASE_URL
        engine = create_engine(database_url)
    
    with engine.connect() as conn:
        try:
            # 检查当前字段类型
            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'status'
            """))
            current_field = result.fetchone()
            
            if current_field:
                print(f"当前status字段类型: {current_field}")
                
                # 修改字段类型为VARCHAR(20)以支持所有状态值
                conn.execute(text("""
                    ALTER TABLE tasks MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'
                """))
                print("已修改status字段为VARCHAR(20)")
            else:
                print("未找到tasks表的status字段")
                
        except Exception as e:
            print(f"修复失败: {e}")
            # 如果是SQLite，使用不同的语法
            if settings.USE_SQLITE:
                try:
                    # SQLite不支持直接修改列类型，需要重建表
                    print("SQLite数据库，需要重建表结构...")
                    # 这里可以添加SQLite的重建逻辑
                except Exception as e2:
                    print(f"SQLite修复也失败: {e2}")
        
        conn.commit()

if __name__ == "__main__":
    print("开始修复任务状态字段...")
    fix_task_status_field()
    print("修复完成！") 
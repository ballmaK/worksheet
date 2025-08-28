#!/usr/bin/env python3
"""
数据库字段名称修改脚本
将description字段改为content，将hours_spent字段改为duration
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def apply_field_changes():
    """应用字段名称修改"""
    try:
        # 创建数据库连接
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
        
        with engine.connect() as conn:
            print("正在修改数据库字段名称...")
            
            # 检查字段是否存在
            result = conn.execute(text("DESCRIBE work_logs"))
            columns = [row[0] for row in result.fetchall()]
            
            # 修改description字段为content
            if 'description' in columns:
                print("正在将description字段改为content...")
                conn.execute(text("ALTER TABLE work_logs CHANGE COLUMN description content TEXT NOT NULL"))
                print("✓ description字段已改为content")
            else:
                print("✓ content字段已存在")
            
            # 修改hours_spent字段为duration
            if 'hours_spent' in columns:
                print("正在将hours_spent字段改为duration...")
                conn.execute(text("ALTER TABLE work_logs CHANGE COLUMN hours_spent duration FLOAT NOT NULL DEFAULT 0.0"))
                print("✓ hours_spent字段已改为duration")
            else:
                print("✓ duration字段已存在")
            
            # 添加title字段（如果不存在）
            if 'title' not in columns:
                print("正在添加title字段...")
                conn.execute(text("ALTER TABLE work_logs ADD COLUMN title VARCHAR(255) NULL"))
                print("✓ title字段已添加")
                
                # 更新title字段，使用content作为默认值
                conn.execute(text("UPDATE work_logs SET title = content WHERE title IS NULL OR title = ''"))
                print("✓ title字段已更新")
            else:
                print("✓ title字段已存在")
            
            # 提交更改
            conn.commit()
            
            print("\n数据库字段修改完成！")
            
            # 显示修改后的表结构
            print("\n修改后的表结构：")
            result = conn.execute(text("DESCRIBE work_logs"))
            for row in result.fetchall():
                print(f"  {row[0]} - {row[1]}")
                
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_field_changes() 
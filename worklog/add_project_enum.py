#!/usr/bin/env python3
"""
向数据库添加project枚举值
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.session import SessionLocal

def add_project_enum():
    """向数据库添加project枚举值"""
    db = SessionLocal()
    
    try:
        print("=== 开始添加project枚举值 ===\n")
        
        # 1. 修改messages表的message_type字段
        print("1. 修改messages表的message_type字段...")
        sql1 = """
        ALTER TABLE messages 
        MODIFY COLUMN message_type ENUM('task','team','worklog','system','user','project') NOT NULL
        """
        db.execute(text(sql1))
        print("✅ messages表修改完成\n")
        
        # 2. 修改message_templates表的message_type字段
        print("2. 修改message_templates表的message_type字段...")
        sql2 = """
        ALTER TABLE message_templates 
        MODIFY COLUMN message_type ENUM('task','team','worklog','system','user','project') NOT NULL
        """
        db.execute(text(sql2))
        print("✅ message_templates表修改完成\n")
        
        # 3. 验证修改结果
        print("3. 验证修改结果...")
        verify_sql = """
        SELECT COLUMN_NAME, COLUMN_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'worksheet' 
        AND TABLE_NAME = 'messages' 
        AND COLUMN_NAME = 'message_type'
        """
        result = db.execute(text(verify_sql)).fetchone()
        if result:
            print(f"✅ messages.message_type字段类型: {result[1]}")
        else:
            print("⚠️ 无法获取字段信息，但修改可能已成功")
        
        # 4. 提交事务
        db.commit()
        print("\n=== 所有修改完成 ===")
        print("✅ project枚举值已成功添加到数据库")
        
    except Exception as e:
        print(f"❌ 修改过程中发生错误: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    add_project_enum() 
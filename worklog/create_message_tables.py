#!/usr/bin/env python3
"""
创建消息相关表的数据库迁移脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models.message import Message, MessageTemplate

def create_message_tables():
    """创建消息相关表"""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    
    try:
        # 创建消息表
        print("创建消息表...")
        Message.__table__.create(engine, checkfirst=True)
        print("✓ 消息表创建成功")
        
        # 创建消息模板表
        print("创建消息模板表...")
        MessageTemplate.__table__.create(engine, checkfirst=True)
        print("✓ 消息模板表创建成功")
        
        # 初始化默认模板
        print("初始化默认消息模板...")
        from app.core.message_service import message_service
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        try:
            message_service.initialize_templates(db)
            print("✓ 默认消息模板初始化成功")
        finally:
            db.close()
        
        print("\n🎉 消息系统数据库迁移完成！")
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_message_tables() 
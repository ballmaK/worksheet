#!/usr/bin/env python3
"""
数据库连接重置工具
用于修复损坏的MySQL连接
"""

import logging
import time
from sqlalchemy import create_engine, text
from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database_connection():
    """
    重置数据库连接
    """
    logger.info("开始重置数据库连接...")
    
    try:
        # 创建新的引擎
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URL,
            poolclass=None,  # 不使用连接池
            connect_args={
                "charset": "utf8mb4",
                "read_timeout": 60,
                "write_timeout": 60,
                "connect_timeout": 60,
                "autocommit": True
            }
        )
        
        # 测试连接
        with engine.connect() as connection:
            logger.info("测试数据库连接...")
            result = connection.execute(text("SELECT 1"))
            logger.info(f"连接测试成功: {result.fetchone()}")
            
            # 重置连接状态
            logger.info("重置连接状态...")
            connection.execute(text("SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'"))
            connection.execute(text("SET SESSION wait_timeout=28800"))
            connection.execute(text("SET SESSION interactive_timeout=28800"))
            
            logger.info("数据库连接重置成功")
            
    except Exception as e:
        logger.error(f"重置数据库连接失败: {e}")
        raise

def test_database_operations():
    """
    测试数据库操作
    """
    logger.info("开始测试数据库操作...")
    
    try:
        from app.db.session import get_db_session
        
        with get_db_session() as db:
            # 测试简单查询
            from app.models.user import User
            users = db.query(User).limit(5).all()
            logger.info(f"成功查询到 {len(users)} 个用户")
            
            # 测试任务查询
            from app.models.task import Task
            tasks = db.query(Task).limit(5).all()
            logger.info(f"成功查询到 {len(tasks)} 个任务")
            
        logger.info("数据库操作测试成功")
        
    except Exception as e:
        logger.error(f"数据库操作测试失败: {e}")
        raise

if __name__ == "__main__":
    try:
        # 重置连接
        reset_database_connection()
        
        # 等待一下
        time.sleep(2)
        
        # 测试操作
        test_database_operations()
        
        logger.info("数据库连接重置和测试完成")
        
    except Exception as e:
        logger.error(f"操作失败: {e}")
        exit(1) 
#!/usr/bin/env python3
"""
创建数据库脚本
"""
import pymysql
from app.core.config import settings
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """创建数据库"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4'
        )
        
        logger.info("✅ 连接到MySQL服务器成功")
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"✅ 数据库 {settings.DB_NAME} 创建成功")
            
            # 显示所有数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            logger.info(f"所有数据库: {[db[0] for db in databases]}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建数据库失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 创建数据库 ===")
    create_database() 
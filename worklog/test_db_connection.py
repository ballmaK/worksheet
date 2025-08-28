#!/usr/bin/env python3
"""
数据库连接测试脚本
"""
import pymysql
from app.core.config import settings
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mysql_connection():
    """测试MySQL数据库连接"""
    try:
        logger.info(f"尝试连接到数据库: {settings.DB_HOST}:{settings.DB_PORT}")
        logger.info(f"用户名: {settings.DB_USER}")
        logger.info(f"数据库名: {settings.DB_NAME}")
        
        # 创建连接
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        logger.info("数据库连接成功！")
        
        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"MySQL版本: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logger.info(f"数据库中的表: {[table[0] for table in tables]}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False

def test_without_database():
    """测试不指定数据库的连接"""
    try:
        logger.info("尝试连接不指定数据库...")
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        logger.info("连接成功（不指定数据库）！")
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            logger.info(f"可用的数据库: {[db[0] for db in databases]}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"连接失败（不指定数据库）: {e}")
        return False

if __name__ == "__main__":
    print("=== 数据库连接测试 ===")
    
    # 测试1: 直接连接指定数据库
    print("\n1. 测试直接连接指定数据库:")
    test_mysql_connection()
    
    # 测试2: 连接不指定数据库
    print("\n2. 测试连接不指定数据库:")
    test_without_database() 
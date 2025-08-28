#!/usr/bin/env python3
"""
详细的MySQL连接测试脚本
"""
import pymysql
import socket
from app.core.config import settings
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_ip():
    """获取本地IP地址"""
    try:
        # 连接到外部地址来获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.error(f"获取本地IP失败: {e}")
        return "unknown"

def test_mysql_connection_detailed():
    """详细的MySQL连接测试"""
    local_ip = get_local_ip()
    logger.info(f"本地IP地址: {local_ip}")
    logger.info(f"目标MySQL服务器: {settings.DB_HOST}:{settings.DB_PORT}")
    
    # 测试1: 基本连接
    logger.info("\n=== 测试1: 基本连接 ===")
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4',
            connect_timeout=10
        )
        logger.info("✅ 基本连接成功！")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"❌ 基本连接失败: {e}")
    
    # 测试2: 不指定数据库
    logger.info("\n=== 测试2: 不指定数据库 ===")
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4',
            connect_timeout=10
        )
        logger.info("✅ 连接成功（不指定数据库）！")
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            logger.info(f"可用数据库: {[db[0] for db in databases]}")
            
            cursor.execute("SELECT USER(), @@hostname")
            user_info = cursor.fetchone()
            logger.info(f"当前用户和主机: {user_info}")
        
        connection.close()
        return True
    except Exception as e:
        logger.error(f"❌ 连接失败（不指定数据库）: {e}")
    
    # 测试3: 使用不同的连接参数
    logger.info("\n=== 测试3: 使用SSL=False ===")
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4',
            ssl={'ssl': {}},
            connect_timeout=10
        )
        logger.info("✅ SSL连接成功！")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"❌ SSL连接失败: {e}")
    
    # 测试4: 尝试不同的用户权限
    logger.info("\n=== 测试4: 检查用户权限 ===")
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT User, Host FROM mysql.user WHERE User = %s", (settings.DB_USER,))
            users = cursor.fetchall()
            logger.info(f"用户 {settings.DB_USER} 的权限记录: {users}")
            
            cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
            grants = cursor.fetchall()
            logger.info("当前用户权限:")
            for grant in grants:
                logger.info(f"  {grant[0]}")
        
        connection.close()
        return True
    except Exception as e:
        logger.error(f"❌ 权限检查失败: {e}")
    
    return False

if __name__ == "__main__":
    print("=== 详细MySQL连接测试 ===")
    test_mysql_connection_detailed() 
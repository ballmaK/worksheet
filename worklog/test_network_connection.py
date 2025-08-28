#!/usr/bin/env python3
"""
网络连接测试脚本
"""
import socket
import pymysql
import time
from app.core.config import settings
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_network_connection():
    """测试网络连接"""
    logger.info("=== 网络连接测试 ===")
    
    # 测试1: 获取本地IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        logger.info(f"本地IP: {local_ip}")
    except Exception as e:
        logger.error(f"获取本地IP失败: {e}")
        return
    
    # 测试2: 创建新的socket连接
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((settings.DB_HOST, settings.DB_PORT))
        if result == 0:
            logger.info("✅ Socket连接成功")
            # 获取socket的本地地址
            local_addr = sock.getsockname()
            logger.info(f"Socket本地地址: {local_addr}")
        else:
            logger.error(f"❌ Socket连接失败，错误码: {result}")
        sock.close()
    except Exception as e:
        logger.error(f"❌ Socket连接异常: {e}")
    
    # 测试3: 强制创建新的MySQL连接
    logger.info("\n=== 测试MySQL连接 ===")
    try:
        # 使用不同的连接参数
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4',
            connect_timeout=10,
            read_timeout=10,
            write_timeout=10,
            autocommit=True
        )
        
        logger.info("✅ MySQL连接成功")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT USER(), @@hostname, @@port")
            info = cursor.fetchone()
            logger.info(f"MySQL连接信息: {info}")
            
            cursor.execute("SHOW VARIABLES LIKE 'bind_address'")
            bind_info = cursor.fetchone()
            logger.info(f"MySQL绑定地址: {bind_info}")
        
        connection.close()
        
    except Exception as e:
        logger.error(f"❌ MySQL连接失败: {e}")

def test_multiple_connections():
    """测试多次连接"""
    logger.info("\n=== 多次连接测试 ===")
    
    for i in range(3):
        logger.info(f"第 {i+1} 次连接测试:")
        try:
            connection = pymysql.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                charset='utf8mb4',
                connect_timeout=5
            )
            logger.info(f"✅ 第 {i+1} 次连接成功")
            connection.close()
            time.sleep(1)  # 等待1秒
        except Exception as e:
            logger.error(f"❌ 第 {i+1} 次连接失败: {e}")

if __name__ == "__main__":
    test_network_connection()
    test_multiple_connections() 
#!/usr/bin/env python3
"""
WorkLog Pro 后端启动脚本
包含依赖检查、数据库连接测试和服务器启动
"""

import subprocess
import sys
import os
import time
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖是否已安装"""
    logger.info("检查Python依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy", 
        "pymysql",
        "redis",
        "jinja2",
        "fastapi_mail",
        "websockets"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} 已安装")
        except ImportError:
            logger.error(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"缺少以下依赖: {', '.join(missing_packages)}")
        logger.info("请运行以下命令安装依赖:")
        logger.info("python install_dependencies.py")
        return False
    
    logger.info("✅ 所有依赖检查通过")
    return True

def check_database_connection():
    """检查数据库连接"""
    logger.info("检查数据库连接...")
    
    try:
        from app.core.config import settings
        from app.db.session import engine
        from sqlalchemy import text
        
        # 测试数据库连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ 数据库连接成功")
            return True
            
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        logger.info("请检查数据库配置 (app/core/config.py)")
        logger.info("确保MySQL服务正在运行")
        return False

def check_redis_connection():
    """检查Redis连接"""
    logger.info("检查Redis连接...")
    
    try:
        import redis
        from app.core.config import settings
        
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        r.ping()
        logger.info("✅ Redis连接成功")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Redis连接失败: {e}")
        logger.info("Redis不是必需的，但建议安装以提高性能")
        return False

def start_server():
    """启动服务器"""
    logger.info("启动WorkLog Pro后端服务器...")
    
    # 检查是否在正确的目录
    if not os.path.exists("main.py"):
        logger.error("❌ 未找到 main.py 文件")
        logger.info("请确保在 worklog 目录下运行此脚本")
        return False
    
    try:
        # 启动uvicorn服务器
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
        
        logger.info("🚀 启动服务器...")
        logger.info(f"服务器地址: http://localhost:8000")
        logger.info(f"API文档: http://localhost:8000/docs")
        logger.info("按 Ctrl+C 停止服务器")
        
        # 运行服务器
        subprocess.run(cmd)
        return True
        
    except KeyboardInterrupt:
        logger.info("服务器已停止")
        return True
    except Exception as e:
        logger.error(f"启动服务器失败: {e}")
        return False

def main():
    """主函数"""
    print("WorkLog Pro 后端启动工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查数据库连接
    if not check_database_connection():
        return
    
    # 检查Redis连接（可选）
    check_redis_connection()
    
    print("=" * 50)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 
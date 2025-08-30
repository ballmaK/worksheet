#!/usr/bin/env python3
"""
开发环境启动脚本
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import sqlalchemy
        import pymysql
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def run_database_migration():
    """运行数据库迁移"""
    try:
        print("🔄 运行数据库迁移...")
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ 数据库迁移完成")
            return True
        else:
            print(f"⚠️  数据库迁移警告: {result.stderr}")
            return True  # 继续运行，即使迁移有警告
    except FileNotFoundError:
        print("⚠️  Alembic未找到，跳过数据库迁移")
        return True
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def start_development_server():
    """启动开发服务器"""
    print("🚀 启动WorkLog Pro开发服务器...")
    
    # 设置环境变量确保使用开发配置
    os.environ["ENVIRONMENT"] = "development"
    
    # 启动uvicorn服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式启用热重载
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    print("🔧 WorkLog Pro 开发环境启动")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 运行数据库迁移
    if not run_database_migration():
        print("💡 数据库迁移失败，但继续启动服务器...")
    
    # 启动开发服务器
    try:
        start_development_server()
    except KeyboardInterrupt:
        print("\n👋 开发服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

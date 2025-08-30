#!/usr/bin/env python3
"""
WorkLog Pro 后端启动脚本（包含调试信息）
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def run_debug():
    """运行调试诊断"""
    print("🔍 运行环境诊断...")
    
    try:
        # 首先检查Railway配置文件
        print("1. 检查Railway配置文件...")
        result = subprocess.run(
            [sys.executable, "check_railway_config.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        print("Railway配置文件检查输出:")
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        # 然后运行Railway MySQL检查
        print("\n2. 检查Railway MySQL配置...")
        result2 = subprocess.run(
            [sys.executable, "check_railway_mysql.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        print("Railway MySQL检查输出:")
        print(result2.stdout)
        if result2.stderr:
            print("错误输出:")
            print(result2.stderr)
        
        # 最后运行通用环境诊断
        print("\n3. 运行通用环境诊断...")
        result3 = subprocess.run(
            [sys.executable, "debug_railway_env.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        print("通用环境诊断输出:")
        print(result3.stdout)
        if result3.stderr:
            print("错误输出:")
            print(result3.stderr)
            
        return result.returncode == 0 and result2.returncode == 0 and result3.returncode == 0
        
    except Exception as e:
        print(f"⚠️  诊断过程中出现错误: {e}")
        return True

def run_migration():
    """运行数据库迁移"""
    print("🔄 检查数据库迁移...")
    
    try:
        # 检查alembic.ini是否存在
        if not Path("alembic.ini").exists():
            print("⚠️  alembic.ini 不存在，跳过迁移")
            return True
        
        # 运行迁移
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ 数据库迁移完成")
            return True
        else:
            print(f"❌ 数据库迁移失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠️  迁移过程中出现错误: {e}")
        print("继续启动服务...")
        return True

def main():
    """主函数"""
    # 获取端口配置
    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"
    
    print(f"🚀 启动 WorkLog Pro 后端服务")
    print(f"主机: {host}")
    print(f"端口: {port}")
    print(f"环境: {os.getenv('NODE_ENV', 'production')}")
    
    # 运行调试诊断
    debug_ok = run_debug()
    
    if not debug_ok:
        print("❌ 环境诊断发现问题，但继续启动服务...")
    
    # 运行数据库迁移
    migration_ok = run_migration()
    
    if not migration_ok:
        print("❌ 数据库迁移失败，但继续启动服务...")
    
    # 启动服务器
    print("🚀 启动FastAPI服务器...")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
WorkLog Pro 后端启动脚本（包含数据库迁移）
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

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
    
    # 运行数据库迁移
    migration_ok = run_migration()
    
    if not migration_ok:
        print("❌ 数据库迁移失败，但继续启动服务...")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

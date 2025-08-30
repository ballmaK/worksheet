#!/usr/bin/env python3
"""
Railway专用启动脚本
集成诊断、数据库迁移和应用启动
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_section(title):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_environment():
    """检查环境变量"""
    print_section("环境检查")
    
    # 检查关键环境变量
    required_vars = ['PORT', 'DB_HOST', 'DB_PASSWORD']
    optional_vars = ['DB_PORT', 'DB_USER', 'DB_NAME', 'SECRET_KEY']
    
    print("📋 必需环境变量:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"  ✅ {var}: {'*' * len(value)}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")
    
    print("\n📋 可选环境变量:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"  ✅ {var}: {'*' * len(value)}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: 未设置（使用默认值）")

def run_database_migration():
    """运行数据库迁移"""
    print_section("数据库迁移")
    
    try:
        print("🔄 运行数据库迁移...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ 数据库迁移成功")
            if result.stdout:
                print(f"输出: {result.stdout}")
        else:
            print(f"❌ 数据库迁移失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 数据库迁移异常: {e}")
        return False
    
    return True

def start_application():
    """启动应用"""
    print_section("启动应用")
    
    # 获取端口
    port = os.getenv("PORT", "8000")
    host = "0.0.0.0"
    
    print(f"🚀 启动 WorkLog Pro 后端服务")
    print(f"主机: {host}")
    print(f"端口: {port}")
    print(f"环境: {os.getenv('RAILWAY_ENVIRONMENT', 'production')}")
    
    # 启动uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=int(port),
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 应用被用户中断")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("🚀 Railway WorkLog Pro 后端启动器")
    print("=" * 60)
    
    # 检查环境
    check_environment()
    
    # 运行数据库迁移
    migration_success = run_database_migration()
    
    if not migration_success:
        print("⚠️  数据库迁移失败，但继续启动应用...")
    
    # 启动应用
    start_application()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
依赖修复脚本
专门处理 WorkLog Pro 后端的依赖安装问题
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def fix_pydantic_issue():
    """修复pydantic编译问题"""
    print("🔧 修复pydantic编译问题...")
    
    # 先卸载可能有问题的pydantic
    run_command("pip uninstall pydantic pydantic-core -y", "卸载pydantic")
    
    # 安装预编译的pydantic
    if not run_command("pip install pydantic==2.4.2 --only-binary=all", "安装预编译pydantic"):
        print("⚠️  尝试安装最新版本pydantic")
        run_command("pip install pydantic", "安装pydantic")
    
    return True

def install_core_deps():
    """安装核心依赖"""
    print("📦 安装核心依赖...")
    
    core_deps = [
        "fastapi",
        "uvicorn",
        "sqlalchemy", 
        "pymysql",
        "requests",
        "python-dotenv",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "alembic"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"安装 {dep}"):
            print(f"⚠️  {dep} 安装失败，尝试使用预编译包")
            run_command(f"pip install {dep} --only-binary=all", f"安装预编译 {dep}")
    
    return True

def install_optional_deps():
    """安装可选依赖"""
    print("📦 安装可选依赖...")
    
    optional_deps = [
        "redis",
        "jinja2",
        "fastapi-mail",
        "websockets",
        "aiofiles"
    ]
    
    for dep in optional_deps:
        run_command(f"pip install {dep}", f"安装 {dep}")
    
    return True

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    test_modules = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pymysql",
        "requests"
    ]
    
    failed = []
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} 导入成功")
        except ImportError as e:
            print(f"❌ {module} 导入失败: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ 以下模块导入失败: {', '.join(failed)}")
        return False
    else:
        print("\n✅ 所有核心模块导入成功！")
        return True

def main():
    """主函数"""
    print("WorkLog Pro 依赖修复工具")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not os.path.exists("main.py"):
        print("❌ 请确保在 worklog 目录下运行此脚本")
        return
    
    # 升级pip
    run_command("python -m pip install --upgrade pip", "升级pip")
    
    # 修复pydantic问题
    fix_pydantic_issue()
    
    # 安装核心依赖
    install_core_deps()
    
    # 安装可选依赖
    install_optional_deps()
    
    # 测试导入
    if test_imports():
        print("\n🎉 依赖修复完成！")
        print("\n现在可以启动服务:")
        print("python start_backend.py")
    else:
        print("\n❌ 依赖修复失败，请检查错误信息")

if __name__ == "__main__":
    main() 
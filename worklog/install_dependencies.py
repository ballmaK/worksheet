#!/usr/bin/env python3
"""
依赖安装脚本
用于自动安装 WorkLog Pro 后端的所有依赖
"""

import subprocess
import sys
import os
import platform

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

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True

def install_core_dependencies():
    """安装核心依赖"""
    print("📦 安装核心依赖...")
    
    # 先安装基础包
    core_packages = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "pymysql",
        "requests",
        "python-dotenv"
    ]
    
    for package in core_packages:
        if not run_command(f"pip install {package}", f"安装 {package}"):
            print(f"⚠️  安装 {package} 失败，继续安装其他包")
    
    return True

def install_optional_dependencies():
    """安装可选依赖"""
    print("📦 安装可选依赖...")
    
    optional_packages = [
        "redis",
        "jinja2",
        "fastapi-mail",
        "websockets",
        "aiofiles"
    ]
    
    for package in optional_packages:
        if not run_command(f"pip install {package}", f"安装 {package}"):
            print(f"⚠️  安装 {package} 失败，这是可选依赖")
    
    return True

def install_test_dependencies():
    """安装测试依赖"""
    print("📦 安装测试依赖...")
    
    test_packages = [
        "pytest",
        "pytest-asyncio",
        "httpx"
    ]
    
    for package in test_packages:
        if not run_command(f"pip install {package}", f"安装 {package}"):
            print(f"⚠️  安装 {package} 失败，测试功能可能不可用")
    
    return True

def install_dependencies():
    """安装依赖"""
    print("🚀 开始安装 WorkLog Pro 后端依赖...")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 升级pip
    if not run_command("python -m pip install --upgrade pip", "升级pip"):
        print("⚠️  pip升级失败，继续安装依赖")
    
    # 分步安装依赖
    print("\n🔧 分步安装依赖...")
    
    # 1. 安装核心依赖
    if not install_core_dependencies():
        print("❌ 核心依赖安装失败")
        return False
    
    # 2. 安装可选依赖
    install_optional_dependencies()
    
    # 3. 安装测试依赖
    install_test_dependencies()
    
    # 检查系统依赖（Windows）
    if platform.system() == "Windows":
        print("🔍 检查Windows系统依赖...")
        print("💡 如果遇到编译错误，请安装 Visual Studio Build Tools")
        print("   下载地址: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("💡 或者使用预编译的wheel包:")
        print("   pip install --only-binary=all package_name")
    
    # 检查系统依赖（Linux）
    elif platform.system() == "Linux":
        print("🔍 检查Linux系统依赖...")
        system_packages = [
            "build-essential",
            "python3-dev",
            "libffi-dev",
            "libssl-dev"
        ]
        for package in system_packages:
            try:
                subprocess.run(f"dpkg -l {package}", shell=True, check=True, capture_output=True)
                print(f"✅ {package} 已安装")
            except subprocess.CalledProcessError:
                print(f"⚠️  {package} 未安装，可能需要手动安装")
    
    # 检查系统依赖（macOS）
    elif platform.system() == "Darwin":
        print("🔍 检查macOS系统依赖...")
        try:
            subprocess.run("xcode-select --print-path", shell=True, check=True, capture_output=True)
            print("✅ Xcode Command Line Tools 已安装")
        except subprocess.CalledProcessError:
            print("⚠️  Xcode Command Line Tools 未安装")
            print("   请运行: xcode-select --install")
    
    print("=" * 50)
    print("✅ 依赖安装完成！")
    return True

def verify_installation():
    """验证安装"""
    print("\n🔍 验证安装...")
    
    # 测试导入主要模块
    test_modules = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "pymysql",
        "requests"
    ]
    
    failed_modules = []
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} 导入成功")
        except ImportError as e:
            print(f"❌ {module} 导入失败: {e}")
            failed_modules.append(module)
    
    # 测试可选模块
    optional_modules = [
        "redis",
        "jinja2",
        "fastapi_mail",
        "websockets"
    ]
    
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} 导入成功")
        except ImportError:
            print(f"⚠️  {module} 未安装（可选）")
    
    if failed_modules:
        print(f"\n❌ 以下核心模块导入失败: {', '.join(failed_modules)}")
        print("请重新运行安装脚本")
        return False
    else:
        print("\n✅ 所有核心模块导入成功！")
        return True

def main():
    """主函数"""
    print("WorkLog Pro 后端依赖安装工具")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not os.path.exists("main.py"):
        print("❌ 未找到 main.py 文件")
        print("请确保在 worklog 目录下运行此脚本")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return
    
    # 验证安装
    if not verify_installation():
        print("❌ 安装验证失败")
        return
    
    print("\n🎉 安装完成！")
    print("\n下一步操作:")
    print("1. 配置数据库连接 (app/core/config.py)")
    print("2. 运行数据库迁移: python -m alembic upgrade head")
    print("3. 启动后端服务: python start_backend.py")
    print("4. 启动前端服务: cd ../worklog-web && python start_frontend.py")

if __name__ == "__main__":
    main() 
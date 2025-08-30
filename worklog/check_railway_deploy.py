#!/usr/bin/env python3
"""
Railway 部署配置检查工具
"""

import os
import sys

def check_required_files():
    """检查必需的部署文件"""
    required_files = [
        'main.py',
        'requirements-minimal.txt',
        'railway.json',
        'nixpacks.toml',
        'Procfile',
        'runtime.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少以下文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ 所有必需文件都存在")
        return True

def check_main_py():
    """检查main.py文件"""
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'FastAPI' in content and 'app' in content:
                print("✅ main.py 文件格式正确")
                return True
            else:
                print("❌ main.py 文件格式不正确")
                return False
    except Exception as e:
        print(f"❌ 无法读取 main.py: {e}")
        return False

def check_requirements():
    """检查requirements文件"""
    try:
        with open('requirements-minimal.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'fastapi' in content.lower() and 'uvicorn' in content.lower():
                print("✅ requirements-minimal.txt 包含必需依赖")
                return True
            else:
                print("❌ requirements-minimal.txt 缺少必需依赖")
                return False
    except Exception as e:
        print(f"❌ 无法读取 requirements-minimal.txt: {e}")
        return False

def check_railway_config():
    """检查Railway配置"""
    try:
        with open('railway.json', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'NIXPACKS' in content and 'uvicorn' in content:
                print("✅ railway.json 配置正确")
                return True
            else:
                print("❌ railway.json 配置不正确")
                return False
    except Exception as e:
        print(f"❌ 无法读取 railway.json: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Railway 部署配置检查")
    print("=" * 50)
    
    checks = [
        check_required_files(),
        check_main_py(),
        check_requirements(),
        check_railway_config()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("🎉 所有检查通过！可以部署到 Railway")
        print("\n📋 部署步骤:")
        print("1. 在 Railway 创建新项目")
        print("2. 连接 GitHub 仓库")
        print("3. 选择 worklog 目录")
        print("4. 配置环境变量")
        print("5. 部署应用")
    else:
        print("❌ 存在配置问题，请修复后重试")
        sys.exit(1)

if __name__ == "__main__":
    main()

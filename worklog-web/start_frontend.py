#!/usr/bin/env python3
"""
WorkLog Pro 前端启动脚本
用于检查和启动前端开发服务器
"""

import subprocess
import sys
import os
import json
import platform
import webbrowser
import time

def check_node_version():
    """检查Node.js版本"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✅ Node.js版本: {version}")
        
        # 检查版本号
        version_parts = version.replace('v', '').split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])
        
        if major < 16:
            print("❌ 需要Node.js 16.0或更高版本")
            return False
        
        return True
    except FileNotFoundError:
        print("❌ 未找到Node.js")
        print("请安装Node.js: https://nodejs.org/")
        return False
    except Exception as e:
        print(f"❌ 检查Node.js版本失败: {e}")
        return False

def check_npm_version():
    """检查npm版本"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✅ npm版本: {version}")
        return True
    except FileNotFoundError:
        print("❌ 未找到npm")
        return False
    except Exception as e:
        print(f"❌ 检查npm版本失败: {e}")
        return False

def check_package_json():
    """检查package.json文件"""
    if not os.path.exists('package.json'):
        print("❌ 未找到package.json文件")
        print("请确保在worklog-web目录下运行此脚本")
        return False
    
    try:
        with open('package.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 项目名称: {data.get('name', 'Unknown')}")
        print(f"✅ 项目版本: {data.get('version', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ 读取package.json失败: {e}")
        return False

def install_dependencies():
    """安装前端依赖"""
    print("📦 检查并安装前端依赖...")
    
    try:
        # 检查node_modules是否存在
        if not os.path.exists('node_modules'):
            print("正在安装依赖...")
            result = subprocess.run(['npm', 'install'], check=True, capture_output=True, text=True)
            print("✅ 依赖安装完成")
        else:
            print("✅ 依赖已安装")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 安装依赖时出错: {e}")
        return False

def start_dev_server():
    """启动开发服务器"""
    print("🚀 启动前端开发服务器...")
    
    try:
        # 启动开发服务器
        cmd = ['npm', 'run', 'dev']
        
        print("=" * 50)
        print("前端服务器启动中...")
        print("服务器地址: http://localhost:5173")
        print("后端API地址: http://localhost:8000")
        print("按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 延迟打开浏览器
        def open_browser():
            time.sleep(3)  # 等待服务器启动
            try:
                webbrowser.open('http://localhost:5173')
                print("🌐 已在浏览器中打开应用")
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print("请手动访问: http://localhost:5173")
        
        # 在新线程中打开浏览器
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 运行开发服务器
        subprocess.run(cmd)
        return True
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
        return True
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return False

def check_backend_server():
    """检查后端服务器是否运行"""
    print("🔍 检查后端服务器...")
    
    try:
        import requests
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务器正在运行")
            return True
        else:
            print("⚠️  后端服务器响应异常")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器")
        print("请确保后端服务器正在运行 (http://localhost:8000)")
        return False
    except ImportError:
        print("⚠️  无法检查后端服务器 (requests模块未安装)")
        return False
    except Exception as e:
        print(f"⚠️  检查后端服务器时出错: {e}")
        return False

def main():
    """主函数"""
    print("WorkLog Pro 前端启动工具")
    print("=" * 50)
    
    # 检查Node.js
    if not check_node_version():
        return
    
    # 检查npm
    if not check_npm_version():
        return
    
    # 检查package.json
    if not check_package_json():
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 检查后端服务器
    check_backend_server()
    
    print("=" * 50)
    
    # 启动开发服务器
    start_dev_server()

if __name__ == "__main__":
    main() 
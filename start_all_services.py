#!/usr/bin/env python3
"""
WorkLog Pro 完整启动脚本
同时启动前后端服务
"""

import subprocess
import sys
import os
import time
import threading
import signal
import platform

# 全局变量存储进程
backend_process = None
frontend_process = None

def signal_handler(signum, frame):
    """处理中断信号"""
    print("\n🛑 正在停止所有服务...")
    stop_all_services()
    sys.exit(0)

def stop_all_services():
    """停止所有服务"""
    global backend_process, frontend_process
    
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
            print("✅ 后端服务已停止")
        except:
            backend_process.kill()
            print("⚠️  强制停止后端服务")
    
    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
            print("✅ 前端服务已停止")
        except:
            frontend_process.kill()
            print("⚠️  强制停止前端服务")

def check_python_dependencies():
    """检查Python依赖"""
    print("🔍 检查Python依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pymysql"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依赖: {', '.join(missing_packages)}")
        print("请运行: cd worklog && python install_dependencies.py")
        return False
    
    return True

def check_node_dependencies():
    """检查Node.js依赖"""
    print("🔍 检查Node.js依赖...")
    
    # 检查Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js 未安装")
        print("请安装Node.js: https://nodejs.org/")
        return False
    
    # 检查npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ npm 未安装")
        return False
    
    return True

def start_backend_service():
    """启动后端服务"""
    global backend_process
    
    print("🚀 启动后端服务...")
    
    try:
        # 切换到后端目录
        os.chdir('worklog')
        
        # 启动后端服务
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        backend_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        print("✅ 后端服务启动成功")
        print("📡 后端地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return False

def start_frontend_service():
    """启动前端服务"""
    global frontend_process
    
    print("🚀 启动前端服务...")
    
    try:
        # 切换到前端目录
        os.chdir('worklog-web')
        
        # 检查依赖是否已安装
        if not os.path.exists('node_modules'):
            print("📦 安装前端依赖...")
            subprocess.run(['npm', 'install'], check=True, capture_output=True)
        
        # 启动前端服务
        cmd = ['npm', 'run', 'dev']
        
        frontend_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        print("✅ 前端服务启动成功")
        print("🌐 前端地址: http://localhost:5173")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动前端服务失败: {e}")
        return False

def monitor_services():
    """监控服务状态"""
    while True:
        time.sleep(10)
        
        # 检查后端服务
        if backend_process and backend_process.poll() is not None:
            print("❌ 后端服务已停止")
            break
        
        # 检查前端服务
        if frontend_process and frontend_process.poll() is not None:
            print("❌ 前端服务已停止")
            break

def main():
    """主函数"""
    print("WorkLog Pro 完整启动工具")
    print("=" * 60)
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查依赖
    if not check_python_dependencies():
        return
    
    if not check_node_dependencies():
        return
    
    print("=" * 60)
    
    # 启动后端服务
    if not start_backend_service():
        print("❌ 后端服务启动失败")
        return
    
    # 等待后端服务启动
    print("⏳ 等待后端服务启动...")
    time.sleep(3)
    
    # 启动前端服务
    if not start_frontend_service():
        print("❌ 前端服务启动失败")
        stop_all_services()
        return
    
    print("=" * 60)
    print("🎉 所有服务启动成功！")
    print("📱 前端应用: http://localhost:5173")
    print("🔧 后端API: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 60)
    print("按 Ctrl+C 停止所有服务")
    print("=" * 60)
    
    try:
        # 监控服务状态
        monitor_services()
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号")
    finally:
        stop_all_services()
        print("👋 所有服务已停止")

if __name__ == "__main__":
    main() 
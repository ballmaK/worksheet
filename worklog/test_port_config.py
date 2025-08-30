#!/usr/bin/env python3
"""
端口配置测试脚本
"""

import os
import sys

def test_port_configuration():
    """测试端口配置"""
    print("🔍 端口配置测试")
    print("=" * 30)
    
    # 获取端口配置
    port = os.getenv("PORT", "8000")
    host = "0.0.0.0"
    
    print(f"主机: {host}")
    print(f"端口: {port}")
    
    # 验证端口是否为数字
    try:
        port_int = int(port)
        if 1 <= port_int <= 65535:
            print(f"✅ 端口配置有效: {port_int}")
            return True
        else:
            print(f"❌ 端口超出范围: {port_int}")
            return False
    except ValueError:
        print(f"❌ 端口格式无效: {port}")
        return False

def check_environment_variables():
    """检查环境变量"""
    print("\n🔍 环境变量检查")
    print("=" * 30)
    
    # 检查PORT变量
    port = os.getenv("PORT")
    if port:
        print(f"✅ PORT: {port}")
    else:
        print("⚠️  PORT: 未设置（将使用默认值8000）")
    
    # 检查其他重要变量
    important_vars = [
        "MYSQLHOST", "MYSQLPORT", "MYSQLUSER", 
        "MYSQLPASSWORD", "MYSQLDATABASE"
    ]
    
    for var in important_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value if var != 'MYSQLPASSWORD' else '*' * len(value)}")
        else:
            print(f"❌ {var}: 未设置")
    
    return True

def main():
    """主函数"""
    print("🚀 端口配置测试工具")
    print("=" * 50)
    
    # 检查环境变量
    check_environment_variables()
    
    # 测试端口配置
    port_ok = test_port_configuration()
    
    print("\n" + "=" * 50)
    if port_ok:
        print("🎉 端口配置测试通过！")
        print("\n📋 启动命令:")
        print("uvicorn main:app --host 0.0.0.0 --port $PORT")
        print("\n或者使用启动脚本:")
        print("bash start.sh")
    else:
        print("❌ 端口配置测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()

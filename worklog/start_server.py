#!/usr/bin/env python3
"""
WorkLog Pro 后端启动脚本
"""

import os
import sys
import uvicorn

def main():
    """主函数"""
    # 获取端口配置
    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"
    
    print(f"🚀 启动 WorkLog Pro 后端服务")
    print(f"主机: {host}")
    print(f"端口: {port}")
    print(f"环境: {os.getenv('NODE_ENV', 'production')}")
    
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

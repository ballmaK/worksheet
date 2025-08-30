#!/bin/bash

# 设置环境变量
export PYTHONPATH="."
export PORT=${PORT:-8000}

echo "🚀 启动 WorkLog Pro 后端服务"
echo "端口: $PORT"
echo "主机: 0.0.0.0"

# 启动应用
exec uvicorn main:app --host 0.0.0.0 --port $PORT

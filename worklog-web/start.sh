#!/bin/bash

# 设置环境变量
export NODE_ENV=production
export PORT=${PORT:-3000}

# 构建应用（如果需要）
if [ ! -d "dist" ]; then
    echo "Building application..."
    npm run build
fi

# 启动服务
echo "Starting server on port $PORT..."
npx serve -s dist -l $PORT

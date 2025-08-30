#!/bin/sh

# 获取端口号，默认为80
PORT=${PORT:-80}

echo "🚀 启动 Nginx 服务器"
echo "📡 端口: $PORT"

# 替换nginx.conf中的$PORT为实际端口
sed -i "s/\$PORT/$PORT/g" /etc/nginx/nginx.conf

# 检查nginx配置
echo "🔍 检查 Nginx 配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置检查通过"
    echo "🚀 启动 Nginx..."
    nginx -g "daemon off;"
else
    echo "❌ Nginx 配置检查失败"
    exit 1
fi

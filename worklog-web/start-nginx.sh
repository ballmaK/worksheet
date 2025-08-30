#!/bin/sh

# 获取端口号，默认为80
PORT=${PORT:-80}
# 获取后端URL，默认为您提供的后端地址
BACKEND_URL=${BACKEND_URL:-https://worksheet-backend-production-62f9.up.railway.app}

echo "🚀 启动 Nginx 服务器"
echo "📡 端口: $PORT"
echo "🔗 后端地址: $BACKEND_URL"

# 替换nginx.conf中的$PORT为实际端口
sed -i "s/\$PORT/$PORT/g" /etc/nginx/nginx.conf
# 替换nginx.conf中的$BACKEND_URL为实际后端地址
sed -i "s|\$BACKEND_URL|$BACKEND_URL|g" /etc/nginx/nginx.conf

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

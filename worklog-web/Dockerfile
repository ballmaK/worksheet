# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装所有依赖
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段 - 使用Nginx
FROM nginx:alpine

# 复制构建产物到Nginx目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制启动脚本
COPY start-nginx.sh /start-nginx.sh
RUN chmod +x /start-nginx.sh

# 暴露端口
EXPOSE $PORT

# 启动Nginx
CMD ["/start-nginx.sh"]

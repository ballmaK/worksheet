FROM node:18-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖，因为需要构建）
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 安装serve
RUN npm install -g serve

# 暴露端口
EXPOSE $PORT

# 启动命令
CMD ["serve", "-s", "dist", "-l", "$PORT"]

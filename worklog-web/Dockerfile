FROM node:18-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装所有依赖（使用npm install而不是npm ci，因为package-lock.json可能不同步）
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 暴露端口
EXPOSE $PORT

# 启动命令
CMD ["npm", "start"]

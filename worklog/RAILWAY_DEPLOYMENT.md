# Railway 部署指南

## 概述
本指南将帮助您将 WorkLog Pro 项目部署到 Railway 平台。

## 前置要求
1. 注册 Railway 账户：https://railway.app/
2. 安装 Railway CLI（可选）：`npm install -g @railway/cli`
3. 确保您的代码已推送到 GitHub

## 部署步骤

### 1. 连接 GitHub 仓库
1. 登录 Railway 控制台
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的 WorkLog Pro 仓库
5. 选择 `worklog` 目录作为部署目录

### 2. 配置环境变量
在 Railway 项目设置中添加以下环境变量：

#### 数据库配置
```
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=work_log
```

#### 安全配置
```
SECRET_KEY=your-super-secret-key-here
```

#### Redis 配置（可选）
```
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```

#### 邮件配置（可选）
```
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@163.com
EMAILS_FROM_NAME=WorkLog Pro
```

### 3. 添加数据库服务
1. 在 Railway 项目中点击 "New"
2. 选择 "Database" → "MySQL"
3. 等待数据库创建完成
4. 复制数据库连接信息到环境变量

### 4. 部署
1. Railway 会自动检测到 Python 项目
2. 使用 `railway.json` 和 `nixpacks.toml` 进行构建
3. 部署完成后，您会获得一个公网 URL

## 文件说明

### railway.json
Railway 部署配置文件，定义了构建和启动命令。

### nixpacks.toml
Nixpacks 构建配置，指定了 Python 版本和依赖安装。

### Procfile
定义了应用的启动命令。

### runtime.txt
指定 Python 运行时版本。

## 数据库迁移
部署后，您需要运行数据库迁移：

1. 通过 Railway CLI 连接到服务：
```bash
railway login
railway link
railway shell
```

2. 运行迁移：
```bash
alembic upgrade head
```

## 监控和日志
- 在 Railway 控制台可以查看实时日志
- 可以设置自定义域名
- 支持自动 HTTPS

## 故障排除

### 常见问题
1. **构建失败**：检查 `requirements.txt` 中的依赖版本
2. **数据库连接失败**：确认环境变量配置正确
3. **端口问题**：Railway 会自动设置 `$PORT` 环境变量

### 调试命令
```bash
# 查看日志
railway logs

# 连接到服务
railway shell

# 重启服务
railway restart
```

## 成本
- Railway 提供每月 $5 的免费额度
- 足够运行小型项目
- 超出免费额度后按使用量计费

## 下一步
部署成功后，您可以：
1. 配置自定义域名
2. 设置自动部署
3. 配置监控和告警
4. 集成 CI/CD 流程

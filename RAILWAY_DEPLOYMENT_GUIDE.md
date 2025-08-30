# 🚀 Railway 完整部署指南

## 📋 项目概述

本项目包含两个独立的应用：
- **后端**: `worklog/` - FastAPI + MySQL
- **前端**: `worklog-web/` - Vue.js + TypeScript

## 🎯 部署策略

### 方案一：分别部署（推荐）
- 后端和前端分别部署为独立的Railway服务
- 更好的资源管理和扩展性
- 便于独立维护和更新

### 方案二：单服务部署
- 将前端构建产物部署到后端服务
- 简化部署流程，但灵活性较低

## 🛠️ 部署步骤

### 第一步：部署后端

#### 1. 创建后端项目
1. 登录 Railway 控制台
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的仓库
5. **重要**: 选择 `worklog` 目录作为部署目录

#### 2. 配置后端环境变量
```
# 数据库配置
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=work_log

# 安全配置
SECRET_KEY=your-generated-secret-key

# Redis配置（可选）
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# 邮件配置（可选）
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@163.com
EMAILS_FROM_NAME=WorkLog Pro
```

#### 3. 添加数据库服务
1. 在项目中点击 "New"
2. 选择 "Database" → "MySQL"
3. 等待创建完成
4. 复制连接信息到环境变量

#### 4. 部署后端
- Railway会自动检测Python项目并构建
- 部署完成后获得后端URL，例如：`https://worklog-backend.railway.app`

### 第二步：部署前端

#### 1. 创建前端项目
1. 在Railway中创建新项目
2. 选择相同的GitHub仓库
3. **重要**: 选择 `worklog-web` 目录作为部署目录

#### 2. 配置前端环境变量
```
NODE_ENV=production
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

#### 3. 部署前端
- Railway会自动检测Node.js项目并构建
- 部署完成后获得前端URL，例如：`https://worklog-frontend.railway.app`

## 🔧 配置说明

### 后端配置文件
- `worklog/railway.json` - Railway部署配置
- `worklog/nixpacks.toml` - 构建配置
- `worklog/requirements-minimal.txt` - Python依赖
- `worklog/main.py` - 应用入口

### 前端配置文件
- `worklog-web/railway.json` - Railway部署配置
- `worklog-web/nixpacks.toml` - 构建配置
- `worklog-web/package.json` - Node.js依赖
- `worklog-web/vite.config.ts` - Vite构建配置

## 🔗 服务连接

### 前端连接后端
1. 在Railway前端项目设置中配置环境变量：
   ```
   VITE_API_BASE_URL=https://your-backend-url.railway.app
   ```

2. 前端代码中通过环境变量访问API：
   ```typescript
   const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
   ```

### 数据库连接
1. 后端通过环境变量连接MySQL数据库
2. 确保数据库服务正常运行
3. 运行数据库迁移：`alembic upgrade head`

## 📊 监控和管理

### 后端监控
- 查看API日志和性能
- 监控数据库连接
- 检查错误和异常

### 前端监控
- 查看构建日志
- 监控静态资源加载
- 检查用户访问情况

## 🔄 更新部署

### 后端更新
1. 推送代码到GitHub
2. Railway自动触发重新部署
3. 检查部署日志和健康状态

### 前端更新
1. 推送代码到GitHub
2. Railway自动重新构建和部署
3. 验证前端功能正常

## 🚨 故障排除

### 常见问题

#### 后端部署失败
- 检查Python版本兼容性
- 验证依赖包版本
- 确认环境变量配置

#### 前端构建失败
- 检查Node.js版本
- 验证npm依赖
- 确认构建脚本正确

#### 服务间连接失败
- 验证API URL配置
- 检查CORS设置
- 确认网络连接

### 调试命令
```bash
# 查看后端日志
railway logs --service backend

# 查看前端日志
railway logs --service frontend

# 连接到后端服务
railway shell --service backend

# 重启服务
railway restart --service backend
```

## 💰 成本估算

### 免费额度
- Railway提供每月 $5 免费额度
- 足够运行小型项目

### 资源使用
- 后端：Python应用 + MySQL数据库
- 前端：Node.js应用 + 静态文件服务
- 预计每月成本：$5-15

## 🎉 部署完成

部署成功后，您将获得：
- 后端API服务：`https://worklog-backend.railway.app`
- 前端Web应用：`https://worklog-frontend.railway.app`
- 完整的WorkLog Pro系统

### 下一步
1. 配置自定义域名
2. 设置SSL证书
3. 配置监控告警
4. 设置自动备份
5. 优化性能配置

---

🎯 **提示**: 建议先部署后端，确认API服务正常后再部署前端，这样可以确保前端能正确连接到后端服务。

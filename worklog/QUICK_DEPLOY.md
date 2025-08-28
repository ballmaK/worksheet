# 🚀 Railway 快速部署指南

## 一键部署步骤

### 1. 准备工作 ✅
- [x] 已创建所有必需的部署文件
- [x] Python 版本检查通过 (3.13.3)
- [x] 已生成环境变量模板

### 2. 注册 Railway
访问 https://railway.app/ 注册账户

### 3. 连接 GitHub 仓库
1. 登录 Railway 控制台
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的 WorkLog Pro 仓库
5. **重要**: 选择 `worklog` 目录作为部署目录

### 4. 配置环境变量
在 Railway 项目设置中添加环境变量，参考 `.env.railway` 文件：

#### 必需配置
```
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=work_log
SECRET_KEY=your-generated-secret-key
```

#### 可选配置
```
REDIS_HOST=your-redis-host
SMTP_HOST=smtp.163.com
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-email-password
```

### 5. 添加数据库
1. 在 Railway 项目中点击 "New"
2. 选择 "Database" → "MySQL"
3. 等待创建完成
4. 复制数据库连接信息到环境变量

### 6. 部署
Railway 会自动：
- 检测 Python 项目
- 安装依赖
- 启动应用
- 提供公网 URL

### 7. 数据库迁移
部署完成后，运行数据库迁移：
```bash
# 通过 Railway CLI
railway shell
alembic upgrade head
```

## 部署文件说明

| 文件 | 作用 |
|------|------|
| `railway.json` | Railway 部署配置 |
| `nixpacks.toml` | 构建配置 |
| `Procfile` | 启动命令 |
| `runtime.txt` | Python 版本 |
| `.env.railway` | 环境变量模板 |

## 常见问题

### Q: 构建失败怎么办？
A: 检查 `requirements.txt` 中的依赖版本，确保兼容性。

### Q: 数据库连接失败？
A: 确认环境变量中的数据库连接信息正确。

### Q: 如何查看日志？
A: 在 Railway 控制台的 "Deployments" 标签页查看。

### Q: 如何重启服务？
A: 在 Railway 控制台点击 "Redeploy" 或使用 CLI 命令。

## 成本说明
- 免费额度：每月 $5
- 足够运行小型项目
- 超出后按使用量计费

## 下一步
部署成功后：
1. 配置自定义域名
2. 设置自动部署
3. 配置监控告警
4. 集成 CI/CD

---

🎉 **恭喜！您的 WorkLog Pro 已成功部署到 Railway！**

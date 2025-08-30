# Railway 环境变量配置指南

## 概述

本文档说明如何在Railway上正确配置WorkLog Pro后端的环境变量。

## 必需的环境变量

### 1. MySQL数据库配置

Railway会自动为MySQL服务提供以下环境变量：

```bash
# Railway MySQL服务自动提供的变量
MYSQLHOST=your-mysql-host.railway.app
MYSQLPORT=3306
MYSQLUSER=root
MYSQLPASSWORD=your-mysql-password
MYSQLDATABASE=railway

# 共享MySQL变量（如果使用共享MySQL服务）
MYSQL_DATABASE=railway
MYSQL_PUBLIC_URL=mysql://root:password@host:port/railway
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_URL=mysql://root:password@host:port/railway
```

### 2. 应用配置

```bash
# 应用端口（Railway自动提供）
PORT=8000

# 安全密钥（必需）
SECRET_KEY=your-secret-key-here

# 环境标识
RAILWAY_ENVIRONMENT=production
```

### 3. 可选配置

```bash
# Redis配置（如果使用Redis）
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# 邮件配置
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@163.com
EMAILS_FROM_NAME=WorkLog Pro

# 钉钉配置（可选）
DINGTALK_APP_KEY=your-dingtalk-app-key
DINGTALK_APP_SECRET=your-dingtalk-app-secret
```

## 配置步骤

### 1. 在Railway控制台中配置

1. 进入您的Railway项目
2. 选择后端服务
3. 点击 "Variables" 标签
4. 添加以下变量：

#### 必需变量
```
SECRET_KEY=your-very-secure-secret-key
RAILWAY_ENVIRONMENT=production
```

#### 可选变量
```
# 邮件配置
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@163.com
EMAILS_FROM_NAME=WorkLog Pro

# Redis配置（如果使用）
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

### 2. 连接MySQL服务

1. 在Railway项目中添加MySQL服务
2. 确保后端服务能够访问MySQL服务
3. Railway会自动提供MySQL环境变量

### 3. 验证配置

部署后，检查启动日志中是否显示：

```
🚀 使用生产环境配置
✅ 数据库连接成功！
✅ 数据库迁移完成
```

## 故障排除

### 1. 数据库连接失败

**错误信息：**
```
Can't connect to MySQL server on 'localhost'
```

**解决方案：**
- 确保MySQL服务已添加到Railway项目
- 检查后端服务是否能够访问MySQL服务
- 验证环境变量是否正确设置

### 2. 环境变量未识别

**错误信息：**
```
🔧 使用开发环境配置
```

**解决方案：**
- 确保设置了 `RAILWAY_ENVIRONMENT=production`
- 或者确保MySQL环境变量（如 `MYSQLHOST`）已设置

### 3. 数据库迁移失败

**错误信息：**
```
❌ 数据库迁移失败
```

**解决方案：**
- 检查数据库连接是否正常
- 确保数据库用户有创建表的权限
- 检查alembic配置是否正确

## 测试工具

使用以下命令测试数据库连接：

```bash
python test_db_connection.py
```

这个脚本会：
- 检查所有环境变量
- 测试数据库连接
- 显示详细的连接信息

## 注意事项

1. **安全密钥**：确保 `SECRET_KEY` 是一个强密码，不要使用默认值
2. **数据库权限**：确保MySQL用户有足够的权限创建和修改表
3. **环境隔离**：生产环境和开发环境使用不同的配置
4. **敏感信息**：不要在代码中硬编码敏感信息，始终使用环境变量

## 示例配置

### 完整的生产环境配置示例

```bash
# Railway自动提供的变量
PORT=8000
MYSQLHOST=your-mysql-host.railway.app
MYSQLPORT=3306
MYSQLUSER=root
MYSQLPASSWORD=your-mysql-password
MYSQLDATABASE=railway

# 手动配置的变量
SECRET_KEY=your-very-secure-secret-key-here
RAILWAY_ENVIRONMENT=production
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@163.com
EMAILS_FROM_NAME=WorkLog Pro
```

这个配置应该能让您的WorkLog Pro后端在Railway上正常运行。

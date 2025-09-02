# WorkLog Pro 后端服务

## 📋 项目简介

WorkLog Pro 是一个现代化的团队工作日志管理系统，提供任务管理、时间追踪、团队协作等功能。

## 🚀 快速开始

### 1. 环境要求

- **Python**: 3.8 或更高版本
- **MySQL**: 5.7 或更高版本
- **Redis**: 3.0 或更高版本（可选，用于缓存）
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

### 2. 安装依赖

#### 方法一：使用安装脚本（推荐）

```bash
# 进入后端目录
cd worklog

# 运行安装脚本
python install_dependencies.py
```

#### 方法二：手动安装

```bash
# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `app/core/config.py` 文件，配置数据库连接：

```python
# 数据库配置
DB_HOST: str = "localhost"
DB_PORT: int = 3306
DB_USER: str = "root"
DB_PASSWORD: str = "your_password"
DB_NAME: str = "work_log"
```

### 4. 创建数据库

```sql
CREATE DATABASE work_log CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 运行数据库迁移

```bash
# 初始化迁移
alembic init alembic

# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 6. 启动服务

#### 方法一：使用启动脚本（推荐）

```bash
python start_backend.py
```

#### 方法二：直接启动

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API 文档

启动服务后，可以访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 配置说明

### 环境变量

可以通过环境变量或 `.env` 文件配置：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=work_log

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ballmai1ly@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=ballmai1ly@gmail.com
EMAILS_FROM_NAME=WorkLog Pro
SMTP_TLS=true

### 生产环境邮件配置

**重要**: 生产环境必须通过环境变量配置邮件信息，不能使用硬编码的默认值。

#### Railway 平台配置

在 Railway 平台的项目设置中添加以下环境变量：

```bash
# 邮件配置 - Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ballmai1ly@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=ballmai1ly@gmail.com
EMAILS_FROM_NAME=WorkLog Pro
SMTP_TLS=true
```

#### 环境变量说明

- `SMTP_HOST`: SMTP服务器地址（Gmail使用 smtp.gmail.com）
- `SMTP_PORT`: SMTP端口（Gmail TLS端口为587）
- `SMTP_USER`: 您的Gmail邮箱地址（ballmai1ly@gmail.com）
- `SMTP_PASSWORD`: Gmail的应用专用密码（不是登录密码）
- `EMAILS_FROM_EMAIL`: 发件人邮箱地址（ballmai1ly@gmail.com）
- `EMAILS_FROM_NAME`: 发件人显示名称
- `SMTP_TLS`: 是否启用TLS（Gmail必须设置为true）

#### 获取Gmail应用专用密码

1. 登录Google账户
2. 进入"安全性" → "2步验证"
3. 开启"2步验证"（如果未开启）
4. 在"应用专用密码"中生成新的密码
5. 将生成的16位应用专用密码填入 `SMTP_PASSWORD` 环境变量

**注意**: Gmail要求使用应用专用密码，不能使用账户密码或2步验证码。

#### 配置验证

部署后，应用启动时会显示邮件配置信息，请检查：

```
📧 生产环境邮件配置:
  SMTP_HOST: smtp.163.com
  SMTP_PORT: 465
  SMTP_USER: your_actual_email@163.com
  SMTP_PASSWORD: ****************
  EMAILS_FROM_EMAIL: your_actual_email@163.com
  EMAILS_FROM_NAME: WorkLog Pro
  SMTP_TLS: false
```

如果看到"未配置邮箱用户"等警告信息，说明环境变量未正确设置。
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api.py

# 运行测试并显示详细输出
pytest -v
```

### 测试数据库连接

```bash
python test_db_connection.py
```

### 测试网络连接

```bash
python test_network_connection.py
```

## 📁 项目结构

```
worklog/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── core/              # 核心配置和服务
│   ├── crud/              # 数据库操作
│   ├── db/                # 数据库配置
│   ├── models/            # 数据模型
│   └── schemas/           # 数据验证模式
├── tests/                 # 测试文件
├── alembic/               # 数据库迁移
├── main.py                # 应用入口
├── requirements.txt        # Python依赖
├── install_dependencies.py # 依赖安装脚本
├── start_backend.py       # 启动脚本
└── README.md              # 项目说明
```

## 🔍 故障排除

### 常见问题

#### 1. 依赖安装失败

**问题**: `Microsoft Visual C++ 14.0 is required`

**解决方案**: 
- Windows: 安装 Visual Studio Build Tools
- 下载地址: https://visualstudio.microsoft.com/visual-cpp-build-tools/

#### 2. 数据库连接失败

**问题**: `Can't connect to MySQL server`

**解决方案**:
1. 确保MySQL服务正在运行
2. 检查数据库配置是否正确
3. 确保数据库用户有足够权限

#### 3. Redis连接失败

**问题**: `Redis connection failed`

**解决方案**:
1. 确保Redis服务正在运行
2. 检查Redis配置
3. Redis不是必需的，可以忽略此错误

#### 4. 端口被占用

**问题**: `Address already in use`

**解决方案**:
1. 查找占用端口的进程: `netstat -ano | findstr :8000`
2. 终止进程或更改端口号

### 日志查看

应用日志会输出到控制台，包含以下信息：
- 数据库连接状态
- API请求日志
- 错误信息
- 性能统计

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目 Issues
3. 联系开发团队

---

**最后更新时间**: 2024年12月19日
**版本**: v1.0.0 
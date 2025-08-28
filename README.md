# WorkLog Pro - 工作日志管理系统

## 项目概述

WorkLog Pro 是一个现代化的团队工作日志管理系统，支持任务管理、团队协作、实时通知等功能。

## 项目结构

```
worksheet/
├── worklog/                 # 后端服务 (Python FastAPI)
│   ├── app/                # 应用核心代码
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试文件
│   ├── requirements.txt    # Python依赖
│   ├── main.py            # 应用入口
│   └── railway.json       # Railway部署配置
├── worklog-web/            # 前端服务 (Vue.js)
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # Vite配置
└── docs/                  # 项目文档
```

## 技术栈

### 后端
- **Python 3.9+**
- **FastAPI** - 现代Web框架
- **SQLAlchemy** - ORM
- **Alembic** - 数据库迁移
- **MySQL** - 数据库
- **Redis** - 缓存和消息队列
- **WebSocket** - 实时通信

### 前端
- **Vue 3** - 前端框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Pinia** - 状态管理
- **Vue Router** - 路由管理

## 快速开始

### 后端启动
```bash
cd worklog
pip install -r requirements.txt
python main.py
```

### 前端启动
```bash
cd worklog-web
npm install
npm run dev
```

## 部署

### Railway 部署
项目已配置好 Railway 部署，包含以下文件：
- `railway.json` - Railway 配置
- `nixpacks.toml` - 构建配置
- `Procfile` - 启动命令
- `runtime.txt` - Python 版本

详细部署指南请参考：
- [快速部署指南](worklog/QUICK_DEPLOY.md)
- [详细部署文档](worklog/RAILWAY_DEPLOYMENT.md)

## 功能特性

- ✅ 用户认证和授权
- ✅ 团队管理
- ✅ 项目管理
- ✅ 任务管理
- ✅ 工作日志记录
- ✅ 实时通知
- ✅ 邮件提醒
- ✅ WebSocket 实时通信
- ✅ 移动端适配
- ✅ 桌面端支持

## 开发进度

详细开发进度请参考：[开发进度报告](WorkLog_Pro_开发进度报告_2024-12-19.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

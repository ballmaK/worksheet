# 工作日志系统消息机制设计文档

## 1. 系统概述

消息机制是工作日志系统的核心功能之一，用于在用户之间传递重要信息、系统通知和业务提醒。系统支持多渠道消息传递，包括实时推送、邮件通知、桌面通知等。

## 2. 系统架构

### 2.1 核心组件

```
消息系统架构
├── 数据层 (Data Layer)
│   ├── Message 模型 - 消息实体
│   └── MessageTemplate 模型 - 消息模板
├── 业务层 (Business Layer)
│   ├── MessageService - 消息服务
│   ├── MessageCRUD - 数据操作
│   └── MessageIntegration - 业务集成
├── API层 (API Layer)
│   └── Messages API - 消息接口
└── 通知层 (Notification Layer)
    ├── WebSocket - 实时通知
    ├── Email - 邮件通知
    └── Desktop - 桌面通知
```

### 2.2 消息类型

| 类型 | 描述 | 优先级 | 示例 |
|------|------|--------|------|
| task | 任务相关 | 重要/紧急 | 任务分配、状态变更、截止提醒 |
| team | 团队相关 | 重要 | 成员邀请、权限变更 |
| worklog | 工作日志 | 普通 | 记录提醒、统计报告 |
| system | 系统通知 | 重要 | 维护通知、功能更新 |
| user | 用户行为 | 普通 | 登录提醒、异常操作 |

### 2.3 消息优先级

| 优先级 | 描述 | 颜色 | 处理策略 |
|--------|------|------|----------|
| urgent | 紧急 | 红色 | 立即处理，多渠道通知 |
| important | 重要 | 橙色 | 优先处理，实时通知 |
| normal | 普通 | 蓝色 | 正常处理，应用内通知 |
| low | 低优先级 | 灰色 | 批量处理，可选通知 |

## 3. 数据模型

### 3.1 Message 模型

```python
class Message(Base):
    id: int                    # 消息ID
    title: str                 # 消息标题
    content: str               # 消息内容
    message_type: str          # 消息类型
    priority: str              # 优先级
    sender_id: int             # 发送者ID
    receiver_id: int           # 接收者ID
    is_read: bool              # 是否已读
    is_deleted: bool           # 是否删除
    read_at: datetime          # 阅读时间
    created_at: datetime       # 创建时间
    sent_via_email: bool       # 邮件发送状态
    sent_via_websocket: bool   # WebSocket发送状态
    sent_via_desktop: bool     # 桌面通知状态
    metadata: dict             # 元数据
```

### 3.2 MessageTemplate 模型

```python
class MessageTemplate(Base):
    id: int                    # 模板ID
    name: str                  # 模板名称
    title_template: str        # 标题模板
    content_template: str      # 内容模板
    message_type: str          # 消息类型
    priority: str              # 优先级
    variables: dict            # 模板变量
    send_via_email: bool       # 是否发送邮件
    send_via_websocket: bool   # 是否发送WebSocket
    send_via_desktop: bool     # 是否发送桌面通知
    is_active: bool            # 是否激活
```

## 4. 核心服务

### 4.1 MessageService

消息服务提供以下核心功能：

- **模板渲染**: 使用Jinja2模板引擎渲染消息内容
- **多渠道发送**: 支持WebSocket、邮件、桌面通知
- **消息创建**: 基于模板创建和发送消息
- **状态管理**: 管理消息的发送状态

### 4.2 MessageIntegration

业务集成服务提供以下功能：

- **任务分配通知**: 当任务被分配时发送通知
- **状态变更通知**: 当任务状态变更时通知相关人员
- **截止提醒**: 任务即将到期时发送提醒
- **团队邀请**: 发送团队邀请通知
- **工作日志提醒**: 定期提醒用户记录工作日志

## 5. API接口

### 5.1 消息管理接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/messages/` | 获取消息列表 |
| GET | `/api/v1/messages/stats` | 获取消息统计 |
| GET | `/api/v1/messages/unread-count` | 获取未读数量 |
| GET | `/api/v1/messages/{id}` | 获取指定消息 |
| PUT | `/api/v1/messages/{id}/read` | 标记消息已读 |
| PUT | `/api/v1/messages/mark-all-read` | 标记所有已读 |
| DELETE | `/api/v1/messages/{id}` | 删除消息 |

### 5.2 模板管理接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/messages/templates/` | 获取模板列表 |
| POST | `/api/v1/messages/templates/` | 创建模板 |
| GET | `/api/v1/messages/templates/{id}` | 获取指定模板 |
| PUT | `/api/v1/messages/templates/{id}` | 更新模板 |
| DELETE | `/api/v1/messages/templates/{id}` | 删除模板 |

## 6. 使用示例

### 6.1 发送任务分配通知

```python
from app.core.message_integration import message_integration

# 在任务分配时调用
message_integration.send_task_assigned_notification(
    db=db,
    task=task,
    assignee=assignee,
    assigner=assigner
)
```

### 6.2 发送状态变更通知

```python
# 在任务状态变更时调用
message_integration.send_task_status_changed_notification(
    db=db,
    task=task,
    old_status="pending",
    new_status="in_progress",
    updater=current_user
)
```

### 6.3 发送截止提醒

```python
# 在定时任务中调用
message_integration.send_task_due_reminder(
    db=db,
    task=task
)
```

## 7. 配置说明

### 7.1 默认模板

系统预置了以下默认模板：

- `task_assigned`: 任务分配通知
- `task_status_changed`: 任务状态变更通知
- `task_due_reminder`: 任务截止提醒
- `team_invitation`: 团队邀请通知
- `worklog_reminder`: 工作日志提醒
- `system_maintenance`: 系统维护通知

### 7.2 通知配置

每个模板可以配置以下通知方式：

```python
{
    "send_via_email": False,      # 邮件通知
    "send_via_websocket": True,   # 实时通知
    "send_via_desktop": True      # 桌面通知
}
```

## 8. 部署说明

### 8.1 数据库迁移

```bash
# 创建消息表
python create_message_tables.py
```

### 8.2 初始化模板

系统启动时会自动初始化默认消息模板。

### 8.3 权限配置

消息模板管理功能需要管理员权限。

## 9. 扩展功能

### 9.1 WebSocket实时通知

- 实现WebSocket连接管理
- 消息实时推送
- 在线状态管理

### 9.2 邮件通知

- 配置SMTP服务
- 邮件模板定制
- 发送状态跟踪

### 9.3 桌面通知

- Electron桌面通知
- 通知权限管理
- 通知历史记录

### 9.4 移动端推送

- 推送服务集成
- 设备管理
- 推送统计

## 10. 监控和维护

### 10.1 消息统计

- 消息发送成功率
- 用户阅读率
- 消息类型分布

### 10.2 性能监控

- 消息发送延迟
- 数据库查询性能
- 通知服务状态

### 10.3 故障处理

- 消息发送失败重试
- 模板渲染错误处理
- 通知服务降级策略

## 11. 最佳实践

### 11.1 消息设计

- 消息内容简洁明了
- 包含必要的操作链接
- 避免信息过载

### 11.2 通知策略

- 根据优先级选择合适的通知方式
- 避免频繁打扰用户
- 提供通知偏好设置

### 11.3 性能优化

- 批量处理消息发送
- 异步处理通知
- 合理设置消息过期时间

## 12. 未来规划

### 12.1 功能增强

- 消息分类和标签
- 消息搜索和过滤
- 消息回复和转发

### 12.2 智能化

- 消息重要性自动判断
- 个性化消息推荐
- 智能通知时间

### 12.3 集成扩展

- 第三方消息服务
- 企业微信/钉钉集成
- 短信通知支持 
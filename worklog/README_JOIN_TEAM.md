# 加入团队功能说明

## 功能概述

新注册用户现在可以通过"加入团队"功能自主发现并申请加入感兴趣的团队，无需等待邀请。

## 主要特性

### 1. 团队搜索
- **模糊搜索**: 支持按团队名称和描述进行关键词搜索
- **公开团队**: 显示所有公开的团队信息
- **实时统计**: 显示团队成员数量和项目数量
- **分页支持**: 支持分页浏览大量团队

### 2. 申请加入
- **申请留言**: 用户可以填写申请理由（10-200字符）
- **状态管理**: 申请状态包括待审核、已通过、已拒绝
- **防重复**: 防止重复提交申请
- **自动通知**: 自动通知团队管理员有新申请

### 3. 权限控制
- **公开可见**: 所有用户都可以搜索和查看公开团队
- **申请限制**: 已经是团队成员的用户无法重复申请
- **管理员审核**: 只有团队管理员可以审核申请

## 技术实现

### 后端API

#### 1. 搜索公开团队
```http
GET /api/v1/teams/search/public?keyword=关键词&page=1&size=20
```

**响应示例:**
```json
[
  {
    "id": 1,
    "name": "技术开发团队",
    "description": "负责核心产品开发",
    "created_at": "2025-09-02T10:00:00",
    "member_count": 8,
    "project_count": 5,
    "is_public": true
  }
]
```

#### 2. 申请加入团队
```http
POST /api/v1/teams/{team_id}/join
Content-Type: application/json

{
  "message": "申请留言内容"
}
```

**响应示例:**
```json
{
  "message": "申请已提交，请等待管理员审核",
  "application_id": 123
}
```

### 数据库设计

#### team_join_requests 表
```sql
CREATE TABLE team_join_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_team_id (team_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

### 前端页面

#### 路由配置
```typescript
{
  path: '/join-teams',
  name: 'JoinTeams',
  component: () => import('@/views/JoinTeams.vue'),
  meta: { requiresAuth: true }
}
```

#### 主要组件
- **搜索区域**: 关键词输入和搜索按钮
- **团队卡片**: 显示团队基本信息和统计
- **申请对话框**: 填写申请留言的表单
- **分页控件**: 支持大量结果的分页浏览

## 使用流程

### 1. 用户操作流程
1. 登录系统后，点击导航菜单中的"加入团队"
2. 在搜索框中输入关键词（可选）
3. 浏览搜索结果，查看团队信息
4. 点击"申请加入"按钮
5. 填写申请留言（必填）
6. 提交申请，等待管理员审核

### 2. 管理员审核流程
1. 收到新成员申请通知
2. 查看申请详情和留言
3. 审核申请，决定是否通过
4. 通过后用户自动成为团队成员
5. 拒绝后用户可重新申请

## 部署说明

### 1. 数据库迁移
```bash
cd worklog
alembic upgrade head
```

### 2. 重启服务
```bash
# 重启后端服务
python main.py

# 重启前端服务
cd worklog-web
npm run dev
```

### 3. 验证功能
```bash
# 运行测试脚本
python test_join_team.py
```

## 注意事项

1. **权限要求**: 用户必须登录才能使用此功能
2. **重复申请**: 系统会阻止重复提交申请
3. **数据一致性**: 申请通过后立即更新团队成员关系
4. **通知机制**: 目前通过日志记录，后续可扩展邮件通知
5. **性能考虑**: 大量团队时建议使用分页和缓存

## 后续扩展

1. **邮件通知**: 申请状态变更时发送邮件通知
2. **申请历史**: 用户可以查看自己的申请历史
3. **批量操作**: 管理员可以批量处理申请
4. **申请模板**: 提供申请留言的模板建议
5. **团队分类**: 按行业、技术栈等分类团队
6. **推荐算法**: 基于用户兴趣推荐相关团队

## 故障排除

### 常见问题

1. **搜索无结果**
   - 检查关键词是否正确
   - 确认数据库中有团队数据
   - 验证用户权限

2. **申请失败**
   - 检查用户是否已经是团队成员
   - 确认是否有待处理的申请
   - 验证团队ID是否存在

3. **页面加载失败**
   - 检查前端路由配置
   - 确认API接口是否正常
   - 验证用户登录状态

### 日志查看
```bash
# 查看后端日志
tail -f worklog.log

# 查看申请相关日志
grep "申请加入团队" worklog.log
```

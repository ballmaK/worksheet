# 加入团队请求管理功能说明

## 功能概述

团队管理员现在可以查看和管理用户提交的加入团队申请，包括查看申请详情、批准或拒绝申请。

## 主要特性

### 1. 查看加入申请
- **申请列表**: 显示所有加入申请（待处理、已批准、已拒绝）
- **申请详情**: 包含申请人信息、申请留言、时间等
- **状态筛选**: 按申请状态进行筛选
- **搜索功能**: 支持按用户名或邮箱搜索

### 2. 申请管理
- **批准申请**: 批准后用户自动成为团队成员
- **拒绝申请**: 拒绝申请并记录原因
- **批量处理**: 支持批量处理多个申请
- **权限控制**: 只有团队管理员可以操作

### 3. 统计信息
- **总申请数**: 显示所有申请的数量
- **待处理数**: 显示待处理的申请数量
- **已批准数**: 显示已批准的申请数量
- **已拒绝数**: 显示已拒绝的申请数量

## 技术实现

### 后端API

#### 1. 获取团队加入申请列表
```http
GET /api/v1/teams/{team_id}/join-requests
Authorization: Bearer {token}
```

**响应示例:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "username": "张三",
    "email": "zhangsan@example.com",
    "message": "我想加入这个团队，因为我对团队的项目很感兴趣",
    "status": "pending",
    "created_at": "2025-09-02T10:00:00",
    "updated_at": "2025-09-02T10:00:00"
  }
]
```

#### 2. 批准加入申请
```http
PUT /api/v1/teams/{team_id}/join-requests/{request_id}/approve
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "message": "申请已批准，用户已加入团队"
}
```

#### 3. 拒绝加入申请
```http
PUT /api/v1/teams/{team_id}/join-requests/{request_id}/reject
Authorization: Bearer {token}
```

**响应示例:**
```json
{
  "message": "申请已拒绝"
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

## 使用流程

### 1. 管理员操作流程
1. 登录系统，进入团队管理页面
2. 点击"查看加入申请"或类似按钮
3. 查看待处理的加入申请列表
4. 点击"批准"或"拒绝"按钮
5. 确认操作，系统自动处理申请

### 2. 申请状态说明
- **pending**: 待处理 - 管理员尚未处理
- **approved**: 已批准 - 用户已成为团队成员
- **rejected**: 已拒绝 - 申请被拒绝

## 权限控制

### 1. 查看权限
- 只有团队管理员可以查看加入申请
- 普通成员无法访问此功能

### 2. 操作权限
- 只有团队管理员可以批准或拒绝申请
- 系统自动验证用户权限

### 3. 数据安全
- 申请数据与团队绑定
- 用户只能查看自己团队的申请

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
```

### 3. 验证功能
```bash
# 运行测试脚本
python test_join_requests_management.py
```

## 前端集成

### 1. 路由配置
```typescript
{
  path: '/teams/:teamId/join-requests',
  name: 'TeamJoinRequests',
  component: () => import('@/views/TeamJoinRequests.vue'),
  meta: { requiresAuth: true, requiresTeamAdmin: true }
}
```

### 2. 页面组件
- **TeamJoinRequests.vue**: 主要的申请管理页面
- **申请列表**: 显示所有申请信息
- **操作按钮**: 批准、拒绝、查看详情
- **筛选搜索**: 按状态和关键词筛选

### 3. API集成
```typescript
// 获取申请列表
const requests = await teamApi.getTeamJoinRequests(teamId)

// 批准申请
await teamApi.approveJoinRequest(teamId, requestId)

// 拒绝申请
await teamApi.rejectJoinRequest(teamId, requestId)
```

## 注意事项

1. **权限要求**: 只有团队管理员可以使用此功能
2. **数据一致性**: 批准申请后立即更新团队成员关系
3. **通知机制**: 可以扩展邮件通知功能
4. **日志记录**: 所有操作都会记录日志

## 后续优化建议

1. **批量操作**: 支持批量批准或拒绝申请
2. **申请原因**: 拒绝时可以填写拒绝原因
3. **自动审核**: 可以设置自动审核规则
4. **申请模板**: 提供标准的申请模板
5. **统计分析**: 添加申请趋势分析

## 故障排除

### 常见问题

1. **无法查看申请列表**
   - 检查用户是否是团队管理员
   - 确认团队ID是否正确
   - 验证API接口是否可用

2. **无法批准/拒绝申请**
   - 检查申请状态是否为pending
   - 确认用户权限是否足够
   - 验证申请ID是否正确

3. **申请状态不更新**
   - 检查数据库连接是否正常
   - 确认事务是否提交成功
   - 验证API响应是否正确

### 调试方法

1. 查看后端日志
2. 检查数据库记录
3. 验证API接口响应
4. 确认用户权限设置

---

**功能完成时间**: 2025-09-02  
**版本**: v1.0.0  
**类型**: 管理功能增强

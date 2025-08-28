<template>
  <div class="message-list">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ messages.length }}</div>
            <div class="stat-label">总消息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card unread">
          <div class="stat-content">
            <div class="stat-number">{{ unreadCount }}</div>
            <div class="stat-label">未读消息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ todayCount }}</div>
            <div class="stat-label">今日消息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ weekCount }}</div>
            <div class="stat-label">本周消息</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 视图切换 -->
    <div class="view-toggle">
      <el-radio-group v-model="currentView" size="large">
        <el-radio-button label="table">
          <el-icon><Grid /></el-icon>
          表格视图
        </el-radio-button>
        <el-radio-button label="card">
          <el-icon><Grid /></el-icon>
          卡片视图
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 表格视图 -->
    <div v-if="currentView === 'table'" class="table-view">
      <el-table 
        :data="messages" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <div class="message-type-icon" :class="getTypeClass(row.message_type)">
              <el-icon>
                <Check v-if="row.message_type === 'task'" />
                <User v-else-if="row.message_type === 'team'" />
                <Warning v-else-if="row.message_type === 'system'" />
                <Timer v-else-if="row.message_type === 'worklog'" />
                <Folder v-else-if="row.message_type === 'project'" />
                <Bell v-else />
              </el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="120" />
        <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sender_name" label="发送者" width="100" />
        <el-table-column prop="created_at" label="时间" width="120">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'warning'" size="small">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$emit('select', row)">查看</el-button>
            <el-button 
              v-if="!row.is_read" 
              size="small" 
              type="primary" 
              @click="markAsRead(row)"
            >
              标记已读
            </el-button>
            <el-button 
              v-if="row.message_type === 'team' && !row.is_read" 
              size="small" 
              type="success" 
              @click="handleTeamInvite(row, 'accept')"
            >
              接受
            </el-button>
            <el-button 
              v-if="row.message_type === 'team' && !row.is_read" 
              size="small" 
              type="danger" 
              @click="handleTeamInvite(row, 'reject')"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 卡片视图 -->
    <div v-else class="card-view">
      <div class="cards-container">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message-card', { unread: !msg.is_read }]"
        >
          <div class="card-header">
            <div class="message-type-icon" :class="getTypeClass(msg.message_type)">
              <el-icon>
                <Check v-if="msg.message_type === 'task'" />
                <User v-else-if="msg.message_type === 'team'" />
                <Warning v-else-if="msg.message_type === 'system'" />
                <Timer v-else-if="msg.message_type === 'worklog'" />
                <Folder v-else-if="msg.message_type === 'project'" />
                <Bell v-else />
              </el-icon>
            </div>
            <div class="message-info">
              <div class="message-title">{{ msg.title }}</div>
              <div class="message-sender">发送者：{{ msg.sender_name }}</div>
            </div>
            <div class="message-time">{{ formatTime(msg.created_at) }}</div>
          </div>
          
          <div class="card-content">
            <div class="message-content">{{ msg.content }}</div>
          </div>
          
          <div class="card-footer">
            <div class="message-status">
              <el-tag :type="msg.is_read ? 'info' : 'warning'" size="small">
                {{ msg.is_read ? '已读' : '未读' }}
              </el-tag>
            </div>
            <div class="message-actions">
              <el-button size="small" @click="$emit('select', msg)">查看</el-button>
              <el-button 
                v-if="!msg.is_read" 
                size="small" 
                type="primary" 
                @click="markAsRead(msg)"
              >
                标记已读
              </el-button>
              <el-button 
                v-if="msg.message_type === 'team' && !msg.is_read" 
                size="small" 
                type="success" 
                @click="handleTeamInvite(msg, 'accept')"
              >
                接受
              </el-button>
              <el-button 
                v-if="msg.message_type === 'team' && !msg.is_read" 
                size="small" 
                type="danger" 
                @click="handleTeamInvite(msg, 'reject')"
              >
                拒绝
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && messages.length === 0" class="empty-state">
      <el-empty description="暂无消息" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, Check, User, Warning, Timer, Folder, Bell } from '@element-plus/icons-vue'
import { markMessageAsRead } from '@/api/message'

// Props
interface Props {
  messages: any[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
const emit = defineEmits<{
  select: [message: any]
  messageRead: [message: any]
  teamInviteResponse: [message: any, action: 'accept' | 'reject']
}>()

// 响应式数据
const currentView = ref<'table' | 'card'>('table')
const selectedMessages = ref<any[]>([])

// 计算属性
const unreadCount = computed(() => props.messages.filter(msg => !msg.is_read).length)
const todayCount = computed(() => {
  const today = new Date().toDateString()
  return props.messages.filter(msg => new Date(msg.created_at).toDateString() === today).length
})
const weekCount = computed(() => {
  const weekAgo = new Date()
  weekAgo.setDate(weekAgo.getDate() - 7)
  return props.messages.filter(msg => new Date(msg.created_at) >= weekAgo).length
})

// 方法
const getTypeClass = (type: string) => {
  const classMap: Record<string, string> = {
    task: 'type-task',
    team: 'type-team',
    system: 'type-system',
    worklog: 'type-worklog',
    project: 'type-project'
  }
  return classMap[type] || 'type-default'
}

const formatTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

const handleSelectionChange = (selection: any[]) => {
  selectedMessages.value = selection
}

const markAsRead = async (message: any) => {
  try {
    await markMessageAsRead(message.id)
    message.is_read = true
    emit('messageRead', message)
    ElMessage.success('已标记为已读')
  } catch (error: any) {
    ElMessage.error('标记已读失败: ' + error.message)
  }
}

const handleTeamInvite = (message: any, action: 'accept' | 'reject') => {
  emit('teamInviteResponse', message, action)
}
</script>

<style scoped>
.message-list {
  padding: 20px;
}

/* 统计卡片 */
.statistics-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.unread {
  border-left: 4px solid #409eff;
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 视图切换 */
.view-toggle {
  margin-bottom: 20px;
  text-align: center;
}

/* 表格视图 */
.table-view {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-type-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
}

.type-task {
  background: linear-gradient(135deg, #409eff, #67c23a);
}

.type-team {
  background: linear-gradient(135deg, #e6a23c, #f56c6c);
}

.type-system {
  background: linear-gradient(135deg, #f56c6c, #e6a23c);
}

.type-worklog {
  background: linear-gradient(135deg, #909399, #606266);
}

.type-project {
  background: linear-gradient(135deg, #67c23a, #409eff);
}

.type-default {
  background: linear-gradient(135deg, #909399, #606266);
}

/* 卡片视图 */
.card-view {
  margin-top: 20px;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.message-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.message-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message-card.unread {
  border-left: 3px solid #409eff;
  background: linear-gradient(135deg, #f8fbff 0%, #ffffff 100%);
}

.card-header {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.message-info {
  flex: 1;
}

.message-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.message-sender {
  font-size: 12px;
  color: #909399;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.card-content {
  padding: 16px;
}

.message-content {
  color: #606266;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.message-actions {
  display: flex;
  gap: 8px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .cards-container {
    grid-template-columns: 1fr;
  }
  
  .statistics-cards .el-col {
    margin-bottom: 10px;
  }
}
</style> 
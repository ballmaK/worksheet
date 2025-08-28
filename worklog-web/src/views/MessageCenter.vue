<template>
  <div class="message-center">
    <!-- 消息统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
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

    <!-- 消息列表卡片 -->
    <el-card class="message-list-card">
      <div class="card-header">
        <span>消息列表</span>
        <div class="header-actions">
          <el-select v-model="filterType" placeholder="消息类型" clearable style="width: 120px; margin-right: 12px;">
            <el-option label="全部" value="" />
            <el-option label="任务通知" value="task" />
            <el-option label="团队邀请" value="team" />
            <el-option label="系统提醒" value="system" />
            <el-option label="工作日志" value="worklog" />
            <el-option label="项目更新" value="project" />
          </el-select>
          
          <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 100px; margin-right: 12px;">
            <el-option label="全部" value="" />
            <el-option label="未读" value="unread" />
            <el-option label="已读" value="read" />
          </el-select>
          
          <el-button type="primary" @click="refreshMessages" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          
          <el-button 
            v-if="selectedMessages.length > 0" 
            type="success" 
            @click="batchMarkAsRead"
          >
            批量标记已读
          </el-button>
        </div>
      </div>
      
      <!-- 消息表格 -->
      <el-table 
        :data="filteredMessages" 
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
            <el-button size="small" @click="handleMessageSelect(row)">查看</el-button>
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

      <!-- 空状态 -->
      <div v-if="!loading && filteredMessages.length === 0" class="empty-state">
        <el-empty description="暂无消息" />
      </div>
    </el-card>

    <!-- 消息详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="消息详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedMessage" class="message-detail">
        <div class="detail-header">
          <div class="message-type-icon" :class="getTypeClass(selectedMessage.message_type)">
            <el-icon>
              <Check v-if="selectedMessage.message_type === 'task'" />
              <User v-else-if="selectedMessage.message_type === 'team'" />
              <Warning v-else-if="selectedMessage.message_type === 'system'" />
              <Timer v-else-if="selectedMessage.message_type === 'worklog'" />
              <Folder v-else-if="selectedMessage.message_type === 'project'" />
              <Bell v-else />
            </el-icon>
          </div>
          <div class="detail-info">
            <h3>{{ selectedMessage.title }}</h3>
            <p class="detail-meta">
              发送者：{{ selectedMessage.sender_name }} | 
              时间：{{ formatTime(selectedMessage.created_at) }}
            </p>
          </div>
        </div>
        
        <div class="detail-content">
          <p>{{ selectedMessage.content }}</p>
        </div>
        
        <div class="detail-actions">
          <el-button 
            v-if="!selectedMessage.is_read" 
            type="primary" 
            @click="markAsRead(selectedMessage)"
          >
            标记已读
          </el-button>
          <el-button 
            v-if="selectedMessage.message_type === 'team' && !selectedMessage.is_read" 
            type="success" 
            @click="handleTeamInvite(selectedMessage, 'accept')"
          >
            接受邀请
          </el-button>
          <el-button 
            v-if="selectedMessage.message_type === 'team' && !selectedMessage.is_read" 
            type="danger" 
            @click="handleTeamInvite(selectedMessage, 'reject')"
          >
            拒绝邀请
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Check, User, Warning, Timer, Folder, Bell } from '@element-plus/icons-vue'
import { getMessages, markAllMessagesAsRead, markMessageAsRead, deleteMessage } from '@/api/message'
import { useWebSocket } from '@/composables/useWebSocket'

interface Message {
  id: number
  title: string
  content: string
  message_type: string
  created_at: string
  is_read: boolean
  sender_name?: string
  message_data?: any
}

const messages = ref<Message[]>([])
const loading = ref(false)
const filterType = ref('')
const filterStatus = ref('')
const selectedMessages = ref<Message[]>([])
const detailVisible = ref(false)
const selectedMessage = ref<Message | null>(null)

// WebSocket相关
const { resetUnreadCount } = useWebSocket()

// 计算属性
const unreadCount = computed(() => messages.value.filter(msg => !msg.is_read).length)
const todayCount = computed(() => {
  const today = new Date().toDateString()
  return messages.value.filter(msg => new Date(msg.created_at).toDateString() === today).length
})
const weekCount = computed(() => {
  const weekAgo = new Date()
  weekAgo.setDate(weekAgo.getDate() - 7)
  return messages.value.filter(msg => new Date(msg.created_at) >= weekAgo).length
})

// 过滤后的消息列表
const filteredMessages = computed(() => {
  // 确保messages.value是数组
  if (!Array.isArray(messages.value)) {
    return []
  }
  
  let filtered = [...messages.value]
  
  if (filterType.value) {
    filtered = filtered.filter(msg => msg.message_type === filterType.value)
  }
  
  if (filterStatus.value) {
    if (filterStatus.value === 'unread') {
      filtered = filtered.filter(msg => !msg.is_read)
    } else if (filterStatus.value === 'read') {
      filtered = filtered.filter(msg => msg.is_read)
    }
  }
  
  return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

// 获取消息列表
const loadMessages = async () => {
  try {
    loading.value = true
    const response = await getMessages()
    // getMessages直接返回Message数组
    if (Array.isArray(response)) {
      messages.value = response
    } else {
      messages.value = []
    }
  } catch (error: any) {
    ElMessage.error('获取消息失败: ' + error.message)
    messages.value = []
  } finally {
    loading.value = false
  }
}

// 标记单条消息为已读
const markAsRead = async (message: any) => {
  try {
    await markMessageAsRead(message.id)
    message.is_read = true
    ElMessage.success('已标记为已读')
  } catch (error: any) {
    ElMessage.error('标记已读失败: ' + error.message)
  }
}

// 删除消息
async function handleDelete(messageId: number) {
  try {
    await ElMessageBox.confirm('确定要删除该消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteMessage(messageId)
    ElMessage.success('删除成功')
    await loadMessages()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除消息失败:', error)
    }
  }
}

// 全部标记为已读
async function markAllRead() {
  try {
    await markAllMessagesAsRead(filterType.value || undefined)
    ElMessage.success('全部标为已读')
    await loadMessages()
    // 重置未读消息计数
    resetUnreadCount()
  } catch (error) {
    ElMessage.error('操作失败')
    console.error('全部标记已读失败:', error)
  }
}

// 显示消息详情
function showDetail(message: Message) {
  selectedMessage.value = message
  detailVisible.value = true
}

// 处理新消息事件
const handleNewMessage = () => {
  // 自动刷新消息列表
  loadMessages()
}

// 处理消息计数更新事件
const handleMessageCountUpdate = (event: CustomEvent) => {
  console.log('消息计数更新:', event.detail)
}

// 处理消息选择事件
const handleMessageSelect = (message: Message) => {
  selectedMessage.value = message
  detailVisible.value = true
}

// 处理消息阅读事件
const handleMessageRead = (message: Message) => {
  // 更新本地消息状态
  const index = messages.value.findIndex(msg => msg.id === message.id)
  if (index !== -1) {
    messages.value[index] = message
  }
}

// 处理团队邀请响应事件
const handleTeamInviteResponse = async (message: Message, action: 'accept' | 'reject') => {
  try {
    // 暂时显示提示信息，因为后端API还未实现
    if (action === 'accept') {
      ElMessage.info('接受邀请功能暂未实现')
    } else {
      ElMessage.info('拒绝邀请功能暂未实现')
    }

    // 标记消息为已读
    await markAsRead(message)
    
    // 刷新消息列表
    await loadMessages()
  } catch (error) {
    ElMessage.error('处理邀请失败')
    console.error('处理邀请失败:', error)
  }
}

// 处理团队邀请事件
const handleTeamInvite = (message: Message, action: 'accept' | 'reject') => {
  try {
    // 暂时显示提示信息，因为后端API还未实现
    if (action === 'accept') {
      ElMessage.info('接受邀请功能暂未实现')
    } else {
      ElMessage.info('拒绝邀请功能暂未实现')
    }

    // 标记消息为已读
    markAsRead(message)
    detailVisible.value = false
  } catch (error) {
    ElMessage.error('处理邀请失败')
    console.error('处理邀请失败:', error)
  }
}

// 处理批量标记已读事件
const batchMarkAsRead = async () => {
  if (selectedMessages.value.length === 0) {
    ElMessage.warning('请选择要标记的消息')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedMessages.value.length} 条消息标记为已读吗？`,
      '确认操作',
      { type: 'warning' }
    )

    const promises = selectedMessages.value.map(msg => 
      markMessageAsRead(msg.id)
    )
    await Promise.all(promises)

    // 更新本地状态
    selectedMessages.value.forEach(msg => {
      const index = messages.value.findIndex(m => m.id === msg.id)
      if (index !== -1) {
        messages.value[index].is_read = true
      }
    })

    selectedMessages.value = []
    ElMessage.success('批量标记成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量标记失败: ' + error.message)
    }
  }
}

// 处理选择变化
const handleSelectionChange = (selection: Message[]) => {
  selectedMessages.value = selection
}

// 处理消息类型类
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

// 处理时间格式化
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

// 处理消息刷新事件
const refreshMessages = () => {
  loadMessages()
}

onMounted(() => {
  loadMessages()
  
  // 监听新消息事件
  window.addEventListener('new-message', handleNewMessage)
  window.addEventListener('message-count-updated', handleMessageCountUpdate as EventListener)
  
  // 进入消息中心时重置未读计数
  resetUnreadCount()
})

onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('new-message', handleNewMessage)
  window.removeEventListener('message-count-updated', handleMessageCountUpdate as EventListener)
})
</script>

<style scoped>
.message-center {
  padding: 20px;
}

/* 统计卡片样式 */
.stat-card {
  text-align: center;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.unread {
  border-left: 4px solid #409eff;
}

.stat-content {
  padding: 16px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 消息列表卡片 */
.message-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
}

.card-header span {
  font-size: 16px;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 消息类型图标 */
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

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

/* 消息详情弹窗 */
.message-detail {
  padding: 20px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.detail-meta {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.detail-content {
  margin-bottom: 20px;
  line-height: 1.6;
  color: #606266;
}

.detail-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-center {
    padding: 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .stat-number {
    font-size: 24px;
  }

  .stat-content {
    padding: 12px;
  }
}
</style> 
<template>
  <div class="websocket-test">
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <span>WebSocket连接测试</span>
          <el-tag :type="connectionStatus.type">{{ connectionStatus.text }}</el-tag>
      </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <h3>连接状态</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="连接状态">
              <el-tag :type="isConnected ? 'success' : 'danger'">
                {{ isConnected ? '已连接' : '未连接' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="连接状态码">
              {{ connectionState }}
            </el-descriptions-item>
            <el-descriptions-item label="未读消息数">
              {{ unreadCount }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="action-buttons" style="margin-top: 20px;">
            <el-button type="primary" @click="connect" :disabled="isConnected">
            连接
          </el-button>
            <el-button type="danger" @click="disconnect" :disabled="!isConnected">
            断开
          </el-button>
            <el-button type="success" @click="sendTestMessage" :disabled="!isConnected">
              发送测试消息
          </el-button>
        </div>
        </el-col>
        
        <el-col :span="12">
          <h3>消息日志</h3>
          <div class="message-log">
            <el-alert
              v-if="messages.length === 0"
              title="暂无消息"
              type="info"
              :closable="false"
            />
            <div v-else class="message-list">
              <div
                v-for="(message, index) in messages"
                :key="index"
                class="message-item"
                :class="message.type"
              >
                <div class="message-header">
                  <span class="message-time">{{ message.timestamp }}</span>
                  <el-tag :type="getMessageTypeColor(message.type)" size="small">
                    {{ message.type }}
                  </el-tag>
                </div>
                <div class="message-content">
                  <pre>{{ JSON.stringify(message.data, null, 2) }}</pre>
                </div>
              </div>
        </div>
      </div>

          <div class="log-actions" style="margin-top: 10px;">
            <el-button size="small" @click="clearMessages">清空日志</el-button>
            <el-button size="small" @click="exportMessages">导出日志</el-button>
          </div>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <div class="test-results">
        <h3>测试结果</h3>
        <el-alert
          v-if="testResults.length === 0"
          title="暂无测试结果"
          type="info"
          :closable="false"
        />
        <div v-else>
          <el-timeline>
            <el-timeline-item
              v-for="(result, index) in testResults"
              :key="index"
              :timestamp="result.timestamp"
              :type="result.type"
            >
              <h4>{{ result.title }}</h4>
              <p>{{ result.content }}</p>
              <p v-if="result.details" class="details">
                <strong>详细信息:</strong> {{ result.details }}
              </p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useWebSocket } from '@/composables/useWebSocket'
import { wsService, WS_STATE } from '@/utils/websocket'

const { isConnected, connectionState, unreadCount, connect, disconnect } = useWebSocket()

const messages = ref<Array<{
  type: string
  data: any
  timestamp: string
}>>([])

const testResults = ref<Array<{
  title: string
  content: string
  details?: string
  timestamp: string
  type: 'success' | 'warning' | 'error' | 'info'
}>>([])

// 计算连接状态
const connectionStatus = computed(() => {
  if (isConnected.value) {
    return { type: 'success', text: '已连接' }
  } else if (connectionState.value === WS_STATE.CONNECTING) {
    return { type: 'warning', text: '连接中' }
  } else {
    return { type: 'danger', text: '未连接' }
  }
})

// 添加测试结果
const addTestResult = (title: string, content: string, type: 'success' | 'warning' | 'error' | 'info' = 'info', details?: string) => {
  testResults.value.unshift({
    title,
    content,
    details,
    timestamp: new Date().toLocaleString(),
    type
  })
}

// 添加消息到日志
const addMessage = (type: string, data: any) => {
  messages.value.unshift({
    type,
    data,
    timestamp: new Date().toLocaleString()
  })
  
  // 限制消息数量
  if (messages.value.length > 100) {
    messages.value = messages.value.slice(0, 100)
  }
}

// 获取消息类型颜色
const getMessageTypeColor = (type: string) => {
  const colors = {
    'task_notification': 'success',
    'project_notification': 'primary',
    'system_notification': 'warning',
    'team_notification': 'info',
    'heartbeat': 'info',
    'error': 'danger'
  }
  return colors[type as keyof typeof colors] || 'info'
}

// 发送测试消息
const sendTestMessage = () => {
  try {
    wsService.send({
      type: 'test',
      data: {
        message: '这是一条测试消息',
        timestamp: Date.now()
      }
    })
    addTestResult('发送测试消息', '已发送测试消息到WebSocket服务器', 'success')
  } catch (error: any) {
    addTestResult('发送测试消息', '发送失败', 'error', error.message)
  }
}

// 清空消息日志
const clearMessages = () => {
  messages.value = []
  addTestResult('清空日志', '已清空消息日志', 'info')
}

// 导出消息日志
const exportMessages = () => {
  try {
    const data = JSON.stringify(messages.value, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `websocket-messages-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    addTestResult('导出日志', '已导出消息日志', 'success')
  } catch (error: any) {
    addTestResult('导出日志', '导出失败', 'error', error.message)
  }
}

// 监听WebSocket消息
const handleWebSocketMessage = (event: Event) => {
  const customEvent = event as CustomEvent
  const message = customEvent.detail
  
  console.log('收到WebSocket消息:', message)
  addMessage('received', message)
  
  // 根据消息类型处理
  if (message.type === 'task_notification') {
    addMessage('task_notification', message)
    addTestResult('任务通知', `收到任务通知: ${message.task_title || '未知任务'}`, 'success')
  } else if (message.type === 'project_notification') {
    addMessage('project_notification', message)
    addTestResult('项目通知', `收到项目通知: ${message.project_name || '未知项目'}`, 'success')
  } else if (message.type === 'system_notification') {
    addMessage('system_notification', message)
    addTestResult('系统通知', `收到系统通知: ${message.title || '未知通知'}`, 'success')
  } else if (message.type === 'heartbeat') {
    addMessage('heartbeat', message)
  } else {
    addMessage('unknown', message)
  }
}

// 监听连接状态变化
const handleConnectionChange = () => {
  if (isConnected.value) {
    addTestResult('连接状态', 'WebSocket连接已建立', 'success')
  } else {
    addTestResult('连接状态', 'WebSocket连接已断开', 'warning')
  }
}

onMounted(() => {
  // 监听WebSocket消息
  window.addEventListener('websocket-message', handleWebSocketMessage)
  
  // 监听连接状态变化
  window.addEventListener('websocket-connect', handleConnectionChange)
  window.addEventListener('websocket-disconnect', handleConnectionChange)
  
  addTestResult('页面加载', 'WebSocket测试页面已加载', 'info')
})

onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('websocket-message', handleWebSocketMessage)
  window.removeEventListener('websocket-connect', handleConnectionChange)
  window.removeEventListener('websocket-disconnect', handleConnectionChange)
})
</script>

<style scoped>
.websocket-test {
  padding: 20px;
}

.test-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-log {
  height: 300px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  background: #fafafa;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-item {
  padding: 10px;
  border-radius: 4px;
  background: white;
  border-left: 4px solid #409eff;
}

.message-item.task_notification {
  border-left-color: #67c23a;
}

.message-item.project_notification {
  border-left-color: #409eff;
}

.message-item.system_notification {
  border-left-color: #e6a23c;
}

.message-item.team_notification {
  border-left-color: #909399;
}

.message-item.heartbeat {
  border-left-color: #f56c6c;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-content {
  font-size: 12px;
  color: #606266;
}

.message-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.test-results {
  margin-top: 20px;
}

.details {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  word-break: break-all;
}

h3 {
  margin-bottom: 16px;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.log-actions {
  display: flex;
  gap: 10px;
}
</style> 
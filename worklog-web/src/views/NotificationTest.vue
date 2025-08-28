<template>
  <div class="notification-test">
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <span>通知系统测试</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <h3>前端通知测试</h3>
          <el-button type="primary" @click="testTaskNotification" style="margin: 8px;">
            测试任务通知
          </el-button>
          <el-button type="success" @click="testTeamNotification" style="margin: 8px;">
            测试团队通知
          </el-button>
          <el-button type="warning" @click="testSystemNotification" style="margin: 8px;">
            测试系统通知
          </el-button>
          <el-button type="info" @click="testWorklogNotification" style="margin: 8px;">
            测试工作日志通知
          </el-button>
          <el-button type="danger" @click="testProjectNotification" style="margin: 8px;">
            测试项目通知
          </el-button>
        </el-col>
        
        <el-col :span="12">
          <h3>WebSocket连接状态</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="连接状态">
              <el-tag :type="isConnected ? 'success' : 'danger'">
                {{ isConnected ? '已连接' : '未连接' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="未读消息数">
              {{ unreadCount }}
            </el-descriptions-item>
            <el-descriptions-item label="最后接收时间">
              {{ lastMessageTime || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-row :gutter="20">
        <el-col :span="24">
          <h3>后端通知测试</h3>
          <el-alert
            title="提示"
            description="以下测试会触发真实的后端通知，请确保WebSocket连接正常"
            type="info"
            show-icon
            style="margin-bottom: 16px;"
          />
          
          <el-row :gutter="16">
            <el-col :span="8">
              <el-card shadow="hover">
                <template #header>
                  <span>任务相关测试</span>
                </template>
                <el-button type="primary" @click="createTestTask" style="width: 100%; margin-bottom: 8px;">
                  创建测试任务
                </el-button>
                <el-button type="success" @click="assignTestTask" style="width: 100%; margin-bottom: 8px;">
                  分配测试任务
                </el-button>
                <el-button type="warning" @click="changeTaskStatus" style="width: 100%; margin-bottom: 8px;">
                  变更任务状态
                </el-button>
                <el-button type="info" @click="addTaskComment" style="width: 100%; margin-bottom: 8px;">
                  添加任务评论
                </el-button>
                <el-button type="danger" @click="completeTestTask" style="width: 100%;">
                  完成测试任务
                </el-button>
              </el-card>
            </el-col>
            
            <el-col :span="8">
              <el-card shadow="hover">
                <template #header>
                  <span>团队相关测试</span>
                </template>
                <el-button type="primary" @click="inviteTeamMember" style="width: 100%; margin-bottom: 8px;">
                  邀请团队成员
                </el-button>
                <el-button type="success" @click="joinTeam" style="width: 100%; margin-bottom: 8px;">
                  加入团队
                </el-button>
                <el-button type="warning" @click="leaveTeam" style="width: 100%;">
                  离开团队
                </el-button>
              </el-card>
            </el-col>
            
            <el-col :span="8">
              <el-card shadow="hover">
                <template #header>
                  <span>其他测试</span>
                </template>
                <el-button type="primary" @click="createTestProject" style="width: 100%; margin-bottom: 8px;">
                  创建测试项目
                </el-button>
                <el-button type="success" @click="submitWorklog" style="width: 100%; margin-bottom: 8px;">
                  提交工作日志
                </el-button>
                <el-button type="warning" @click="sendSystemNotification" style="width: 100%;">
                  发送系统通知
                </el-button>
              </el-card>
            </el-col>
          </el-row>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-row :gutter="20">
        <el-col :span="24">
          <h3>接收到的消息</h3>
          <el-table :data="receivedMessages" style="width: 100%">
            <el-table-column prop="timestamp" label="时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="120">
              <template #default="scope">
                <el-tag :type="getMessageTypeColor(scope.row.type)">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button size="small" @click="viewMessageDetail(scope.row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 消息详情对话框 -->
    <el-dialog v-model="messageDetailVisible" title="消息详情" width="600px">
      <pre>{{ JSON.stringify(selectedMessage, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useNotification } from '@/composables/useNotification'
import { useWebSocket } from '@/composables/useWebSocket'
import { ElMessage } from 'element-plus'
import { messageApi } from '@/api/message'

const notification = useNotification()
const { isConnected, unreadCount } = useWebSocket()

// 接收到的消息列表
const receivedMessages = ref<any[]>([])
const messageDetailVisible = ref(false)
const selectedMessage = ref<any>(null)
const lastMessageTime = ref<string>('')

// 前端通知测试
const testTaskNotification = () => {
  notification.showTaskNotification('任务通知', '您有一个新的任务分配', { taskId: 1, taskTitle: '测试任务' })
}

const testTeamNotification = () => {
  notification.showTeamNotification('团队通知', '有新的团队成员加入', { teamId: 1, memberName: '张三' })
}

const testSystemNotification = () => {
  notification.showSystemNotification('系统通知', '系统将在今晚进行维护', { maintenanceTime: '22:00-24:00' })
}

const testWorklogNotification = () => {
  notification.showWorklogNotification('工作日志提醒', '请及时填写今日工作日志', { date: new Date().toISOString().split('T')[0] })
}

const testProjectNotification = () => {
  notification.showProjectNotification('项目通知', '项目状态已更新', { projectId: 1, projectName: '测试项目' })
}

// 后端通知测试
const createTestTask = async () => {
  try {
    const response = await fetch('/api/v1/tasks/quick', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        title: '通知测试任务',
        description: '这是一个用于测试通知功能的任务',
        team_id: 1,
        priority: 'medium'
      })
    })
    
    if (response.ok) {
      ElMessage.success('测试任务创建成功，请查看通知')
    } else {
      ElMessage.error('创建测试任务失败')
    }
  } catch (error) {
    ElMessage.error('创建测试任务失败')
  }
}

const assignTestTask = async () => {
  try {
    const response = await fetch('/api/v1/tasks/1/assign?assignee_id=1', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (response.ok) {
      ElMessage.success('任务分配成功，请查看通知')
    } else {
      ElMessage.error('任务分配失败')
    }
  } catch (error) {
    ElMessage.error('任务分配失败')
  }
}

const changeTaskStatus = async () => {
  try {
    const response = await fetch('/api/v1/tasks/1', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        status: 'in_progress'
      })
    })
    
    if (response.ok) {
      ElMessage.success('任务状态变更成功，请查看通知')
    } else {
      ElMessage.error('任务状态变更失败')
    }
  } catch (error) {
    ElMessage.error('任务状态变更失败')
  }
}

const addTaskComment = async () => {
  try {
    const response = await fetch('/api/v1/tasks/1/comments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        content: '这是一条测试评论'
      })
    })
    
    if (response.ok) {
      ElMessage.success('评论添加成功，请查看通知')
    } else {
      ElMessage.error('评论添加失败')
    }
  } catch (error) {
    ElMessage.error('评论添加失败')
  }
}

const completeTestTask = async () => {
  try {
    const response = await fetch('/api/v1/tasks/1/complete', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (response.ok) {
      ElMessage.success('任务完成成功，请查看通知')
    } else {
      ElMessage.error('任务完成失败')
    }
  } catch (error) {
    ElMessage.error('任务完成失败')
  }
}

const inviteTeamMember = async () => {
  ElMessage.info('团队邀请功能待实现')
}

const joinTeam = async () => {
  ElMessage.info('加入团队功能待实现')
}

const leaveTeam = async () => {
  ElMessage.info('离开团队功能待实现')
}

const createTestProject = async () => {
  ElMessage.info('创建项目功能待实现')
}

const submitWorklog = async () => {
  ElMessage.info('提交工作日志功能待实现')
}

const sendSystemNotification = async () => {
  ElMessage.info('系统通知功能待实现')
}

// 消息处理
const handleWebSocketMessage = (message: any) => {
  receivedMessages.value.unshift({
    timestamp: new Date().toISOString(),
    type: message.type || 'unknown',
    title: message.title || message.notification_type || '通知',
    content: message.content || JSON.stringify(message),
    data: message
  })
  
  // 限制消息数量
  if (receivedMessages.value.length > 50) {
    receivedMessages.value = receivedMessages.value.slice(0, 50)
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

const getMessageTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'task_notification': 'primary',
    'team_notification': 'success',
    'system_notification': 'warning',
    'worklog_notification': 'info',
    'project_notification': 'danger'
  }
  return colorMap[type] || 'default'
}

const viewMessageDetail = (message: any) => {
  selectedMessage.value = message
  messageDetailVisible.value = true
}

// 监听WebSocket消息
onMounted(() => {
  window.addEventListener('websocket-message', (event: any) => {
    handleWebSocketMessage(event.detail)
  })
})

onUnmounted(() => {
  window.removeEventListener('websocket-message', handleWebSocketMessage)
})
</script>

<style scoped>
.notification-test {
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

h3 {
  margin-bottom: 16px;
  color: #303133;
}
</style> 
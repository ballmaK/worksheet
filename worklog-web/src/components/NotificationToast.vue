<template>
  <Teleport to="body">
    <TransitionGroup
      name="notification"
      tag="div"
      class="notification-container"
    >
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="['notification-toast', `notification-${notification.type}`]"
        @click="handleNotificationClick(notification)"
      >
        <div class="notification-icon">
          <el-icon>
            <Check v-if="notification.type === 'task'" />
            <User v-else-if="notification.type === 'team'" />
            <Warning v-else-if="notification.type === 'system'" />
            <Timer v-else-if="notification.type === 'worklog'" />
            <Folder v-else-if="notification.type === 'project'" />
            <Bell v-else />
          </el-icon>
        </div>
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-message">{{ notification.content }}</div>
          <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
        </div>
        <div class="notification-actions">
          <el-button
            type="text"
            size="small"
            @click.stop="closeNotification(notification.id)"
            class="close-btn"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="notification-progress" :style="{ width: `${notification.progress}%` }"></div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Check, User, Warning, Timer, Folder, Bell, Close } from '@element-plus/icons-vue'

interface Notification {
  id: string
  title: string
  content: string
  type: 'task' | 'team' | 'system' | 'worklog' | 'project' | 'general'
  timestamp: number
  progress: number
  data?: any
}

const router = useRouter()
const notifications = ref<Notification[]>([])
let progressIntervals: Map<string, number> = new Map()

// 添加通知
const addNotification = (notification: Omit<Notification, 'id' | 'progress'>) => {
  const id = `notification-${Date.now()}-${Math.random()}`
  const newNotification: Notification = {
    ...notification,
    id,
    progress: 100
  }
  
  notifications.value.unshift(newNotification)
  
  // 开始进度条倒计时
  startProgress(newNotification)
  
  // 自动移除通知
  setTimeout(() => {
    closeNotification(id)
  }, 5000) // 5秒后自动关闭
}

// 开始进度条倒计时
const startProgress = (notification: Notification) => {
  const interval = setInterval(() => {
    const index = notifications.value.findIndex(n => n.id === notification.id)
    if (index !== -1) {
      notifications.value[index].progress -= 2 // 每100ms减少2%
      if (notifications.value[index].progress <= 0) {
        clearInterval(interval)
        progressIntervals.delete(notification.id)
      }
    } else {
      clearInterval(interval)
      progressIntervals.delete(notification.id)
    }
  }, 100)
  
  progressIntervals.set(notification.id, interval)
}

// 关闭通知
const closeNotification = (id: string) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index !== -1) {
    notifications.value.splice(index, 1)
    
    // 清理定时器
    const interval = progressIntervals.get(id)
    if (interval) {
      clearInterval(interval)
      progressIntervals.delete(id)
    }
  }
}

// 处理通知点击
const handleNotificationClick = (notification: Notification) => {
  // 根据消息类型跳转到相应页面
  switch (notification.type) {
    case 'task':
      if (notification.data?.task_id) {
        router.push(`/tasks/${notification.data.task_id}`)
      } else {
        router.push('/tasks')
      }
      break
    case 'team':
      router.push('/teams')
      break
    case 'worklog':
      router.push('/work-logs')
      break
    case 'project':
      if (notification.data?.project_id) {
        router.push(`/projects/${notification.data.project_id}`)
      } else {
        router.push('/projects')
      }
      break
    default:
      router.push('/messages')
  }
  
  // 关闭通知
  closeNotification(notification.id)
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const now = Date.now()
  const diff = now - timestamp
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 1天内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return new Date(timestamp).toLocaleDateString()
  }
}

// 暴露方法给父组件
defineExpose({
  addNotification
})

// 组件卸载时清理所有定时器
onUnmounted(() => {
  progressIntervals.forEach(interval => clearInterval(interval))
  progressIntervals.clear()
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
}

.notification-toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  min-width: 320px;
  max-width: 400px;
}

.notification-toast:hover {
  transform: translateX(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.16);
}

.notification-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

.notification-task .notification-icon {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
}

.notification-team .notification-icon {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
}

.notification-system .notification-icon {
  background: linear-gradient(135deg, #e6a23c, #f0ad4e);
  color: white;
}

.notification-worklog .notification-icon {
  background: linear-gradient(135deg, #909399, #c0c4cc);
  color: white;
}

.notification-project .notification-icon {
  background: linear-gradient(135deg, #9c27b0, #ba68c8);
  color: white;
}

.notification-general .notification-icon {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.4;
}

.notification-message {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.notification-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.close-btn {
  padding: 4px;
  color: #909399;
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: #606266;
}

.notification-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #67c23a, #85ce61);
  transition: width 0.1s linear;
}

/* 动画效果 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notification-container {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .notification-toast {
    min-width: auto;
    max-width: none;
  }
}
</style> 
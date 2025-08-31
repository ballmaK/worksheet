<template>
  <div class="websocket-status" :title="statusText">
    <!-- 连接状态图标 -->
    <el-icon :class="statusClass" class="status-icon">
      <Connection v-if="isConnected" />
      <Loading v-else-if="connectionState === WS_STATE.CONNECTING" />
      <Close v-else />
    </el-icon>

    <!-- 未读消息数量 -->
    <div v-if="unreadCount > 0" class="unread-badge">
      {{ unreadCount > 99 ? '99+' : unreadCount }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Connection, Close, Loading } from '@element-plus/icons-vue'
import { WS_STATE } from '@/utils/websocket'

interface Props {
  isConnected: boolean
  connectionState: number
  unreadCount: number
}

const props = defineProps<Props>()

// 计算状态样式类
const statusClass = computed(() => {
  if (props.isConnected) {
    return 'connected'
  } else if (props.connectionState === WS_STATE.CONNECTING) {
    return 'connecting'
  } else {
    return 'disconnected'
  }
})

// 计算状态文本
const statusText = computed(() => {
  if (props.isConnected) {
    return 'WebSocket已连接'
  } else if (props.connectionState === WS_STATE.CONNECTING) {
    return 'WebSocket连接中...'
  } else {
    return 'WebSocket未连接'
  }
})
</script>

<style scoped>
.websocket-status {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;
  position: relative;
}

.status-icon {
  font-size: 16px;
  transition: all 0.3s ease;
}

.status-icon.connected {
  color: #67c23a;
}

.status-icon.connecting {
  color: #e6a23c;
  animation: spin 1s linear infinite;
}

.status-icon.disconnected {
  color: #f56c6c;
}

.unread-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #f56c6c;
  color: white;
  border-radius: 8px;
  font-size: 10px;
  font-weight: bold;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .status-icon {
    font-size: 14px;
  }

  .unread-badge {
    min-width: 14px;
    height: 14px;
    font-size: 9px;
  }
}
</style> 
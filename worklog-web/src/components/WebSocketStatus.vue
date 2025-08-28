<template>
  <div class="websocket-status">
    <!-- 连接状态指示器 -->
    <div class="status-indicator" :class="statusClass" :title="statusText">
      <el-icon v-if="isConnected" class="status-icon">
        <Connection />
      </el-icon>
      <el-icon v-else-if="connectionState === WS_STATE.CONNECTING" class="status-icon connecting">
        <Loading />
      </el-icon>
      <el-icon v-else class="status-icon">
        <Close />
      </el-icon>
    </div>

    <!-- 未读消息数量 -->
    <div v-if="unreadCount > 0" class="unread-badge">
      {{ unreadCount > 99 ? '99+' : unreadCount }}
    </div>

    <!-- 连接状态提示 -->
    <el-tooltip :content="statusText" placement="bottom">
      <span class="status-text">{{ statusText }}</span>
    </el-tooltip>
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
  gap: 8px;
  padding: 6px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.websocket-status:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  transition: all 0.3s ease;
  position: relative;
}

.status-icon {
  font-size: 14px;
  color: white;
}

.status-indicator.connected {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
  animation: pulse 2s infinite;
}

.status-indicator.connecting {
  background: linear-gradient(135deg, #e6a23c, #f0ad4e);
  box-shadow: 0 2px 8px rgba(230, 162, 60, 0.3);
}

.status-indicator.disconnected {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.status-icon.connecting {
  animation: spin 1s linear infinite;
}

.unread-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
  border-radius: 10px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(245, 108, 108, 0.3);
  animation: bounce 1s infinite;
}

.status-text {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  font-weight: 500;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(103, 194, 58, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-3px);
  }
  60% {
    transform: translateY(-1px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .websocket-status {
    padding: 4px 8px;
    gap: 6px;
  }

  .status-text {
    display: none;
  }

  .unread-badge {
    min-width: 18px;
    height: 18px;
    font-size: 10px;
  }

  .status-indicator {
    width: 20px;
    height: 20px;
  }

  .status-icon {
    font-size: 12px;
  }
}
</style> 
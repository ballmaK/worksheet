<template>
  <div class="work-mode-card" :class="{ 'work-mode-active': isWorkMode }">
    <div class="card-header">
      <div class="header-icon">
        <el-icon :size="24" :color="isWorkMode ? '#dc3545' : '#409eff'">
          <Monitor v-if="!isWorkMode" />
          <Close v-else />
        </el-icon>
      </div>
      <div class="header-content">
        <h3 class="card-title">{{ isWorkMode ? '工作模式已开启' : '进入工作模式' }}</h3>
        <p class="card-description">
          {{ isWorkMode ? '专注工作，悬浮任务栏已激活' : '切换到专注工作模式，隐藏主界面' }}
        </p>
      </div>
    </div>
    
    <div class="card-body">
      <div class="mode-features">
        <div class="feature-item" v-for="feature in currentFeatures" :key="feature.text">
          <el-icon :color="feature.color" :size="16">
            <component :is="feature.icon" />
          </el-icon>
          <span>{{ feature.text }}</span>
        </div>
      </div>
      
      <div class="action-section">
        <el-button
          :type="isWorkMode ? 'danger' : 'primary'"
          :icon="isWorkMode ? 'Close' : 'Monitor'"
          @click="toggleWorkMode"
          :loading="loading"
          size="large"
          class="toggle-btn"
        >
          {{ isWorkMode ? '退出工作模式' : '进入工作模式' }}
        </el-button>
        
        <div class="shortcut-hint" v-if="!isWorkMode">
          <el-icon><Key /></el-icon>
          <span>快捷键: Ctrl+Shift+W</span>
        </div>
      </div>
    </div>
    
    <!-- 工作模式状态指示器 -->
    <div v-if="isWorkMode" class="status-indicator">
      <div class="indicator-dot"></div>
      <span>工作模式运行中</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElButton, ElIcon, ElMessage } from 'element-plus'
import { Monitor, Close, Key, Timer, Setting, Lock } from '@element-plus/icons-vue'

const isWorkMode = ref(false)
const loading = ref(false)

// 功能特性列表
const normalFeatures = [
  { icon: 'Timer', text: '实时时间追踪', color: '#409eff' },
  { icon: 'Setting', text: '快速任务切换', color: '#67c23a' },
  { icon: 'Lock', text: '专注工作环境', color: '#e6a23c' }
]

const workModeFeatures = [
  { icon: 'Timer', text: '悬浮任务栏', color: '#dc3545' },
  { icon: 'Key', text: '全局快捷键', color: '#dc3545' },
  { icon: 'Lock', text: '最小化干扰', color: '#dc3545' }
]

const currentFeatures = computed(() => {
  return isWorkMode.value ? workModeFeatures : normalFeatures
})

// 检查工作模式状态
const checkWorkMode = async () => {
  try {
    const electronAPI = (window as any).electronAPI
    if (electronAPI && electronAPI.getWorkMode) {
      isWorkMode.value = await electronAPI.getWorkMode()
    }
  } catch (error) {
    console.error('获取工作模式状态失败:', error)
  }
}

// 切换工作模式
const toggleWorkMode = async () => {
  const electronAPI = (window as any).electronAPI
  if (!electronAPI || !electronAPI.toggleWorkMode) {
    ElMessage.warning('此功能仅在桌面客户端中可用')
    return
  }
  
  loading.value = true
  try {
    isWorkMode.value = await electronAPI.toggleWorkMode()
    
    if (isWorkMode.value) {
      ElMessage.success('已进入工作模式，主窗口已隐藏')
    } else {
      ElMessage.info('已退出工作模式，恢复正常界面')
    }
  } catch (error) {
    console.error('切换工作模式失败:', error)
    ElMessage.error('切换工作模式失败')
  } finally {
    loading.value = false
  }
}

// 监听工作模式变化
const handleWorkModeChange = (event: any) => {
  if (event.detail && typeof event.detail.isWorkMode === 'boolean') {
    isWorkMode.value = event.detail.isWorkMode
  }
}

onMounted(() => {
  checkWorkMode()
  window.addEventListener('work-mode-changed', handleWorkModeChange)
  setInterval(checkWorkMode, 5000)
})
</script>

<style scoped>
.work-mode-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  min-height: 200px;
}

.work-mode-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(64, 158, 255, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.work-mode-card:hover::before {
  opacity: 1;
}

.work-mode-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  border-radius: 8px;
  color: white;
  flex-shrink: 0;
}

.work-mode-active .header-icon {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
}

.header-content {
  flex: 1;
}

.card-title {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-description {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mode-features {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.action-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.toggle-btn {
  width: 100%;
  height: 40px;
  font-weight: 600;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.shortcut-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  padding: 6px 12px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(64, 158, 255, 0.2);
}

.status-indicator {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(220, 53, 69, 0.1);
  border-radius: 20px;
  border: 1px solid rgba(220, 53, 69, 0.2);
}

.indicator-dot {
  width: 8px;
  height: 8px;
  background: #dc3545;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7);
  }
  70% {
    box-shadow: 0 0 0 4px rgba(220, 53, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
  }
}

.status-indicator span {
  font-size: 12px;
  color: #dc3545;
  font-weight: 600;
}

/* 工作模式激活状态 */
.work-mode-card.work-mode-active {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border-color: #ffc107;
  box-shadow: 0 4px 20px rgba(255, 193, 7, 0.2);
}

.work-mode-card.work-mode-active::before {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 193, 7, 0.2) 100%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .work-mode-card {
    padding: 16px;
  }
  
  .card-header {
    gap: 12px;
  }
  
  .header-icon {
    width: 40px;
    height: 40px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .toggle-btn {
    height: 44px;
  }
}

/* 加载状态 */
.toggle-btn.is-loading {
  opacity: 0.7;
  pointer-events: none;
}
</style> 
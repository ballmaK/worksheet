<template>
  <div v-if="showTips" class="operation-tips">
    <div class="tips-container">
      <!-- 提示内容 -->
      <div class="tip-content">
        <el-icon class="tip-icon" :class="currentTip.type">
          <component :is="currentTip.icon" />
        </el-icon>
        <span class="tip-text">{{ currentTip.text }}</span>
      </div>
      
      <!-- 控制按钮 -->
      <div class="tips-controls">
        <!-- 切换按钮 -->
        <el-button 
          type="text" 
          size="small" 
          @click="prevTip"
          :disabled="currentIndex === 0"
        >
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        
        <!-- 指示器 -->
        <div class="tip-indicators">
          <span 
            v-for="(tip, index) in tips" 
            :key="index"
            class="indicator"
            :class="{ active: index === currentIndex }"
            @click="goToTip(index)"
          ></span>
        </div>
        
        <el-button 
          type="text" 
          size="small" 
          @click="nextTip"
          :disabled="currentIndex === tips.length - 1"
        >
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        
        <!-- 关闭按钮 -->
        <el-button 
          type="text" 
          size="small" 
          @click="closeTips"
          class="close-btn"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  ArrowLeft, 
  ArrowRight, 
  Close,
  Key,
  Timer,
  Star,
  Bell,
  User,
  Document,
  InfoFilled,
  Setting
} from '@element-plus/icons-vue'

// 提示数据
const tips = [
  {
    text: '💡 快捷键：Ctrl + N 快速创建新任务',
    icon: 'Key',
    type: 'keyboard'
  },
  {
    text: '⏰ 工作模式：专注模式下自动记录工作时间',
    icon: 'Timer',
    type: 'timer'
  },
  {
    text: '🎯 拖拽任务卡片可快速调整任务状态',
    icon: 'Setting',
    type: 'target'
  },
  {
    text: '⭐ 双击任务可快速查看详情',
    icon: 'Star',
    type: 'star'
  },
  {
    text: '💡 悬浮任务栏：随时记录工作进度',
    icon: 'InfoFilled',
    type: 'lightbulb'
  },
  {
    text: '🔮 智能提醒：系统会自动提醒您的重要任务',
    icon: 'Bell',
    type: 'magic'
  },
  {
    text: '🧭 团队协作：邀请同事加入团队共同管理项目',
    icon: 'User',
    type: 'compass'
  },
  {
    text: '📊 数据统计：查看个人和团队的工作效率报告',
    icon: 'Document',
    type: 'stats'
  }
]

const currentIndex = ref(0)
const showTips = ref(true)
let autoPlayTimer: number | null = null

const currentTip = computed(() => tips[currentIndex.value])

// 切换到下一个提示
const nextTip = () => {
  if (currentIndex.value < tips.length - 1) {
    currentIndex.value++
  } else {
    currentIndex.value = 0
  }
  resetAutoPlay()
}

// 切换到上一个提示
const prevTip = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  } else {
    currentIndex.value = tips.length - 1
  }
  resetAutoPlay()
}

// 跳转到指定提示
const goToTip = (index: number) => {
  currentIndex.value = index
  resetAutoPlay()
}

// 关闭提示
const closeTips = () => {
  showTips.value = false
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
    autoPlayTimer = null
  }
}

// 重置自动播放
const resetAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
  }
  startAutoPlay()
}

// 开始自动播放
const startAutoPlay = () => {
  autoPlayTimer = setInterval(() => {
    nextTip()
  }, 6000) // 6秒切换一次
}

// 组件挂载时开始自动播放
onMounted(() => {
  startAutoPlay()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
  }
})
</script>

<style scoped>
.operation-tips {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 0;
  position: relative;
  z-index: 1000;
}

.tips-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.tip-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.tip-icon {
  font-size: 18px;
  opacity: 0.9;
}

.tip-icon.keyboard {
  color: #ffd700;
}

.tip-icon.timer {
  color: #00ff88;
}

.tip-icon.target {
  color: #ff6b6b;
}

.tip-icon.star {
  color: #ffd700;
}

.tip-icon.lightbulb {
  color: #ffd700;
}

.tip-icon.magic {
  color: #a855f7;
}

.tip-icon.compass {
  color: #3b82f6;
}

.tip-icon.stats {
  color: #10b981;
}

.tip-text {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.tips-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tip-indicators {
  display: flex;
  gap: 4px;
  margin: 0 8px;
}

.indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background-color: white;
  transform: scale(1.2);
}

.indicator:hover {
  background-color: rgba(255, 255, 255, 0.8);
}

.close-btn {
  color: rgba(255, 255, 255, 0.8);
  margin-left: 8px;
}

.close-btn:hover {
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tips-container {
    padding: 0 12px;
    flex-direction: column;
    gap: 8px;
  }
  
  .tip-content {
    text-align: center;
  }
  
  .tip-text {
    font-size: 13px;
  }
  
  .tips-controls {
    gap: 4px;
  }
  
  .tip-indicators {
    margin: 0 4px;
  }
}

/* 动画效果 */
.operation-tips {
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.tip-content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style> 
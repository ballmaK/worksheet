<template>
  <QuickCreateTask
      @task-created="handleTaskCreated"
      @task-create-error="handleTaskCreateError"
      class="quick-create-wrapper"
      tabindex="0"
  >
    <div 
        class="floating-task-bar"
        :class="{ 
            'expanded': isExpanded,
            'minimized': isMinimized,
            'compact': isCompactMode,
            'working': currentTask && isWorking,
            'dragging': isDragging
        }"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
        @mousedown="startDrag"
    >
      <!-- 简洁模式显示 -->
      <div v-if="isCompactMode" class="compact-mode">
        <div class="compact-header">
          <div class="compact-task-info" :class="{ 'switching': isSwitchingTask }">
            <div class="compact-task-title">
              <el-icon class="compact-icon"><User /></el-icon>
              <span class="task-text">{{ currentTask?.title || '无当前任务' }}</span>
        </div>
            <div class="compact-timer">
              <el-icon class="timer-icon"><Clock /></el-icon>
              <span class="time-text">{{ formatTime(elapsedTime) }}</span>
            </div>
            <!-- 任务切换指示器 -->
            <div class="compact-task-indicator" v-if="tasks.length > 1">
              <span class="indicator-text">{{ getCurrentTaskIndex() + 1 }}/{{ tasks.length }}</span>
            </div>
          </div>
          <div class="compact-controls">
            <!-- 任务切换按钮 -->
          <el-button
                type="info"
                circle
              size="small"
                @click="switchToPreviousTask"
                class="compact-switch-btn"
                :disabled="tasks.length <= 1"
                title="上一个任务 (←)"
            >
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <el-button
                :type="isWorking ? 'danger' : 'success'"
                circle
                size="large"
                @click="toggleWorkStatus"
                class="compact-play-btn"
                :class="{ 'playing': isWorking }"
            >
              <el-icon><component :is="isWorking ? VideoPause : VideoPlay" /></el-icon>
            </el-button>
            <el-button
                type="info"
                circle
                size="small"
                @click="switchToNextTask"
                class="compact-switch-btn"
                :disabled="tasks.length <= 1"
                title="下一个任务 (→)"
            >
              <el-icon><ArrowRight /></el-icon>
            </el-button>
            <el-button
                type="warning"
                circle
                size="small"
                @click="completeCurrentTask"
                class="compact-complete-btn"
                v-if="currentTask"
            >
              <el-icon><CircleCheck /></el-icon>
            </el-button>
            <el-button
                type="info"
                circle
                size="small"
                @click="stopCurrentTask"
                class="compact-stop-btn"
            >
              <el-icon><CircleClose /></el-icon>
          </el-button>
        </div>
        </div>
        
        <!-- 快捷键提示 -->
        <div class="compact-shortcuts" v-if="showShortcutsHint">
          <span class="shortcut-hint">← → 切换任务 | Enter 启动/停止 | Ctrl+Enter 切换模式</span>
        </div>
      </div>

      <!-- 短时间弹窗提示 -->
      <div v-if="showCompactTip" class="compact-tip-toast">
        <span class="tip-toast-text">{{ compactTipText }}</span>
      </div>

      <!-- 任务栏内容 -->
      <div class="task-bar-content" v-show="!isMinimized && !isCompactMode">
        <!-- 当前任务显示 -->
        <div v-if="currentTask" class="current-task-section">
          <div class="task-info">
            <div class="task-title">
              <el-icon class="task-icon"><User /></el-icon>
              {{ currentTask.title }}
            </div>
            <div class="task-meta">
              <div class="timer-container">
                <el-icon class="timer-icon"><Clock /></el-icon>
              <span class="timer">{{ formatTime(elapsedTime) }}</span>
              </div>
              <span class="status" :class="{ 'working': isWorking }">
                <el-icon class="status-icon">
                  <component :is="isWorking ? VideoPlay : VideoPause" />
                </el-icon>
                {{ isWorking ? '工作中' : '已暂停' }}
              </span>
            </div>
          </div>
          <div class="task-actions">
            <el-button
                :type="isWorking ? 'warning' : 'success'"
                size="small"
                @click="toggleWorkStatus"
                class="work-btn"
            >
              <el-icon><component :is="isWorking ? VideoPause : VideoPlay" /></el-icon>
              {{ isWorking ? '暂停工作' : '开始工作' }}
            </el-button>
            <el-button
                type="danger"
                size="small"
                @click="stopCurrentTask"
                class="stop-btn"
            >
              <el-icon><CircleClose /></el-icon>
              停止
            </el-button>
          </div>
        </div>

        <!-- 任务详情展示区域 -->
        <div v-if="currentTask && currentTask.description" class="task-detail-section">
          <div class="detail-header">
            <el-icon class="detail-icon"><InfoFilled /></el-icon>
            <span class="detail-title">任务内容</span>
          </div>
          <div class="detail-content">
            <div class="detail-item">
              <span class="description">{{ currentTask.description }}</span>
            </div>
          </div>
        </div>

        <!-- 任务列表 -->
        <div class="task-list-section">
          <div class="section-header">
            <div class="section-title-container">
              <el-icon class="section-icon"><Calendar /></el-icon>
              <span class="section-title">我的任务 ({{ tasks.length }})</span>
            </div>
            <div class="header-actions">
            <el-button
                type="text"
                size="small"
                @click="refreshTasks"
                class="refresh-btn"
                :loading="loading"
                  title="刷新任务列表"
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
            </div>
          </div>
          
          <div class="task-list">
            <div
                v-for="task in sortedTasks"
                :key="task.id"
                class="task-item"
                :class="{ 
                    'active': currentTask?.id === task.id,
                    'working': currentTask?.id === task.id && isWorking
                }"
                @click="handleTaskClick(task)"
                @dblclick="handleTaskDoubleClick(task)"
            >
              <!-- 装饰性光点 -->
              <div class="sparkle-dot"></div>
              
              <div class="task-item-content">
                <div class="task-item-header">
                <div class="task-item-title">
                  <el-icon class="task-item-icon"><User /></el-icon>
                  {{ task.title }}
                </div>
                  <div class="task-item-badges">
                  <span class="task-priority" :class="`priority-${task.priority}`">
                    <el-icon class="priority-icon">
                      <component :is="getPriorityIcon(task.priority)" />
                    </el-icon>
                    {{ getPriorityText(task.priority) }}
                  </span>
                  <span class="task-status">
                    <el-icon class="status-icon">
                      <component :is="getStatusIcon(task.status)" />
                    </el-icon>
                    {{ getStatusText(task.status) }}
                  </span>
                </div>
                </div>
                <div class="task-item-footer">
                  <div class="task-item-meta">
                    <span class="task-due-date" v-if="task.due_date">
                      <el-icon class="due-icon"><Clock /></el-icon>
                      {{ formatDate(task.due_date) }}
                    </span>
              </div>
              <div class="task-item-actions">
                <el-button
                    type="text"
                    size="small"
                    @click="handleTaskDoubleClick(task)"
                    class="switch-btn"
                        title="双击进入简洁模式"
                >
                  <el-icon><Switch /></el-icon>
                  切换
                </el-button>
              </div>
                </div>
              </div>
            </div>
            
            <!-- 空状态 -->
            <div v-if="tasks.length === 0" class="empty-state">
              <el-icon class="empty-icon"><Calendar /></el-icon>
              <p>暂无任务</p>
              <el-button type="primary" size="small" @click="refreshTasks">
                刷新任务
              </el-button>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="quick-actions">
          <el-button
              type="primary"
              size="small"
              @click="showTaskManagement"
              class="manage-btn"
          >
            <el-icon><Calendar /></el-icon>
            管理视图
          </el-button>
          <el-button
              type="success"
              size="small"
              @click="testQuickCreate"
              class="test-btn"
              title="测试快速创建功能"
          >
            <el-icon><Plus /></el-icon>
            测试创建
          </el-button>
        </div>
      </div>

      <!-- 最小化时的显示 -->
      <div v-if="isMinimized" class="minimized-content">
        <div class="minimized-task-info">
          <el-icon class="minimized-icon"><Clock /></el-icon>
          <span v-if="currentTask" class="minimized-task-title">
            {{ currentTask.title }}
          </span>
          <span v-else class="no-task">无当前任务</span>
        </div>
        <div class="minimized-timer" v-if="currentTask">
          <el-icon class="timer-icon"><Clock /></el-icon>
          {{ formatTime(elapsedTime) }}
        </div>
      </div>

      <!-- 拖拽手柄区域 -->
      <div class="drag-handle"></div>
    </div>
  </QuickCreateTask>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Clock, VideoPlay, VideoPause, CircleClose, CircleCheck, 
  Calendar, InfoFilled, Refresh, Star, StarFilled, Warning, 
  CircleCloseFilled, ArrowLeft, ArrowRight
} from '@element-plus/icons-vue'
import { taskApi, type Task } from '@/api/task'
import { workLogApi } from '@/api/workLog'
import QuickCreateTask from './QuickCreateTask.vue'

// 状态管理
const isExpanded = ref(false)
const isMinimized = ref(false)
const isCompactMode = ref(false)
const isCollapsed = ref(false)
const isWorking = ref(false)
const isDragging = ref(false)
const isSwitchingTask = ref(false)
const currentTask = ref<Task | null>(null)
const tasks = ref<Task[]>([])
const loading = ref(false)
const workStartTime = ref<Date | null>(null)
const dragStartPos = ref<{ x: number; y: number } | null>(null)
const windowStartPos = ref<{ x: number; y: number } | null>(null)
const showCompactTip = ref(false)
const compactTipText = ref('')
const timerInterval = ref<number | null>(null)
const showShortcutsHint = ref(false)
const currentTime = ref(Date.now()) // 添加当前时间响应式变量
const taskTotalDuration = ref(0) // 任务累计工作时间（毫秒）
const currentSessionDuration = ref(0) // 当前会话工作时间（毫秒）

// 计算当前工作时间（累计时间 + 当前会话时间）
const elapsedTime = computed(() => {
  if (!isWorking.value) {
    // 不工作时显示累计时间（小时转毫秒）
    return (currentTask.value?.actual_hours || 0) * 3600000
  }
  // 工作时显示累计时间 + 当前会话时间
  const totalAccumulated = (currentTask.value?.actual_hours || 0) * 3600000
  const currentSession = currentSessionTime.value
  return totalAccumulated + currentSession
})

// 计算当前会话时间
const currentSessionTime = computed(() => {
  if (!workStartTime.value || !isWorking.value) return 0
  return currentTime.value - workStartTime.value.getTime()
})

// 计算排序后的任务列表（执行中的任务置顶）
const sortedTasks = computed(() => {
  const workingTask = tasks.value.find(task => 
    task.status === 'in_progress' && isWorking.value && currentTask.value?.id === task.id
  )
  
  if (workingTask) {
    // 如果有正在执行的任务，将其置顶
    const otherTasks = tasks.value.filter(task => task.id !== workingTask.id)
    return [workingTask, ...otherTasks]
  }
  
  // 否则按原有顺序显示
  return tasks.value
})

// 获取任务状态类型
const getStatusType = (status?: string) => {
  const statusTypes: { [key: string]: string } = {
    'pending': 'info',
    'assigned': 'warning',
    'in_progress': 'primary',
    'review': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusTypes[status || ''] || 'info'
}

// 获取任务状态文本
const getStatusText = (status?: string) => {
  const statusTexts: { [key: string]: string } = {
    'pending': '待分派',
    'assigned': '已分派',
    'in_progress': '进行中',
    'review': '审核中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusTexts[status || ''] || status || '未知'
}

// 获取优先级文本
const getPriorityText = (priority?: string) => {
  const priorityTexts: { [key: string]: string } = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'urgent': '紧急'
  }
  return priorityTexts[priority || ''] || priority || ''
}

// 格式化时间显示
const formatTime = (milliseconds: number) => {
  const totalSeconds = Math.floor(milliseconds / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 启动计时器
const startTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
  timerInterval.value = setInterval(() => {
    // 更新当前时间以触发响应式更新
    currentTime.value = Date.now()
  }, 1000) as any
}

// 停止计时器
const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

// 获取任务列表
const fetchTasks = async () => {
  try {
    loading.value = true
    const response: any = await taskApi.getTasks({
      page: 1,
      page_size: 20
    })
    
    if (response && response.items) {
      tasks.value = response.items
    } else if (Array.isArray(response)) {
      tasks.value = response
    }
  } catch (error: any) {
    console.error('获取任务失败:', error)
    ElMessage.error('获取任务失败')
  } finally {
    loading.value = false
  }
}

// 处理任务点击
const handleTaskClick = (task: Task) => {
  // 如果正在拖拽，不处理点击
  if (isDragging.value) {
    return
  }
  
  // 切换任务
  switchToTask(task)
}

// 处理任务双击（进入简洁模式）
const handleTaskDoubleClick = (task: Task) => {
  // 如果正在拖拽，不处理双击
  if (isDragging.value) {
    return
  }
  
  // 切换任务
  switchToTask(task)
  
  // 如果不在简洁模式，则进入简洁模式
  if (!isCompactMode.value) {
    isCompactMode.value = true
  }
}

// 停止当前任务
const stopCurrentTask = async () => {
  if (isWorking.value) {
    await pauseWork()
  }
  
  // 清空当前任务
  currentTask.value = null
  workStartTime.value = null
  currentSessionDuration.value = 0
  
  ElMessage.success('已停止当前任务')
}

// 开始工作
const startWork = async () => {
  try {
    // 设置工作开始时间为当前时间
    workStartTime.value = new Date()
    isWorking.value = true
    
    // 启动计时器
    startTimer()
    
    // 更新任务状态为进行中
    if (currentTask.value) {
      await taskApi.updateTask(currentTask.value.id, {
        status: 'in_progress'
      })
      
      // 记录开始工作日志
      await workLogApi.createWorkLog({
        task_id: currentTask.value.id,
        team_id: currentTask.value.team_id,
        project_id: currentTask.value.project_id,
        work_type: 'feature', // 使用正确的枚举值
        content: `继续执行任务: ${currentTask.value.title}`,
        start_time: workStartTime.value.toISOString(),
        end_time: workStartTime.value.toISOString() // 开始时的结束时间等于开始时间
      })
      
      // 刷新任务列表以更新状态
      await fetchTasks()
      
      // 重新获取当前任务的最新数据，确保actual_hours是最新的
      const updatedTask = tasks.value.find(task => task.id === currentTask.value?.id)
      if (updatedTask) {
        currentTask.value = updatedTask
        console.log(`开始工作，任务数据已更新，累计工作时间: ${updatedTask.actual_hours?.toFixed(2)}小时`)
      }
    }
  } catch (error: any) {
    console.error('开始工作失败:', error)
    ElMessage.error('开始工作失败')
  }
}

// 暂停工作
const pauseWork = async () => {
  try {
    if (!workStartTime.value || !currentTask.value) {
    isWorking.value = false
    stopTimer()
      return
    }
    
      const endTime = new Date()
    const sessionDuration = endTime.getTime() - workStartTime.value.getTime()
    const sessionHours = sessionDuration / 3600000 // 毫秒转小时
    
    // 计算新的累计工作时间
    const currentActualHours = currentTask.value.actual_hours || 0
    const newActualHours = currentActualHours + sessionHours
    
    // 更新任务的累计工作时间
    await taskApi.updateTask(currentTask.value.id, {
      actual_hours: newActualHours
    })
    
    // 记录工作日志
        await workLogApi.createWorkLog({
      task_id: currentTask.value.id,
          team_id: currentTask.value.team_id,
          project_id: currentTask.value.project_id,
      work_type: 'feature', // 使用正确的枚举值
      content: `任务工作: ${currentTask.value.title} - 继续执行任务`,
      start_time: workStartTime.value.toISOString(),
      end_time: endTime.toISOString()
    })
    
    isWorking.value = false
    stopTimer()
    
    // 刷新任务列表以更新actual_hours
    await fetchTasks()
    
    // 重新获取当前任务的最新数据，确保actual_hours是最新的
    if (currentTask.value) {
      const updatedTask = tasks.value.find(task => task.id === currentTask.value?.id)
      if (updatedTask) {
        currentTask.value = updatedTask
        console.log(`任务数据已更新，新的累计工作时间: ${updatedTask.actual_hours?.toFixed(2)}小时`)
      }
    }
    
    console.log(`工作暂停，本次工作时长: ${formatTime(sessionDuration)}, 累计工作时长: ${newActualHours.toFixed(2)}小时`)
  } catch (error: any) {
    console.error('暂停工作失败:', error)
    ElMessage.error('暂停工作失败')
    // 即使失败也要停止计时器
    isWorking.value = false
    stopTimer()
  }
}

// 开始拖拽
const startDrag = (event: MouseEvent) => {
  // 只防止在真正的交互元素上开始拖拽
  const target = event.target as HTMLElement
  
  // 检查是否点击在按钮、输入框、链接等交互元素上
  if (target.closest('button') || 
      target.closest('input') || 
      target.closest('textarea') || 
      target.closest('select') || 
      target.closest('a') || 
      target.closest('.task-item-actions') ||
      target.closest('.task-actions') ||
      target.closest('.quick-actions')) {
    return
  }
  
  if (window.electronAPI) {
    isDragging.value = true
    dragStartPos.value = { x: event.clientX, y: event.clientY }
    
    // 获取窗口当前位置作为起始位置
    window.electronAPI.getWindowPosition().then((pos: any) => {
      windowStartPos.value = { x: pos.x, y: pos.y }
    })
    
    // 添加document事件监听器
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', stopDrag)
    
    // 阻止事件冒泡，防止触发其他点击事件
    event.preventDefault()
    event.stopPropagation()
  }
}

// 停止拖拽
const stopDrag = (event?: MouseEvent) => {
  if (event) {
    // 如果是鼠标释放事件，阻止事件冒泡
    event.preventDefault()
    event.stopPropagation()
  }
  
  isDragging.value = false
  
  // 移除document事件监听器
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopDrag)
}

// 处理鼠标移动事件 - 简化版本
const handleMouseMove = (event: MouseEvent) => {
  if (isDragging.value && window.electronAPI && dragStartPos.value && windowStartPos.value) {
    // 计算鼠标移动的距离
    const dx = event.clientX - dragStartPos.value.x
    const dy = event.clientY - dragStartPos.value.y
    
    // 计算窗口的新位置，确保是数字类型
    const newX = Math.round(windowStartPos.value.x + dx)
    const newY = Math.round(windowStartPos.value.y + dy)
    
    // 移动窗口到新位置
    window.electronAPI.moveWindowTo(newX, newY)
    
    // 阻止事件冒泡
    event.preventDefault()
    event.stopPropagation()
  }
}

// 动态调整窗口大小
const adjustWindowSize = () => {
  // 如果正在拖拽，不调整窗口大小
  if (isDragging.value) {
    return
  }
  
  // 检查是否在Electron环境中
  if (window.electronAPI) {
    // 简洁模式使用动态高度
    if (isCompactMode.value) {
      const compactWidth = 320
      // 根据是否显示快捷键提示来调整高度
      const compactHeight = showShortcutsHint.value ? 120 : 80 // 显示提示时稍高一些
      
      console.log(`简洁模式窗口大小: ${compactWidth}x${compactHeight}, 显示提示: ${showShortcutsHint.value}`)
      
      window.electronAPI.resizeWindow(Number(compactWidth), Number(compactHeight)).then(() => {
        console.log('简洁模式窗口大小调整成功')
      }).catch((error: any) => {
        console.error('简洁模式窗口大小调整失败:', error)
      })
      return
    }
    
    // 普通模式的计算逻辑
    const taskCount = tasks.value.length
    const baseHeight = 400 // 减少基础高度
    const taskItemHeight = 70 // 每个任务项的高度（包含间距）
    const maxHeight = 700 // 减少最大高度
    const minHeight = 350 // 减少最小高度
    
    // 计算理想高度
    let idealHeight = baseHeight + (taskCount * taskItemHeight)
    
    // 限制在最小和最大高度之间
    idealHeight = Math.max(minHeight, Math.min(maxHeight, idealHeight))
    
    console.log(`调整窗口大小: 任务数量=${taskCount}, 计算高度=${idealHeight}, 基础高度=${baseHeight}, 任务项高度=${taskItemHeight}`)
    
    // 调用Electron API调整窗口大小
    window.electronAPI.resizeWindow(Number(400), Number(idealHeight)).then(() => {
      console.log('窗口大小调整成功')
    }).catch((error: any) => {
      console.error('窗口大小调整失败:', error)
    })
  } else {
    console.log('不在Electron环境中，跳过窗口大小调整')
  }
}

// 获取任务累计工作时间（从actual_hours字段）
const getTaskTotalDuration = (task: Task) => {
  return (task.actual_hours || 0) * 3600000 // 小时转毫秒
}

// 切换任务
const switchToTask = async (task: Task) => {
  if (isWorking.value) {
    // 如果正在工作，先停止当前任务
    await pauseWork()
  }
  
  // 重新获取任务的最新数据
  await fetchTasks()
  const updatedTask = tasks.value.find(t => t.id === task.id)
  if (updatedTask) {
    currentTask.value = updatedTask
    console.log(`切换到任务: ${updatedTask.title}, 累计工作时间: ${updatedTask.actual_hours?.toFixed(2)}小时`)
  } else {
    currentTask.value = task
  }
  
  isSwitchingTask.value = true
  
  // 重置当前会话时间
  currentSessionDuration.value = 0
  
  setTimeout(() => {
    isSwitchingTask.value = false
  }, 300)
}

// 刷新任务列表
const refreshTasks = async () => {
  // 如果正在拖拽，不刷新任务
  if (isDragging.value) {
    return
  }
  
  await fetchTasks()
  
  // 强制调整窗口大小，但延迟执行避免与拖拽冲突
  setTimeout(() => {
    if (!isDragging.value) {
      adjustWindowSize()
    }
  }, 300)
}

// Electron窗口控制
const minimizeWindow = () => {
  // 这里需要调用Electron的API
  console.log('最小化窗口')
}

const closeWindow = () => {
  // 这里需要调用Electron的API
  console.log('关闭窗口')
}

// 打开其他窗口
const showTaskManagement = () => {
  // 这里可以跳转到管理视图页面或打开新窗口
  window.open('/tasks', '_blank')
}

const openCalendar = () => {
  // 移除提示信息
  // ElMessage.info('打开日历视图')
}

const openMainWindow = () => {
  // 移除提示信息
  // ElMessage.info('打开主窗口')
}

// 监听工作状态变化，保存到本地存储
watch([isWorking, workStartTime, currentTask], () => {
  const workState = {
    isWorking: isWorking.value,
    workStartTime: workStartTime.value?.toISOString(),
    taskId: currentTask.value?.id
  }
  localStorage.setItem('electronFloatingTaskBarWorkState', JSON.stringify(workState))
}, { deep: true })

// 监听工作状态变化，控制计时器
watch(isWorking, (newValue) => {
  if (newValue) {
    startTimer()
  } else {
    stopTimer()
  }
})

// 监听任务列表变化
watch(tasks, () => {
  nextTick(() => {
    setTimeout(() => {
      adjustWindowSize()
    }, 100)
  })
}, { deep: true })

// 监听快捷键提示状态变化
watch(showShortcutsHint, () => {
  if (isCompactMode.value) {
    nextTick(() => {
      adjustWindowSize()
    })
  }
})

// 组件挂载时获取任务列表
onMounted(async () => {
  await fetchTasks()
  
  // 从本地存储恢复工作状态
  const savedWorkState = localStorage.getItem('electronFloatingTaskBarWorkState')
  if (savedWorkState) {
    try {
      const workState = JSON.parse(savedWorkState)
      if (workState.isWorking && workState.workStartTime && workState.taskId) {
        // 找到对应的任务
        const task = tasks.value.find(t => t.id === workState.taskId)
        if (task) {
          currentTask.value = task
          workStartTime.value = new Date(workState.workStartTime)
          isWorking.value = true
          startTimer()
          console.log('恢复工作状态:', task.title, '累计时间:', formatTime((task.actual_hours || 0) * 3600000))
        }
      }
    } catch (error) {
      console.error('恢复工作状态失败:', error)
    }
  }
  
  // 初始调整窗口大小，增加延迟确保DOM完全加载
  setTimeout(() => {
    adjustWindowSize()
  }, 500)
  document.addEventListener('keydown', handleKeyDown)
  
  // 确保QuickCreateTask组件获得焦点，以便能够接收键盘事件
  setTimeout(() => {
    const quickCreateWrapper = document.querySelector('.quick-create-wrapper') as HTMLElement
    if (quickCreateWrapper) {
      quickCreateWrapper.focus()
    }
  }, 1000)
  
  // 添加点击事件监听器，确保点击时重新获得焦点
  document.addEventListener('click', handleDocumentClick)
})

// 组件卸载时保存工作状态
onUnmounted(() => {
  if (isWorking.value) {
    pauseWork()
  }
  stopTimer()
  
  // 清理拖拽事件监听器
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('click', handleDocumentClick)
})

// 处理文档点击事件，确保 QuickCreateTask 组件获得焦点
const handleDocumentClick = () => {
  // 延迟设置焦点，确保其他点击事件处理完成
  setTimeout(() => {
    const quickCreateWrapper = document.querySelector('.quick-create-wrapper') as HTMLElement
    if (quickCreateWrapper) {
      quickCreateWrapper.focus()
    }
  }, 100)
}

// 处理QuickCreateTask组件事件
const handleTaskCreated = async (task: any) => {
  console.log('任务创建成功:', task)
  // 刷新任务列表
  await refreshTasks()
}

const handleTaskCreateError = (error: any) => {
  console.error('任务创建失败:', error)
}

// 鼠标事件处理
const handleMouseEnter = () => {
  isExpanded.value = true
}

const handleMouseLeave = () => {
  isExpanded.value = false
}

// 切换最小化状态
const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

// 切换工作状态
const toggleWorkStatus = async () => {
  if (isWorking.value) {
    await pauseWork()
  } else {
    await startWork()
  }
}

// 获取优先级图标
const getPriorityIcon = (priority?: string) => {
  const priorityIcons: { [key: string]: any } = {
    'low': Star,
    'medium': StarFilled,
    'high': Warning,
    'urgent': CircleCloseFilled
  }
  return priorityIcons[priority || 'low'] || Star
}

// 获取状态图标
const getStatusIcon = (status?: string) => {
  const statusIcons: { [key: string]: any } = {
    'pending': Clock,
    'assigned': User,
    'in_progress': VideoPlay,
    'review': InfoFilled,
    'completed': CircleCheck,
    'cancelled': CircleCloseFilled
  }
  return statusIcons[status || 'pending'] || Clock
}

// 切换简洁模式
const toggleCompactMode = () => {
  isCompactMode.value = !isCompactMode.value
  
  console.log('切换简洁模式:', isCompactMode.value)
  
  // 只在进入简洁模式时显示提示
  if (isCompactMode.value) {
    showShortcutsHint.value = true
    setTimeout(() => {
      showShortcutsHint.value = false
      // 快捷键提示消失后调整窗口大小，使其更加紧凑
      nextTick(() => {
        adjustWindowSize()
      })
    }, 2000)
  }
  
  // 调整窗口大小
  nextTick(() => {
    adjustWindowSize()
  })
}

// 处理键盘事件
const handleKeyDown = (event: KeyboardEvent) => {
  // 如果当前在输入框中，不处理任何快捷键
  const target = event.target as HTMLElement
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.contentEditable === 'true') {
    return
  }
  
  // 只处理 Ctrl+Enter，不拦截其他按键
  if (event.ctrlKey && event.code === 'Enter') {
    event.preventDefault() // 防止默认行为
    
    // Ctrl+Enter 切换简洁模式
    toggleCompactMode()
  }
  
  // 处理Enter键 - 启动/停止工作
  if (event.code === 'Enter') {
    event.preventDefault() // 防止默认行为
    
    // 如果有当前任务，则切换工作状态
    if (currentTask.value) {
      toggleWorkStatus()
    }
  }
  
  // 在简洁模式下处理左右箭头键切换任务
  if (isCompactMode.value && tasks.value.length > 1) {
    if (event.code === 'ArrowLeft') {
      event.preventDefault()
      switchToPreviousTask()
    } else if (event.code === 'ArrowRight') {
      event.preventDefault()
      switchToNextTask()
    }
  }
  
  // 对于空格键，不阻止默认行为，让 QuickCreateTask 组件处理双击空格
  if (event.code === 'Space') {
    // 不调用 preventDefault()，让事件继续传播
    return
  }
  
  // 不处理其他按键，让其他组件的键盘事件能够正常工作
}

// 显示短时间弹窗提示
const showCompactTipToast = (text: string) => {
  compactTipText.value = text
  showCompactTip.value = true
  
  // 2秒后自动隐藏
  setTimeout(() => {
    showCompactTip.value = false
  }, 2000)
}

// 完成任务
const completeCurrentTask = async () => {
  if (!currentTask.value) {
    ElMessage.warning('没有当前任务')
    return
  }
  
  try {
    // 如果正在工作，先停止工作
    if (isWorking.value) {
      await pauseWork()
    }
    
    // 更新任务状态为已完成
    await taskApi.updateTask(currentTask.value.id, {
      status: 'completed'
    })
    
    // 显示成功提示
    ElMessage.success('任务已完成')
    
    // 刷新任务列表
    await fetchTasks()
    
    // 清除当前任务
    currentTask.value = null
    
    // 显示短时间弹窗提示
    showCompactTipToast('任务已完成')
    
  } catch (error: any) {
    console.error('完成任务失败:', error)
    ElMessage.error('完成任务失败')
  }
}

// 获取当前任务索引
const getCurrentTaskIndex = () => {
  return tasks.value.findIndex(task => task.id === currentTask.value?.id)
}

// 切换到上一个任务
const switchToPreviousTask = () => {
  const index = getCurrentTaskIndex()
  if (index > 0) {
    switchToTask(tasks.value[index - 1])
  }
}

// 切换到下一个任务
const switchToNextTask = () => {
  const index = getCurrentTaskIndex()
  if (index < tasks.value.length - 1) {
    switchToTask(tasks.value[index + 1])
  }
}

// 测试快速创建功能
const testQuickCreate = () => {
  console.log('测试快速创建功能')
  // 通过 ref 调用 QuickCreateTask 组件的方法
  const quickCreateWrapper = document.querySelector('.quick-create-wrapper') as any
  if (quickCreateWrapper && quickCreateWrapper.__vueParentComponent) {
    const quickCreateComponent = quickCreateWrapper.__vueParentComponent.exposed
    if (quickCreateComponent && quickCreateComponent.showQuickCreateDialog) {
      quickCreateComponent.showQuickCreateDialog()
      console.log('成功调用快速创建对话框')
    } else {
      console.log('无法找到快速创建组件的方法')
    }
  } else {
    console.log('无法找到快速创建组件')
  }
}
</script>

<style scoped>
.floating-task-bar {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
  cursor: default;
  user-select: none;
  pointer-events: auto;
}

.floating-task-bar:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.floating-task-bar.working {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  box-shadow: 0 8px 32px rgba(103, 194, 58, 0.2);
}

.floating-task-bar.working:hover {
  box-shadow: 0 12px 40px rgba(103, 194, 58, 0.3);
}

/* 拖拽时的样式 */
.floating-task-bar.dragging {
  opacity: 0.8;
  transform: scale(0.98);
  transition: none;
}

/* 防止按钮区域触发拖拽 */
.floating-task-bar button,
.floating-task-bar .task-actions,
.floating-task-bar .quick-actions,
.floating-task-bar .task-item-actions {
  cursor: pointer;
  user-select: none;
  -webkit-app-region: no-drag;
}

/* 任务项可以拖拽，但点击时不会触发拖拽 */
.floating-task-bar .task-item {
  cursor: pointer;
  /* 移除 no-drag，允许拖拽 */
}

/* 确保内容区域可以拖拽 */
.task-bar-content {
  pointer-events: auto;
  /* 移除 no-drag，允许拖拽 */
}

/* 拖拽手柄区域 */
.drag-handle {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
  cursor: move;
  z-index: 10;
  -webkit-app-region: drag;
}

.task-bar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
  padding: 0;
  margin: 0;
}

.current-task-section {
  padding: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  position: relative;
  flex-shrink: 0;
  min-height: 200px;
  color: white;
}

.current-task-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.1)"/><circle cx="10" cy="60" r="0.5" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="40" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

/* 任务详情区域样式 */
.task-detail-section {
  padding: 20px 40px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  position: relative;
}

.task-detail-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.3) 50%, transparent 100%);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.detail-icon {
  font-size: 16px;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 6px;
  border-radius: 6px;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.detail-content {
  display: block;
}

.detail-item {
  display: block;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.detail-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

.description {
  color: #606266;
  font-weight: 500;
  line-height: 1.6;
  font-size: 14px;
  display: block;
  word-wrap: break-word;
}

.priority-badge, .status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.priority-badge.priority-high {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  color: white;
}

.priority-badge.priority-medium {
  background: linear-gradient(135deg, #e6a23c 0%, #f0c78a 100%);
  color: white;
}

.priority-badge.priority-low {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.status-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.task-info {
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.task-title {
  font-size: 32px;
  font-weight: 800;
  color: white;
  margin-bottom: 25px;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 15px;
}

.task-icon {
  font-size: 28px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.2);
  padding: 10px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 25px;
}

.timer-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.timer-icon {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.9);
}

.timer {
  font-size: 48px;
  font-weight: 900;
  color: #ffffff;
  font-family: 'Digital-7', 'DS-Digital', 'Consolas', 'Monaco', monospace;
  text-shadow: 
    0 0 10px #ffffff,
    0 0 20px #ffffff,
    0 0 30px #ffffff;
  padding: 8px 16px;
  letter-spacing: 3px;
  animation: timerGlow 2s ease-in-out infinite alternate;
}

@keyframes timerGlow {
  0% {
    text-shadow: 
      0 0 10px #ffffff,
      0 0 20px #ffffff,
      0 0 30px #ffffff;
  }
  100% {
    text-shadow: 
      0 0 15px #ffffff,
      0 0 25px #ffffff,
      0 0 35px #ffffff;
  }
}

.status {
  font-size: 15px;
  padding: 10px 20px;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 700;
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.status.working {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
  border-color: rgba(103, 194, 58, 0.5);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.3);
}

.status-icon {
  font-size: 16px;
}

.task-actions {
  display: flex;
  gap: 15px;
  position: relative;
  z-index: 1;
}

.work-btn, .stop-btn {
  padding: 12px 24px !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
  transition: all 0.3s ease !important;
  font-size: 14px !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
}

.work-btn:hover, .stop-btn:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
}

.work-btn {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%) !important;
  color: white !important;
}

.stop-btn {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%) !important;
  color: white !important;
}

.task-list-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 50%, #f0f4ff 100%);
  position: relative;
}

.task-list-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(103, 194, 58, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.section-header {
  padding: 20px 40px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 249, 255, 0.9) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 2;
}

.section-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.05) 50%, transparent 100%);
  pointer-events: none;
}

.section-title-container {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.section-icon {
  font-size: 18px;
  color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.refresh-btn {
  color: #667eea !important;
  padding: 8px !important;
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(102, 126, 234, 0.1) !important;
}

.refresh-btn:hover {
  background: rgba(102, 126, 234, 0.1) !important;
  transform: rotate(180deg) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
}

.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.task-list::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(45deg, transparent 49%, rgba(102, 126, 234, 0.02) 50%, transparent 51%),
    linear-gradient(-45deg, transparent 49%, rgba(118, 75, 162, 0.02) 50%, transparent 51%);
  background-size: 20px 20px;
  pointer-events: none;
}

.task-item {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 255, 0.95) 100%);
  border: 1px solid rgba(102, 126, 234, 0.1);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.task-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.task-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.task-item:hover::before {
  opacity: 1;
}

.task-item:hover::after {
  opacity: 1;
}

.task-item:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 12px 30px rgba(0, 0, 0, 0.12),
    0 4px 12px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.task-item.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.2),
    0 4px 12px rgba(102, 126, 234, 0.1);
}

.task-item.active::after {
  opacity: 1;
}

.task-item.working {
  border-color: #67c23a;
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(133, 206, 97, 0.1) 100%);
  box-shadow: 
    0 8px 25px rgba(103, 194, 58, 0.2),
    0 4px 12px rgba(103, 194, 58, 0.1);
}

.task-item.working::after {
  background: linear-gradient(90deg, #67c23a 0%, #85ce61 100%);
  opacity: 1;
}

.task-item-content {
  position: relative;
  z-index: 1;
}

.task-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.task-item-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  margin-right: 12px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.task-item-icon {
  font-size: 16px;
  color: #667eea;
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 1px 2px rgba(102, 126, 234, 0.3));
}

.task-item-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.task-item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
}

.task-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-due-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #e6a23c;
  font-weight: 600;
  padding: 4px 8px;
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.1) 0%, rgba(230, 162, 60, 0.05) 100%);
  border-radius: 6px;
  border: 1px solid rgba(230, 162, 60, 0.2);
  backdrop-filter: blur(5px);
}

.due-icon {
  font-size: 12px;
  filter: drop-shadow(0 1px 1px rgba(230, 162, 60, 0.3));
}

.task-item-actions {
  display: flex;
  gap: 8px;
}

.task-priority, .task-status {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.task-priority.priority-high {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.15) 0%, rgba(245, 108, 108, 0.05) 100%);
  color: #f56c6c;
  border: 1px solid rgba(245, 108, 108, 0.2);
}

.task-priority.priority-high:hover {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.2) 0%, rgba(245, 108, 108, 0.1) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(245, 108, 108, 0.2);
}

.task-priority.priority-medium {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.15) 0%, rgba(230, 162, 60, 0.05) 100%);
  color: #e6a23c;
  border: 1px solid rgba(230, 162, 60, 0.2);
}

.task-priority.priority-medium:hover {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2) 0%, rgba(230, 162, 60, 0.1) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(230, 162, 60, 0.2);
}

.task-priority.priority-low {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15) 0%, rgba(103, 194, 58, 0.05) 100%);
  color: #67c23a;
  border: 1px solid rgba(103, 194, 58, 0.2);
}

.task-priority.priority-low:hover {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2) 0%, rgba(103, 194, 58, 0.1) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(103, 194, 58, 0.2);
}

.task-status {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(102, 126, 234, 0.05) 100%);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.task-status:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(102, 126, 234, 0.1) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.priority-icon, .status-icon {
  font-size: 12px;
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.1));
}

.switch-btn {
  color: #667eea !important;
  padding: 6px 12px !important;
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(102, 126, 234, 0.1) !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
}

.switch-btn:hover {
  background: rgba(102, 126, 234, 0.1) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 20px;
}

.quick-actions {
  padding: 15px 20px;
  background: white;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.manage-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 10px 20px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
  font-size: 13px !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}

.manage-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

.minimized-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.minimized-task-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.minimized-icon {
  font-size: 16px;
}

.minimized-task-title {
  font-weight: 600;
  font-size: 14px;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-task {
  font-size: 14px;
  opacity: 0.8;
}

.minimized-timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 16px;
  font-family: 'Digital-7', 'DS-Digital', 'Consolas', 'Monaco', monospace;
  color: #ffffff;
  text-shadow: 
    0 0 6px #ffffff,
    0 0 12px #ffffff;
  padding: 3px 6px;
  animation: minimizedTimerGlow 2s ease-in-out infinite alternate;
}

@keyframes minimizedTimerGlow {
  0% {
    text-shadow: 
      0 0 6px #ffffff,
      0 0 12px #ffffff;
  }
  100% {
    text-shadow: 
      0 0 8px #ffffff,
      0 0 16px #ffffff,
      0 0 24px #ffffff;
  }
}

.timer-icon {
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .floating-task-bar {
    width: 100%;
    height: 100%;
  }
  
  .current-task-section {
    padding: 20px;
    min-height: 150px;
  }
  
  .task-title {
    font-size: 20px;
  }
  
  .timer {
    font-size: 24px;
  }
  
  .section-header {
    padding: 15px 20px;
  }
  
  .task-list {
    padding: 15px 20px 15px;
  }
  
  .task-item {
    padding: 15px;
  }
  
  .quick-actions {
    padding: 15px 20px;
  }
  
  .global-admin-button {
    top: 10px;
    right: 10px;
  }
  
  .admin-btn {
    padding: 8px 16px !important;
    font-size: 12px !important;
  }
}

@media (max-width: 500px) {
  .floating-task-bar {
    width: 100%;
    height: 100%;
  }
  
  .current-task-section {
    padding: 15px;
    min-height: 120px;
  }
  
  .task-title {
    font-size: 18px;
  }
  
  .timer {
    font-size: 20px;
  }
  
  .section-header {
    padding: 12px 15px;
  }
  
  .task-list {
    padding: 15px 15px 15px;
  }
  
  .task-item {
    padding: 12px;
    margin-bottom: 8px;
  }
  
  .task-item-title {
    font-size: 13px;
  }
  
  .task-item-meta {
    gap: 6px;
  }
  
  .task-priority, .task-status {
    font-size: 10px;
    padding: 2px 5px;
  }
  
  .quick-actions {
    padding: 12px 15px;
  }
  
  .manage-btn {
    padding: 8px 16px !important;
    font-size: 12px !important;
  }
  
  .global-admin-button {
    top: 8px;
    right: 8px;
  }
  
  .admin-btn {
    padding: 6px 12px !important;
    font-size: 11px !important;
  }
}

/* 简洁模式样式 - 现代化扁平设计 */
.floating-task-bar.compact {
  width: 320px;
  height: auto;
  min-height: 80px;
  background: #1a1a1a;
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.floating-task-bar.compact:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

.compact-mode {
  padding: 10px;
  color: white;
  display: flex;
  align-items: center;
  min-height: 80px;
}

.compact-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
    width: 100%;
  gap: 8px;
}

.compact-task-info {
  flex: 1;
  min-width: 0;
  text-align: left;
  transition: all 0.3s ease;
}

.compact-task-info.switching {
  animation: taskSwitch 0.3s ease;
}

@keyframes taskSwitch {
  0% {
    opacity: 0.7;
    transform: translateX(-10px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

.compact-task-title {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  margin-bottom: 6px;
  transition: all 0.3s ease;
}

.compact-icon {
  font-size: 16px;
  color: #64b5f6;
  opacity: 0.9;
}

.task-text {
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
  line-height: 1.4;
  letter-spacing: 0.2px;
  transition: all 0.3s ease;
}

.compact-timer {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 6px;
  transition: all 0.3s ease;
}

.timer-icon {
  font-size: 14px;
  color: #81c784;
}

.time-text {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  font-family: 'Digital-7', 'DS-Digital', 'Consolas', 'Monaco', monospace;
  letter-spacing: 2px;
  text-shadow: 
    0 0 8px #ffffff,
    0 0 16px #ffffff;
  padding: 4px 8px;
  animation: compactTimerGlow 2s ease-in-out infinite alternate;
}

@keyframes compactTimerGlow {
  0% {
    text-shadow: 
      0 0 8px #ffffff,
      0 0 16px #ffffff;
  }
  100% {
    text-shadow: 
      0 0 12px #ffffff,
      0 0 20px #ffffff;
  }
}

.compact-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.compact-play-btn {
  width: 32px !important;
  height: 32px !important;
  background: #4caf50 !important;
  border: none !important;
  border-radius: 6px !important;
  color: white !important;
  font-size: 12px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3) !important;
}

.compact-play-btn:hover {
  background: #66bb6a !important;
  transform: scale(1.05) !important;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4) !important;
}

.compact-play-btn.playing {
  background: #f44336 !important;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3) !important;
}

.compact-play-btn.playing:hover {
  background: #ef5350 !important;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4) !important;
}

.compact-stop-btn {
  width: 24px !important;
  height: 24px !important;
  background: #ff9800 !important;
  border: none !important;
  border-radius: 4px !important;
  color: white !important;
  font-size: 10px !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.compact-stop-btn:hover {
  background: #ffb74d !important;
  transform: scale(1.05) !important;
}

.compact-complete-btn {
  width: 24px !important;
  height: 24px !important;
  background: #2196f3 !important;
  border: none !important;
  border-radius: 4px !important;
  color: white !important;
  font-size: 10px !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.compact-complete-btn:hover {
  background: #42a5f5 !important;
  transform: scale(1.05) !important;
}

.compact-switch-btn {
  width: 20px !important;
  height: 20px !important;
  background: #2a2a2a !important;
  border: 1px solid #444 !important;
  color: #888 !important;
  transition: all 0.3s ease !important;
}

.compact-switch-btn:hover:not(:disabled) {
  background: #3a3a3a !important;
  color: #64b5f6 !important;
  border-color: #64b5f6 !important;
}

.compact-switch-btn:disabled {
  opacity: 0.3 !important;
  cursor: not-allowed !important;
}

.compact-shortcuts {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 4px;
  opacity: 0.7;
  transition: opacity 0.5s ease;
  animation: fadeInOut 2s ease-in-out;
}

@keyframes fadeInOut {
  0% {
    opacity: 0;
  }
  20% {
    opacity: 0.7;
  }
  80% {
    opacity: 0.7;
  }
  100% {
    opacity: 0;
  }
}

.shortcut-hint {
  font-size: 10px;
  color: #aaa;
  white-space: nowrap;
}

.compact-task-indicator {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 2px;
}

.indicator-text {
  font-size: 11px;
  color: #888;
  font-weight: 500;
}

.task-list-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 10% 10%, rgba(102, 126, 234, 0.03) 0%, transparent 30%),
    radial-gradient(circle at 90% 90%, rgba(118, 75, 162, 0.03) 0%, transparent 30%),
    radial-gradient(circle at 50% 50%, rgba(103, 194, 58, 0.02) 0%, transparent 40%);
  pointer-events: none;
  animation: backgroundFloat 20s ease-in-out infinite;
}

@keyframes backgroundFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-10px) rotate(1deg);
  }
  66% {
    transform: translateY(5px) rotate(-1deg);
  }
}

.task-item {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 255, 0.95) 100%);
  border: 1px solid rgba(102, 126, 234, 0.1);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.task-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.task-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.task-item:hover::before {
  opacity: 1;
}

.task-item:hover::after {
  opacity: 1;
}

.task-item:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 12px 30px rgba(0, 0, 0, 0.12),
    0 4px 12px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.task-item.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.2),
    0 4px 12px rgba(102, 126, 234, 0.1);
}

.task-item.active::after {
  opacity: 1;
}

.task-item.working {
  border-color: #67c23a;
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(133, 206, 97, 0.1) 100%);
  box-shadow: 
    0 8px 25px rgba(103, 194, 58, 0.2),
    0 4px 12px rgba(103, 194, 58, 0.1);
}

.task-item.working::after {
  background: linear-gradient(90deg, #67c23a 0%, #85ce61 100%);
  opacity: 1;
}

/* 添加装饰性光点 */
.task-item .sparkle-dot {
  content: '';
  position: absolute;
  top: 10px;
  right: 10px;
  width: 6px;
  height: 6px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
  animation: sparkle 2s ease-in-out infinite;
  z-index: 2;
}

.task-item:hover .sparkle-dot {
  opacity: 1;
}

@keyframes sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.2) rotate(180deg);
    opacity: 1;
  }
}

/* 添加任务项内容的装饰边框 */
.task-item-content {
  position: relative;
  z-index: 1;
}

.task-item-content::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, transparent 30%, rgba(102, 126, 234, 0.1) 50%, transparent 70%);
  border-radius: 18px;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.task-item:hover .task-item-content::before {
  opacity: 1;
}
</style> 
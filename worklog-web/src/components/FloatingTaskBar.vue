<template>
  <div class="floating-task-bar" :class="{ collapsed: isCollapsed }">
    <!-- 当前任务显示 -->
    <div class="current-task" @click="toggleTaskList">
      <div class="task-info">
        <span class="task-title">{{ currentTask?.title || '未选择任务' }}</span>
        <span class="timer" v-if="isWorking">{{ formatDuration(currentDuration) }}</span>
      </div>
      <div class="task-status">
        <el-tag :type="getStatusType(currentTask?.status)" size="small">
          {{ getStatusText(currentTask?.status) }}
        </el-tag>
      </div>
    </div>
    
    <!-- 快速操作按钮 -->
    <div class="quick-actions">
      <el-button size="small" @click="toggleCollapse">
        <el-icon>
          <ArrowUp v-if="isCollapsed" />
          <ArrowDown v-else />
        </el-icon>
      </el-button>
    </div>
    
    <!-- 任务列表（展开时显示） -->
    <div class="task-list" v-if="!isCollapsed">
      <div class="task-list-header">
        <span>我的任务</span>
        <el-button size="small" @click="refreshTasks">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
      
      <div class="task-items">
        <!-- 所有任务，按优先级排序 -->
        <transition-group name="task-slide" tag="div">
          <div 
            v-for="task in sortedTasks" 
            :key="task.id"
            class="task-item"
            :class="{ 
              active: currentTask?.id === task.id,
              working: task.status === 'in_progress' && isWorking && currentTask?.id === task.id
            }"
            @click="switchToTask(task.id)"
            @dblclick="toggleTaskWork(task.id)"
          >
            <div class="task-item-content">
              <div class="task-header">
                <span class="task-name">{{ task.title }}</span>
                <div class="working-indicator" v-if="task.status === 'in_progress' && isWorking && currentTask?.id === task.id">
                  <el-icon class="pulse"><VideoPlay /></el-icon>
                  <span>执行中</span>
                </div>
              </div>
              <div class="task-meta">
                <el-tag :type="getStatusType(task.status)" size="small">
                  {{ getStatusText(task.status) }}
                </el-tag>
                <span class="task-priority" v-if="task.priority">
                  {{ getPriorityText(task.priority) }}
                </span>
              </div>
            </div>
          </div>
        </transition-group>
        
        <div v-if="tasks.length === 0" class="no-tasks">
          <el-empty description="暂无任务" :image-size="60">
            <el-button size="small" @click="openTaskManagement">
              创建任务
            </el-button>
          </el-empty>
        </div>
      </div>
      
      <div class="task-list-footer">
        <el-button size="small" @click="openTaskManagement">
          管理任务
        </el-button>
        <el-button size="small" @click="openCalendar">
          日历视图
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPause, VideoPlay, ArrowUp, ArrowDown, Refresh } from '@element-plus/icons-vue'
import { taskApi, type Task } from '@/api/task'
import { workLogApi } from '@/api/workLog'
import { useUserStore } from '@/stores/user'

// 定义组件事件
const emit = defineEmits<{
  'task-switched': [task: Task]
  'work-started': [task: Task]
  'work-paused': [task: Task, duration: number]
}>()

// 状态管理
const isCollapsed = ref(false)
const isWorking = ref(false)
const currentTask = ref<Task | null>(null)
const tasks = ref<Task[]>([])
const loading = ref(false)
const workStartTime = ref<Date | null>(null)
const timerInterval = ref<number | null>(null)
const currentTime = ref(Date.now())

// 计算当前工作时间
const currentDuration = computed(() => {
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

// 格式化时间
const formatDuration = (duration: number) => {
  const hours = Math.floor(duration / (1000 * 60 * 60))
  const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((duration % (1000 * 60)) / 1000)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
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

// 切换任务列表显示
const toggleTaskList = () => {
  isCollapsed.value = !isCollapsed.value
}

// 切换折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// 切换任务工作状态（双击触发）
const toggleTaskWork = async (taskId: number) => {
  const task = tasks.value.find(t => t.id === taskId)
  if (!task) return
  
  // 如果任务正在进行中，则暂停
  if (task.status === 'in_progress' && isWorking.value && currentTask.value?.id === task.id) {
    await pauseWork()
  } else {
    // 如果任务未开始，则开始工作
    await switchToTask(taskId)
    await startWork()
  }
}

// 切换任务
const switchToTask = async (taskId: number) => {
  try {
    // 如果当前正在工作，先暂停
    if (isWorking.value) {
      await pauseWork()
    }
    
    // 设置新任务
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      currentTask.value = task
      // 发射任务切换事件
      emit('task-switched', task)
      ElMessage.success(`已切换到: ${task.title}`)
    }
  } catch (error: any) {
    console.error('切换任务失败:', error)
    ElMessage.error('切换任务失败')
  }
}

// 开始工作
const startWork = async () => {
  try {
    workStartTime.value = new Date()
    isWorking.value = true
    
    // 启动计时器
    startTimer()
    
    // 更新任务状态为进行中
    if (currentTask.value) {
      await taskApi.updateTask(currentTask.value.id, {
        status: 'in_progress'
      })
      // 刷新任务列表以更新状态
      await fetchTasks()
      // 发射开始工作事件
      emit('work-started', currentTask.value)
    }
    
    ElMessage.success('开始工作')
  } catch (error: any) {
    console.error('开始工作失败:', error)
    ElMessage.error('开始工作失败')
  }
}

// 暂停工作
const pauseWork = async () => {
  try {
    isWorking.value = false
    
    // 停止计时器
    stopTimer()
    
    // 记录工作日志
    if (currentTask.value && workStartTime.value) {
      const endTime = new Date()
      const duration = endTime.getTime() - workStartTime.value.getTime()
      
      try {
        await workLogApi.createWorkLog({
          content: `为任务"${currentTask.value.title}"工作`,
          work_type: 'feature',
          start_time: workStartTime.value.toISOString(),
          end_time: endTime.toISOString(),
          team_id: currentTask.value.team_id,
          project_id: currentTask.value.project_id,
          task_id: currentTask.value.id
        })
        console.log('工作日志记录成功')
        // 发射暂停工作事件
        emit('work-paused', currentTask.value, duration)
      } catch (logError: any) {
        console.error('记录工作日志失败:', logError)
        ElMessage.warning('工作日志记录失败，但工作已暂停')
        // 即使日志记录失败，也发射暂停事件
        const duration = endTime.getTime() - workStartTime.value.getTime()
        emit('work-paused', currentTask.value, duration)
      }
    }
    
    workStartTime.value = null
    ElMessage.success('已暂停工作')
  } catch (error: any) {
    console.error('暂停工作失败:', error)
    ElMessage.error('暂停工作失败')
  }
}

// 刷新任务列表
const refreshTasks = async () => {
  await fetchTasks()
  ElMessage.success('任务列表已刷新')
}

// 打开任务管理
const openTaskManagement = () => {
  // 这里可以打开任务管理窗口或跳转到任务管理页面
  ElMessage.info('打开任务管理')
}

// 打开日历视图
const openCalendar = () => {
  // 这里可以打开日历视图窗口或跳转到日历页面
  ElMessage.info('打开日历视图')
}

// 监听工作状态变化，控制计时器
watch(isWorking, (newValue) => {
  if (newValue) {
    startTimer()
  } else {
    stopTimer()
  }
})

// 组件挂载时获取任务列表
onMounted(async () => {
  const userStore = useUserStore()
  // 只在用户已登录时才获取任务数据
  if (userStore.isLoggedIn) {
    await fetchTasks()

    // 从本地存储恢复工作状态
    const savedWorkState = localStorage.getItem('floatingTaskBarWorkState')
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
            console.log('恢复工作状态:', task.title)
          }
        }
      } catch (error) {
        console.error('恢复工作状态失败:', error)
      }
    }
  }
})

// 监听工作状态变化，保存到本地存储
watch([isWorking, workStartTime, currentTask], () => {
  const workState = {
    isWorking: isWorking.value,
    workStartTime: workStartTime.value?.toISOString(),
    taskId: currentTask.value?.id
  }
  localStorage.setItem('floatingTaskBarWorkState', JSON.stringify(workState))
}, { deep: true })

// 组件卸载时保存工作状态
onUnmounted(() => {
  if (isWorking.value) {
    pauseWork()
  }
  stopTimer()
})
</script>

<style scoped>
.floating-task-bar {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 320px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 9999;
  transition: all 0.3s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.floating-task-bar.collapsed {
  width: 280px;
}

.current-task {
  padding: 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.current-task:hover {
  background-color: #f5f7fa;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-weight: 600;
  color: #303133;
  display: block;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timer {
  font-size: 12px;
  color: #409EFF;
  font-weight: 500;
}

.quick-actions {
  padding: 8px 16px;
  display: flex;
  gap: 8px;
  justify-content: center;
  border-bottom: 1px solid #f0f0f0;
}

.task-list {
  max-height: 400px;
  overflow-y: auto;
}

.task-list-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
  font-weight: 500;
  color: #606266;
}

.task-items {
  max-height: 300px;
  overflow-y: auto;
}

.task-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.task-item:hover {
  background-color: #f5f7fa;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-item.active {
  background-color: #e1f3d8;
  border-left: 3px solid #67c23a;
}

.task-item.working {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-left: 3px solid #409EFF;
  margin-bottom: 8px;
  border-radius: 8px;
  margin: 8px 8px 8px 8px;
}

.task-item.working:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.task-item-content {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.task-name {
  font-weight: 500;
  color: #303133;
  display: block;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.task-item.working .task-name {
  color: white;
}

.working-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 12px;
}

.working-indicator .pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.task-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.task-status {
  font-size: 12px;
  color: #909399;
}

.task-item.working .task-status {
  color: rgba(255, 255, 255, 0.8);
}

.task-priority {
  font-size: 11px;
  color: #909399;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
}

.task-item.working .task-priority {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.2);
}

.no-tasks {
  padding: 20px;
  text-align: center;
}

.task-list-footer {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* 滑动动画 */
.task-slide-enter-active,
.task-slide-leave-active {
  transition: all 0.5s ease;
}

.task-slide-enter-from {
  opacity: 0;
  transform: translateY(-30px);
}

.task-slide-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.task-slide-move {
  transition: transform 0.5s ease;
}

/* 滚动条样式 */
.task-items::-webkit-scrollbar {
  width: 4px;
}

.task-items::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.task-items::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.task-items::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .floating-task-bar {
    width: calc(100vw - 40px);
    right: 20px;
    left: 20px;
  }
  
  .floating-task-bar.collapsed {
    width: calc(100vw - 40px);
  }
}
</style> 
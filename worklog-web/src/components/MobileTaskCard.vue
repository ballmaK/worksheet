<template>
  <div class="mobile-task-card" @click="handleCardClick">
    <!-- 任务状态指示器 -->
    <div class="status-indicator" :class="task.status"></div>
    
    <!-- 任务主要内容 -->
    <div class="task-content">
      <div class="task-header">
        <h4 class="task-title">{{ task.title }}</h4>
        <div class="priority-badge" :class="task.priority">
          {{ getPriorityText(task.priority) }}
        </div>
      </div>
      
      <p class="task-description" v-if="task.description">
        {{ task.description }}
      </p>
      
      <!-- 任务元信息 -->
      <div class="task-meta">
        <div class="meta-item">
          <el-icon><Calendar /></el-icon>
          <span>{{ formatDate(task.due_date) }}</span>
        </div>
        <div class="meta-item" v-if="task.assignee">
          <el-icon><User /></el-icon>
          <span>{{ task.assignee.username }}</span>
        </div>
      </div>
      
      <!-- 快速操作按钮 -->
      <div class="quick-actions">
        <el-button 
          size="small" 
          type="primary" 
          @click.stop="updateStatus('in_progress')"
          v-if="task.status === 'pending'"
        >
          开始
        </el-button>
        <el-button 
          size="small" 
          type="success" 
          @click.stop="updateStatus('completed')"
          v-if="task.status === 'in_progress'"
        >
          完成
        </el-button>
        <el-button 
          size="small" 
          @click.stop="showComments"
        >
          评论
        </el-button>
      </div>
    </div>
    
    <!-- 滑动操作区域 -->
    <div class="swipe-actions">
      <div class="swipe-action edit" @click.stop="editTask">
        <el-icon><Edit /></el-icon>
      </div>
      <div class="swipe-action delete" @click.stop="deleteTask">
        <el-icon><Delete /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Calendar, User, Edit, Delete } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'
import { taskApi } from '@/api/task'

interface Task {
  id: number
  title: string
  description?: string
  status: string
  priority: string
  due_date?: string
  assignee?: {
    username: string
  }
}

const props = defineProps<{
  task: Task
}>()

const emit = defineEmits<{
  statusUpdated: [taskId: number, newStatus: string]
  taskEdited: [task: Task]
  taskDeleted: [taskId: number]
}>()

const getPriorityText = (priority: string) => {
  const priorityMap = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return priorityMap[priority] || priority
}

const handleCardClick = () => {
  // 触发任务详情查看
  emit('taskEdited', props.task)
}

const updateStatus = async (newStatus: string) => {
  try {
    await taskApi.updateTask(props.task.id, { status: newStatus })
    ElMessage.success('任务状态更新成功')
    emit('statusUpdated', props.task.id, newStatus)
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const showComments = () => {
  // 显示评论列表
  emit('taskEdited', props.task)
}

const editTask = () => {
  emit('taskEdited', props.task)
}

const deleteTask = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await taskApi.deleteTask(props.task.id)
    ElMessage.success('任务删除成功')
    emit('taskDeleted', props.task.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.mobile-task-card {
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #e4e7ed;
  transition: all 0.3s ease;
  touch-action: pan-y;
  overflow: hidden;
}

.mobile-task-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.status-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  border-radius: 2px;
}

.status-indicator.pending {
  background-color: #909399;
}

.status-indicator.in_progress {
  background-color: #409eff;
}

.status-indicator.completed {
  background-color: #67c23a;
}

.status-indicator.overdue {
  background-color: #f56c6c;
}

.task-content {
  position: relative;
  z-index: 1;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.task-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  flex: 1;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.priority-badge.low {
  background-color: #f0f9ff;
  color: #0ea5e9;
}

.priority-badge.medium {
  background-color: #fef3c7;
  color: #d97706;
}

.priority-badge.high {
  background-color: #fef2f2;
  color: #dc2626;
}

.priority-badge.urgent {
  background-color: #fef2f2;
  color: #dc2626;
  font-weight: 600;
}

.task-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
  margin: 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 12px;
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.quick-actions .el-button {
  flex: 1;
  min-height: 36px;
  font-size: 13px;
}

.swipe-actions {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  display: flex;
  align-items: center;
  background: linear-gradient(to left, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  padding: 0 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.mobile-task-card:hover .swipe-actions {
  opacity: 1;
}

.swipe-action {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.swipe-action.edit {
  background-color: #409eff;
  color: white;
}

.swipe-action.delete {
  background-color: #f56c6c;
  color: white;
}

.swipe-action:active {
  transform: scale(0.9);
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .mobile-task-card:hover .swipe-actions {
    opacity: 0;
  }
  
  .mobile-task-card:active .swipe-actions {
    opacity: 1;
  }
  
  .quick-actions .el-button {
    min-height: 44px;
  }
  
  .swipe-action {
    width: 44px;
    height: 44px;
  }
}

/* 小屏幕优化 */
@media (max-width: 480px) {
  .mobile-task-card {
    padding: 12px;
    margin-bottom: 8px;
  }
  
  .task-title {
    font-size: 15px;
  }
  
  .task-description {
    font-size: 13px;
  }
  
  .task-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .quick-actions {
    flex-direction: column;
    gap: 6px;
  }
}
</style> 
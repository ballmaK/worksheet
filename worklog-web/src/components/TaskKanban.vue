<template>
  <div class="kanban-container">
    <!-- 看板头部 -->
    <div class="kanban-header">
      <h3>{{ getViewTitle() }}</h3>
      <div class="kanban-actions">
        <el-button @click="refreshTasks" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 看板内容 -->
    <div class="kanban-board" v-loading="loading">
      <div
          v-for="status in taskStatuses"
          :key="status.value"
          class="kanban-column"
          @drop="handleDrop($event, status.value)"
          @dragover.prevent
          @dragenter.prevent
      >
        <div class="column-header">
          <div class="column-title">
            <el-tag :type="getStatusType(status.value)" size="small">
              {{ status.label }}
            </el-tag>
            <span class="task-count">({{ getStatusTasks(status.value).length }})</span>
          </div>
        </div>
        
        <div class="column-content">
          <div
              v-for="task in getStatusTasks(status.value)"
              :key="task.id"
              class="task-card"
              draggable="true"
              @click="handleTaskClick(task)"
              @dragstart="handleDragStart($event, task)"
              @dragend="handleDragEnd"
          >
            <!-- 任务卡片头部 -->
            <div class="task-card-header">
              <div class="task-title-section">
                <div class="task-title">
                  <el-icon class="task-icon"><User /></el-icon>
                  <span class="title-text">{{ task.title }}</span>
                </div>
                <div class="task-badges">
                  <span class="priority-badge" :class="`priority-${task.priority}`">
                    <el-icon class="priority-icon">
                      <Star v-if="task.priority === 'low'" />
                      <StarFilled v-else-if="task.priority === 'medium'" />
                      <Warning v-else-if="task.priority === 'high'" />
                      <CircleCloseFilled v-else-if="task.priority === 'urgent'" />
                      <Star v-else />
                    </el-icon>
                    <span class="priority-text">{{ getPriorityText(task.priority) }}</span>
                  </span>
                  <span class="task-type-badge" :class="`type-${task.task_type}`">
                    <el-icon class="type-icon"><Calendar /></el-icon>
                    <span class="type-text">{{ getTaskTypeLabel(task.task_type) }}</span>
                  </span>
                </div>
              </div>
            </div>

            <!-- 任务卡片内容 -->
            <div class="task-card-content" v-if="task.description">
              <div class="task-description">
                <span class="description-text">{{ task.description }}</span>
              </div>
            </div>

            <!-- 任务卡片底部 -->
            <div class="task-card-footer" v-if="hasFooterContent(task)">
              <div class="task-meta">
                <div class="meta-item" v-if="task.project">
                  <el-icon class="meta-icon"><Calendar /></el-icon>
                  <span class="meta-text project-text">{{ task.project.name }}</span>
                </div>
                <div class="meta-item" v-if="task.due_date">
                  <el-icon class="meta-icon"><Clock /></el-icon>
                  <span class="meta-text">{{ formatDate(task.due_date) }}</span>
                </div>
                <div class="meta-item" v-if="task.estimated_hours">
                  <el-icon class="meta-icon"><Timer /></el-icon>
                  <span class="meta-text">{{ task.estimated_hours }}小时</span>
                </div>
                <div class="meta-item" v-if="task.assignee">
                  <el-icon class="meta-icon"><User /></el-icon>
                  <span class="meta-text">{{ task.assignee?.username || '未知用户' }}</span>
                </div>
              </div>
            </div>

            <!-- 装饰性光点 -->
            <div class="sparkle-dot"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && filteredTasks.length === 0" class="empty-state">
      <el-empty :description="getEmptyDescription()">
        <el-button type="primary" @click="showCreateDialog">
          创建第一个任务
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Refresh,
  User,
  VideoPlay,
  CircleCheck,
  Upload,
  Check,
  CircleClose,
  MoreFilled,
  Calendar,
  Clock,
  Timer,
  Star,
  StarFilled,
  Warning,
  CircleCloseFilled
} from '@element-plus/icons-vue'
import type { Task } from '@/api/task'

// Props
interface Props {
  tasks: Task[]
  loading: boolean
  viewMode: string
  teams: any[]
  projects: any[]
  teamMembers: any[]
  selectedTeamId?: number
  selectedProjectId?: number
}

const props = withDefaults(defineProps<Props>(), {
  tasks: () => [],
  loading: false,
  viewMode: 'all',
  teams: () => [],
  projects: () => [],
  teamMembers: () => [],
  selectedTeamId: undefined,
  selectedProjectId: undefined
})

// Emits
const emit = defineEmits<{
  'refresh': []
  'view-task': [task: Task]
  'edit-task': [task: Task]
  'workflow-action': [command: string]
  'show-assign-dialog': [task: Task]
  'show-create-dialog': []
}>()

// 任务状态选项
const taskStatuses = [
  { label: '待分派', value: 'pending' },
  { label: '已分派', value: 'assigned' },
  { label: '进行中', value: 'in_progress' },
  { label: '待审核', value: 'review' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

// 计算属性
const filteredTasks = computed(() => props.tasks)

// 方法
const getViewTitle = () => {
  switch (props.viewMode) {
    case 'my':
      return '我的任务'
    case 'team':
      const team = props.teams.find(t => t.id === props.selectedTeamId)
      return team ? `${team.name} 团队任务` : '团队任务'
    case 'project':
      const project = props.projects.find(p => p.id === props.selectedProjectId)
      return project ? `${project.name} 项目任务` : '项目任务'
    default:
      return '全部任务'
  }
}

const getEmptyDescription = () => {
  switch (props.viewMode) {
    case 'my':
      return '您还没有任何任务'
    case 'team':
      return '该团队还没有任何任务'
    case 'project':
      return '该项目还没有任何任务'
    default:
      return '还没有任何任务'
  }
}

const getStatusTasks = (status: string) => {
  return filteredTasks.value.filter(task => task.status === status)
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'pending':
      return 'info'
    case 'assigned':
      return 'warning'
    case 'in_progress':
      return 'primary'
    case 'review':
      return 'warning'
    case 'completed':
      return 'success'
    case 'cancelled':
      return 'danger'
    default:
      return 'info'
  }
}

const getPriorityType = (priority: string) => {
  const priorityMap: Record<string, string> = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger',
    'urgent': 'danger'
  }
  return priorityMap[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const priorityMap: Record<string, string> = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'urgent': '紧急'
  }
  return priorityMap[priority] || priority
}

const getTaskTypeLabel = (taskType: string) => {
  const typeMap: Record<string, string> = {
    'feature': '功能开发',
    'bug': 'Bug修复',
    'improvement': '改进优化',
    'documentation': '文档工作',
    'meeting': '会议',
    'research': '调研',
    'other': '其他'
  }
  return typeMap[taskType] || '其他'
}

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString()
}

const getAssigneeName = (assigneeId: number) => {
  // 首先尝试从任务数据中获取负责人信息
  const task = props.tasks.find(t => t.assignee_id === assigneeId)
  if (task && task.assignee) {
    return task.assignee.username
  }
  
  // 如果任务数据中没有，则从团队成员中查找
  const member = props.teamMembers.find(m => m.user_id === assigneeId)
  return member ? member.username : '未知用户'
}

// 拖拽相关
const handleDragStart = (event: DragEvent, task: Task) => {
  event.dataTransfer?.setData('text/plain', task.id.toString())
}

const handleDragEnd = () => {
  // 拖拽结束处理
}

const handleDrop = (event: DragEvent, status: string) => {
  event.preventDefault()
  const taskId = event.dataTransfer?.getData('text/plain')
  if (taskId) {
    emit('workflow-action', `update-status:${taskId}:${status}`)
  }
}

// 任务操作
const refreshTasks = () => {
  emit('refresh')
}

const handleWorkflowAction = (command: string) => {
  emit('workflow-action', command)
}

const showAssignDialog = (task: Task) => {
  emit('show-assign-dialog', task)
}

const showCreateDialog = () => {
  emit('show-create-dialog')
}

// 权限检查方法
const canPerformWorkflowActions = (task: Task) => {
  const currentUserId = parseInt(localStorage.getItem('userId') || '0')
  if (!currentUserId) return false
  
  const isAdmin = isTeamAdmin(task.team_id)
  if (isAdmin) return true
  
  const isAssignee = task.assignee_id === currentUserId
  const isCreator = task.creator_id === currentUserId
  return isAssignee || isCreator
}

const canStartWork = (task: Task) => {
  const currentUserId = parseInt(localStorage.getItem('userId') || '0')
  const statusOk = task.status === 'assigned'
  const isAssignee = task.assignee_id === currentUserId
  return statusOk && isAssignee
}

const isTaskAssignee = (task: Task) => {
  const currentUserId = parseInt(localStorage.getItem('userId') || '0')
  return task.assignee_id === currentUserId
}

const canApproveTask = (task: Task) => {
  const currentUserId = parseInt(localStorage.getItem('userId') || '0')
  return task.creator_id === currentUserId || isTeamAdmin(task.team_id)
}

const canAssignTask = (task: Task) => {
  return isTeamAdmin(task.team_id)
}

const isTeamAdmin = (teamId: number) => {
  const currentUserId = parseInt(localStorage.getItem('userId') || '0')
  if (!currentUserId || !teamId) return false
  
  const member = props.teamMembers.find(m => m.user_id === currentUserId && m.team_id === teamId)
  return member ? member.role === 'admin' : false
}

const getPriorityIcon = (priority: string) => {
  const priorityIconMap: Record<string, any> = {
    'low': 'Star',
    'medium': 'StarFilled',
    'high': 'Warning',
    'urgent': 'CircleCloseFilled'
  }
  return priorityIconMap[priority] || 'Star'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待处理',
    'assigned': '已分配',
    'in_progress': '进行中',
    'review': '待审核',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const isOverdue = (dueDate: string) => {
  const today = new Date().toISOString().split('T')[0]
  const d = new Date(dueDate)
  const overdue = d < new Date(today)
  return overdue
}

const handleTaskClick = (task: Task) => {
  emit('view-task', task)
}

const hasFooterContent = (task: Task) => {
  return task.project || task.due_date || task.estimated_hours || task.assignee
}
</script>

<style scoped>
.kanban-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  min-height: 600px;
  overflow: hidden;
}

.kanban-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 4px;
  flex-shrink: 0;
}

.kanban-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.kanban-board {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  flex: 1;
  overflow-x: auto;
  padding-bottom: 20px;
  height: 100%;
  min-height: 0;
}

.kanban-column {
  background: #f5f7fa;
  border-radius: 12px;
  min-height: 500px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
}

.column-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
  border-radius: 12px 12px 0 0;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.column-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-count {
  color: #909399;
  font-size: 14px;
  font-weight: 500;
}

.column-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  min-height: 300px;
  height: 100%;
}

.task-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  min-height: fit-content;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.2);
}

.task-card::before {
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

.task-card::after {
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

.task-card:hover::before {
  opacity: 1;
}

.task-card:hover::after {
  opacity: 1;
}

/* 装饰性光点 */
.sparkle-dot {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 6px;
  height: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  opacity: 0.6;
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.task-card-header {
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.task-title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.task-icon {
  font-size: 16px;
  color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-text {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.4;
  flex: 1;
  word-wrap: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.task-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.priority-badge, .task-type-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.priority-badge:hover, .task-type-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
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

.priority-badge.priority-urgent {
  background: linear-gradient(135deg, #f56c6c 0%, #ff4757 100%);
  color: white;
  animation: urgentPulse 2s ease-in-out infinite;
}

@keyframes urgentPulse {
  0%, 100% {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  50% {
    box-shadow: 0 2px 8px rgba(245, 108, 108, 0.4);
  }
}

.task-type-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.priority-icon, .type-icon {
  font-size: 12px;
}

.priority-text, .type-text {
  font-size: 11px;
  font-weight: 600;
}

.task-card-content {
  margin-bottom: 10px;
  position: relative;
  z-index: 1;
}

.task-description {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  padding: 8px 10px;
  border-left: 3px solid #667eea;
}

.description-text {
  color: #606266;
  font-weight: 500;
  line-height: 1.5;
  font-size: 13px;
  display: block;
  word-wrap: break-word;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.task-card-footer {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  position: relative;
  z-index: 1;
  margin-top: 8px;
  min-height: 0;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  width: 100%;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #909399;
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}

.meta-item:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  transform: translateY(-1px);
}

.meta-icon {
  font-size: 11px;
  flex-shrink: 0;
}

.meta-text {
  font-size: 10px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  padding: 6px !important;
  border-radius: 6px !important;
  transition: all 0.3s ease !important;
  color: #909399 !important;
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(102, 126, 234, 0.1) !important;
}

.action-btn:hover {
  color: #667eea !important;
  background: rgba(102, 126, 234, 0.1) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2) !important;
}

.view-btn:hover {
  color: #409eff !important;
  background: rgba(64, 158, 255, 0.1) !important;
}

.edit-btn:hover {
  color: #e6a23c !important;
  background: rgba(230, 162, 60, 0.1) !important;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .kanban-board {
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
  }
}

@media (max-width: 1200px) {
  .kanban-board {
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
  
  .kanban-column {
    min-height: 450px;
  }
}

@media (max-width: 900px) {
  .kanban-board {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}

@media (max-width: 768px) {
  .kanban-container {
    height: calc(100vh - 150px);
    min-height: 500px;
  }
  
  .kanban-board {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .kanban-column {
    min-height: 400px;
    max-height: none;
  }
  
  .column-content {
    max-height: none;
  }
  
  .kanban-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .task-card {
    padding: 16px;
    margin-bottom: 12px;
  }
  
  .task-meta {
    gap: 6px;
  }
  
  .meta-item {
    max-width: 100px;
    font-size: 10px;
  }
  
  .meta-text {
    font-size: 9px;
  }
}
</style> 
<template>
  <div class="quick-filters">
    <!-- 活跃筛选标签 -->
    <div v-if="hasActiveFilters" class="active-filters">
      <div class="filter-tags">
        <span class="filter-label">当前视图：</span>
        <el-tag
            v-if="viewMode === 'my'"
            closable
            type="primary"
            @close="switchToAllTasks"
            class="filter-tag"
        >
          <el-icon><UserFilled /></el-icon>
          我的任务
        </el-tag>
        <el-tag
            v-if="viewMode === 'team' && selectedTeamId"
            closable
            type="success"
            @close="switchToAllTasks"
            class="filter-tag"
        >
          <el-icon><User /></el-icon>
          团队：{{ getTeamName(selectedTeamId) }}
        </el-tag>
        <el-tag
            v-if="viewMode === 'project' && selectedProjectId"
            closable
            type="warning"
            @close="switchToAllTasks"
            class="filter-tag"
        >
          <el-icon><Folder /></el-icon>
          项目：{{ getProjectName(selectedProjectId) }}
        </el-tag>
        <el-tag
            v-for="assigneeId in selectedAssigneeIds"
            :key="assigneeId"
            closable
            type="info"
            @close="removeAssigneeFilter(assigneeId)"
            class="filter-tag"
        >
          <el-icon><User /></el-icon>
          负责人：{{ getAssigneeName(assigneeId) }}
        </el-tag>
        <el-tag
            v-if="filterPriority"
            closable
            type="danger"
            @close="clearPriorityFilter"
            class="filter-tag"
        >
          <el-icon><Star /></el-icon>
          优先级：{{ getPriorityLabel(filterPriority) }}
        </el-tag>
        <el-tag
            v-if="filterTaskType"
            closable
            type="warning"
            @close="clearTaskTypeFilter"
            class="filter-tag"
        >
          <el-icon><Document /></el-icon>
          类型：{{ getTaskTypeLabel(filterTaskType) }}
        </el-tag>
        <el-tag
            v-if="filterStatus"
            closable
            type="success"
            @close="clearStatusFilter"
            class="filter-tag"
        >
          <el-icon><CircleCheck /></el-icon>
          状态：{{ getStatusLabel(filterStatus) }}
        </el-tag>
      </div>
      <el-button
          type="text"
          size="small"
          @click="switchToAllTasks"
          class="clear-all-btn"
      >
        <el-icon><Close /></el-icon>
        查看全部
      </el-button>
    </div>

    <!-- 筛选器 -->
    <div class="filter-section">
      <div class="filter-group">
        <span class="filter-group-label">任务视图：</span>
        <div class="filter-tags">
          <el-tag
              :type="viewMode === 'my' ? 'primary' : 'info'"
              :effect="viewMode === 'my' ? 'light' : 'plain'"
              @click="switchToMyTasks"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><UserFilled /></el-icon>
            我的任务
          </el-tag>
          <el-tag
              :type="viewMode === 'all' ? 'primary' : 'info'"
              :effect="viewMode === 'all' ? 'light' : 'plain'"
              @click="switchToAllTasks"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><DataBoard /></el-icon>
            全部任务
          </el-tag>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">团队筛选：</span>
        <div class="filter-tags">
          <el-tag
              v-for="team in teams"
              :key="team.id"
              :type="selectedTeamId === team.id ? 'success' : 'info'"
              :effect="selectedTeamId === team.id ? 'light' : 'plain'"
              @click="handleTeamSelect(team.id)"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><User /></el-icon>
            {{ team.name }}
          </el-tag>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">项目筛选：</span>
        <div class="filter-tags">
          <el-tag
              v-for="project in projects"
              :key="project.id"
              :type="selectedProjectId === project.id ? 'warning' : 'info'"
              :effect="selectedProjectId === project.id ? 'light' : 'plain'"
              @click="handleProjectSelect(project.id)"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><Folder /></el-icon>
            {{ project.name }}
          </el-tag>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">负责人筛选：</span>
        <div class="filter-tags">
          <el-tag
              v-for="member in teamMembers"
              :key="member.id"
              :type="selectedAssigneeIds.includes(member.id) ? 'danger' : 'info'"
              :effect="selectedAssigneeIds.includes(member.id) ? 'light' : 'plain'"
              @click="handleAssigneeSelect(member.id)"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><User /></el-icon>
            {{ member.username }}
          </el-tag>
          <!-- 调试信息：显示团队成员数量 -->
          <el-tag v-if="teamMembers.length === 0" type="warning" effect="plain">
            暂无团队成员数据
          </el-tag>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">优先级筛选：</span>
        <div class="filter-tags">
          <el-tag
              v-for="priority in ['low', 'medium', 'high', 'urgent']"
              :key="priority"
              :type="isPrioritySelected(priority) ? 'danger' : 'info'"
              :effect="isPrioritySelected(priority) ? 'light' : 'plain'"
              @click="handlePrioritySelect(priority)"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><Star /></el-icon>
            {{ getPriorityLabel(priority) }}
          </el-tag>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">任务类型筛选：</span>
        <div class="filter-tags">
          <el-tag
              v-for="type in ['bug', 'feature', 'improvement', 'task', 'other']"
              :key="type"
              :type="isTaskTypeSelected(type) ? 'warning' : 'info'"
              :effect="isTaskTypeSelected(type) ? 'light' : 'plain'"
              @click="handleTaskTypeSelect(type)"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><Document /></el-icon>
            {{ getTaskTypeLabel(type) }}
          </el-tag>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-group-label">任务状态筛选：</span>
        <div class="filter-tags">
          <el-tag
              v-for="status in ['pending', 'in_progress', 'completed', 'review', 'cancelled']"
              :key="status"
              :type="isStatusSelected(status) ? 'success' : 'info'"
              :effect="isStatusSelected(status) ? 'light' : 'plain'"
              @click="handleStatusSelect(status)"
              class="filter-option-tag"
          >
            <el-icon class="tag-icon"><CircleCheck /></el-icon>
            {{ getStatusLabel(status) }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { 
  UserFilled, 
  User, 
  Folder, 
  DataBoard, 
  Close,
  Star,
  Document,
  CircleCheck
} from '@element-plus/icons-vue'
import type { Team } from '@/api/team'
import type { Project } from '@/api/project'

// Props
interface Props {
  viewMode?: string
  selectedTeamId?: number
  selectedProjectId?: number
  selectedAssigneeIds?: number[]
  filterPriority?: string
  filterTaskType?: string
  filterStatus?: string
  teams?: Team[]
  projects?: Project[]
  teamMembers?: any[]
}

const props = withDefaults(defineProps<Props>(), {
  viewMode: 'all',
  selectedTeamId: undefined,
  selectedProjectId: undefined,
  selectedAssigneeIds: () => [],
  filterPriority: '',
  filterTaskType: '',
  filterStatus: '',
  teams: () => [],
  projects: () => [],
  teamMembers: () => []
})

// Emits
const emit = defineEmits<{
  'update:viewMode': [value: string]
  'update:selectedTeamId': [value: number | undefined]
  'update:selectedProjectId': [value: number | undefined]
  'update:selectedAssigneeIds': [value: number[]]
  'update:filterPriority': [value: string]
  'update:filterTaskType': [value: string]
  'update:filterStatus': [value: string]
  'teamChange': [teamId: number | undefined]
  'projectChange': [projectId: number | undefined]
  'assigneeChange': [assigneeIds: number[]]
  'switchToMyTasks': []
  'switchToAllTasks': []
}>()

// 本地状态
const viewMode = ref(props.viewMode)
const selectedTeamId = ref(props.selectedTeamId)
const selectedProjectId = ref(props.selectedProjectId)
const selectedAssigneeIds = ref<number[]>(props.selectedAssigneeIds)
const filterPriority = ref(props.filterPriority)
const filterTaskType = ref(props.filterTaskType)
const filterStatus = ref(props.filterStatus)

// 计算属性
const hasActiveFilters = computed(() => {
  return viewMode.value !== 'all' || 
         selectedTeamId.value || 
         selectedProjectId.value || 
         selectedAssigneeIds.value.length > 0 ||
         filterPriority.value ||
         filterTaskType.value ||
         filterStatus.value
})

// 监听本地状态变化，同步到父组件
watch(viewMode, (newValue) => {
  emit('update:viewMode', newValue)
})

watch(selectedTeamId, (newValue) => {
  emit('update:selectedTeamId', newValue)
})

watch(selectedProjectId, (newValue) => {
  emit('update:selectedProjectId', newValue)
})

watch(selectedAssigneeIds, (newValue) => {
  emit('update:selectedAssigneeIds', newValue)
})

watch(filterPriority, (newValue) => {
  emit('update:filterPriority', newValue)
})

watch(filterTaskType, (newValue) => {
  emit('update:filterTaskType', newValue)
})

watch(filterStatus, (newValue) => {
  emit('update:filterStatus', newValue)
})

// 监听props变化，同步到本地状态
watch(() => props.viewMode, (newValue) => {
  viewMode.value = newValue
})

watch(() => props.selectedTeamId, (newValue) => {
  selectedTeamId.value = newValue
})

watch(() => props.selectedProjectId, (newValue) => {
  selectedProjectId.value = newValue
})

watch(() => props.selectedAssigneeIds, (newValue) => {
  selectedAssigneeIds.value = newValue
})

watch(() => props.filterPriority, (newValue) => {
  filterPriority.value = newValue
})

watch(() => props.filterTaskType, (newValue) => {
  filterTaskType.value = newValue
})

watch(() => props.filterStatus, (newValue) => {
  filterStatus.value = newValue
})

// 监听团队成员数据变化
watch(() => props.teamMembers, (newValue) => {
  console.log('TaskFilters 接收到团队成员数据:', newValue)
}, { immediate: true })

// 方法
const switchToMyTasks = () => {
  viewMode.value = 'my'
  selectedTeamId.value = undefined
  selectedProjectId.value = undefined
  selectedAssigneeIds.value = []
  filterPriority.value = ''
  filterTaskType.value = ''
  filterStatus.value = ''
  emit('switchToMyTasks')
}

const switchToAllTasks = () => {
  viewMode.value = 'all'
  selectedTeamId.value = undefined
  selectedProjectId.value = undefined
  selectedAssigneeIds.value = []
  filterPriority.value = ''
  filterTaskType.value = ''
  filterStatus.value = ''
  emit('switchToAllTasks')
}

const handleTeamSelect = (teamId: number) => {
  if (selectedTeamId.value === teamId) {
    // 如果点击的是当前选中的团队，则取消选择
    selectedTeamId.value = undefined
    viewMode.value = 'all'
  } else {
    // 选择新团队
    selectedTeamId.value = teamId
    viewMode.value = 'team'
    selectedProjectId.value = undefined
  }
  emit('teamChange', selectedTeamId.value)
}

const handleProjectSelect = (projectId: number) => {
  if (selectedProjectId.value === projectId) {
    // 如果点击的是当前选中的项目，则取消选择
    selectedProjectId.value = undefined
    viewMode.value = 'all'
  } else {
    // 选择新项目
    selectedProjectId.value = projectId
    viewMode.value = 'project'
    selectedTeamId.value = undefined
  }
  emit('projectChange', selectedProjectId.value)
}

const handleAssigneeSelect = (assigneeId: number) => {
  const index = selectedAssigneeIds.value.indexOf(assigneeId)
  if (index > -1) {
    // 如果已选中，则取消选择
    selectedAssigneeIds.value.splice(index, 1)
  } else {
    // 如果未选中，则添加选择
    selectedAssigneeIds.value.push(assigneeId)
  }
  emit('assigneeChange', selectedAssigneeIds.value)
}

const removeAssigneeFilter = (assigneeId: number) => {
  const index = selectedAssigneeIds.value.indexOf(assigneeId)
  if (index > -1) {
    selectedAssigneeIds.value.splice(index, 1)
    emit('assigneeChange', selectedAssigneeIds.value)
  }
}

const getTeamName = (teamId: number) => {
  const team = props.teams.find(t => t.id === teamId)
  return team ? team.name : `团队${teamId}`
}

const getProjectName = (projectId: number) => {
  const project = props.projects.find(p => p.id === projectId)
  return project ? project.name : `项目${projectId}`
}

const getAssigneeName = (assigneeId: number) => {
  const member = props.teamMembers.find(m => m.id === assigneeId)
  return member ? member.username : `用户${assigneeId}`
}

const isPrioritySelected = (priority: string) => {
  return filterPriority.value === priority
}

const handlePrioritySelect = (priority: string) => {
  filterPriority.value = priority
  emit('update:filterPriority', priority)
}

const isTaskTypeSelected = (type: string) => {
  return filterTaskType.value === type
}

const handleTaskTypeSelect = (type: string) => {
  filterTaskType.value = type
  emit('update:filterTaskType', type)
}

const isStatusSelected = (status: string) => {
  return filterStatus.value === status
}

const handleStatusSelect = (status: string) => {
  filterStatus.value = status
  emit('update:filterStatus', status)
}

const getPriorityLabel = (priority: string): string => {
  const priorityLabels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return priorityLabels[priority] || priority
}

const getTaskTypeLabel = (type: string): string => {
  const typeLabels: Record<string, string> = {
    bug: '缺陷',
    feature: '功能',
    improvement: '改进',
    task: '任务',
    other: '其他'
  }
  return typeLabels[type] || type
}

const getStatusLabel = (status: string): string => {
  const statusLabels: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    review: '审核中',
    cancelled: '已取消'
  }
  return statusLabels[status] || status
}

const clearPriorityFilter = () => {
  filterPriority.value = ''
  emit('update:filterPriority', '')
}

const clearTaskTypeFilter = () => {
  filterTaskType.value = ''
  emit('update:filterTaskType', '')
}

const clearStatusFilter = () => {
  filterStatus.value = ''
  emit('update:filterStatus', '')
}
</script>

<style scoped>
.quick-filters {
  margin-bottom: 24px;
}

.active-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  margin-bottom: 16px;
}

.filter-tags {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.clear-all-btn {
  color: #64748b;
  font-size: 13px;
}

.clear-all-btn:hover {
  color: #ef4444;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-group-label {
  font-size: 14px;
  color: #475569;
  font-weight: 600;
  padding-bottom: 4px;
  border-bottom: 1px solid #e2e8f0;
}

.filter-option-tag {
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  margin: 2px;
}

.filter-option-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-icon {
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .active-filters {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .filter-section {
    padding: 16px;
    gap: 16px;
  }

  .filter-group {
    gap: 10px;
  }

  .filter-tags {
    justify-content: flex-start;
  }
}
</style> 
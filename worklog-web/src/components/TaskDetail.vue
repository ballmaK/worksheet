<template>
  <el-drawer
      v-model="visible"
      :title="task ? '任务详情' : '创建任务'"
      size="600px"
      :destroy-on-close="false"
      :class="[styles['task-detail-drawer'], styles[`status-${currentTaskStatus}`]]"
  >
    <div :class="styles['task-detail-content']">
      <!-- 任务标题区域 -->
      <div :class="styles['task-header-section']">
        <div :class="styles['task-title-section']">
          <el-input
              v-model="taskForm.title"
              placeholder="请输入任务标题"
              :maxlength="100"
              show-word-limit
              :disabled="!isFieldEditable('title')"
              :class="styles['task-title-input']"
          />
        </div>
      </div>

      <!-- 任务描述区域 -->
      <div :class="styles['task-description-section']">
        <div :class="styles['section-title']">
          <el-icon><Document /></el-icon>
          <span>任务描述</span>
        </div>
          <el-input
              v-model="taskForm.description"
              type="textarea"
              rows="4"
            placeholder="请输入任务描述..."
              :maxlength="500"
              show-word-limit
            :disabled="!isFieldEditable('description')"
            :class="styles['description-textarea']"
        />
      </div>

      <!-- 基本信息区域 -->
      <div :class="styles['task-basic-section']">
        <div :class="styles['section-title']">
          <el-icon><InfoFilled /></el-icon>
          <span>基本信息</span>
        </div>
        
        <!-- 状态提示 -->
        <div :class="styles['status-hint']">
          <el-alert
              :title="getStatusHintTitle()"
              :description="getStatusHintDescription()"
              :type="getStatusHintType()"
              :closable="false"
              show-icon
              :class="styles['status-alert']"
          />
        </div>
        
        <!-- 所属项目 -->
        <div :class="[styles['info-item'], { [styles['disabled']]: !isFieldEditable('project_id') }]">
          <div :class="styles['info-label']">所属项目</div>
          <div :class="styles['info-content']">
            <div :class="styles['tag-selector']">
              <el-tag
                v-for="project in teamProjects"
                :key="project.id"
                  :type="taskForm.project_id === project.id ? 'primary' : 'info'"
                  :effect="taskForm.project_id === project.id ? 'light' : 'plain'"
                  :class="[styles['tag-item'], { [styles['disabled']]: !isFieldEditable('project_id') }]"
                  @click="isFieldEditable('project_id') ? selectProject(project) : null"
              >
                <el-icon :class="styles['tag-icon']">
                  <component :is="Document" />
                </el-icon>
                {{ project.name }}
                <el-icon 
                    v-if="taskForm.project_id === project.id && isFieldEditable('project_id')" 
                    :class="styles['tag-close']" 
                    @click.stop="clearProject"
                >
                  <Close />
                </el-icon>
              </el-tag>
              <el-tag
                  v-if="teamProjects.length === 0"
                  type="info"
                  effect="plain"
                  :class="styles['tag-item']"
                  disabled
              >
                <el-icon><Document /></el-icon>
                暂无项目
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 负责人 -->
        <div :class="[styles['info-item'], { [styles['disabled']]: !isFieldEditable('assignee_id') }]">
          <div :class="styles['info-label']">负责人</div>
          <div :class="styles['info-content']">
            <div :class="styles['tag-selector']">
              <el-tag
                  v-for="member in localTeamMembers"
                  :key="member.user_id"
                  :type="taskForm.assignee_id === member.user_id ? 'success' : 'info'"
                  :effect="taskForm.assignee_id === member.user_id ? 'light' : 'plain'"
                  :class="[styles['tag-item'], { [styles['disabled']]: !isFieldEditable('assignee_id') }]"
                  @click="isFieldEditable('assignee_id') ? selectAssignee(member) : null"
              >
                <el-avatar :size="16" :src="member.avatar">
                  {{ member.username?.[0]?.toUpperCase() }}
                </el-avatar>
                {{ member.username }}
                <el-icon 
                    v-if="taskForm.assignee_id === member.user_id && isFieldEditable('assignee_id')" 
                    :class="styles['tag-close']" 
                    @click.stop="clearAssignee"
                >
                  <Close />
                </el-icon>
              </el-tag>
              <el-tag
                  v-if="localTeamMembers.length === 0"
                  type="info"
                  effect="plain"
                  :class="styles['tag-item']"
                  disabled
              >
                <el-icon><User /></el-icon>
                暂无成员
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 任务类型 -->
        <div :class="[styles['info-item'], { [styles['disabled']]: !isFieldEditable('task_type') }]">
          <div :class="styles['info-label']">任务类型</div>
          <div :class="styles['info-content']">
            <div :class="styles['tag-selector']">
              <el-tag
                  v-for="type in taskTypes"
                  :key="type.value"
                  :type="taskForm.task_type === type.value ? 'primary' : 'info'"
                  :effect="taskForm.task_type === type.value ? 'light' : 'plain'"
                  :class="[styles['tag-item'], { [styles['disabled']]: !isFieldEditable('task_type') }]"
                  @click="isFieldEditable('task_type') ? selectTaskType(type.value) : null"
              >
                <el-icon :class="styles['tag-icon']">
                  <component :is="type.icon" />
                </el-icon>
                {{ type.label }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 优先级 -->
        <div :class="[styles['info-item'], { [styles['disabled']]: !isFieldEditable('priority') }]">
          <div :class="styles['info-label']">优先级</div>
          <div :class="styles['info-content']">
            <div :class="styles['tag-selector']">
              <el-tag
                  v-for="priority in priorities"
                  :key="priority.value"
                  :type="taskForm.priority === priority.value ? priority.type : 'info'"
                  :effect="taskForm.priority === priority.value ? 'light' : 'plain'"
                  :class="[styles['tag-item'], { [styles['disabled']]: !isFieldEditable('priority') }]"
                  @click="isFieldEditable('priority') ? selectPriority(priority.value) : null"
              >
                <el-icon :class="styles['tag-icon']">
                  <component :is="priority.icon" />
                </el-icon>
                {{ priority.label }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 任务状态 -->
        <div :class="styles['info-item']">
          <div :class="styles['info-label']">任务状态</div>
          <div :class="styles['info-content']">
            <div :class="styles['status-section']">
              <!-- 当前状态显示 -->
              <el-tag
                  :type="getStatusType(currentTaskStatus)"
                  :effect="isFieldEditable('status') ? 'light' : 'plain'"
                  :class="[styles['current-status'], { [styles['disabled']]: !isFieldEditable('status') }]"
              >
                {{ getStatusLabel(currentTaskStatus) }}
              </el-tag>
              
              <!-- 状态变更选项 -->
              <div v-if="isFieldEditable('status') && availableStatuses.length > 0" :class="styles['status-options']">
                <el-dropdown @command="changeStatus">
                  <el-button type="primary" size="small" text>
                    变更状态
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                          v-for="status in availableStatuses"
                          :key="status.value"
                          :command="status.value"
                          :class="styles['status-option']"
                      >
                        <el-tag :type="status.type" size="small">
                          {{ status.label }}
                        </el-tag>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 时间信息区域 -->
      <div :class="styles['task-time-section']">
        <div :class="styles['section-title']">
          <el-icon><Clock /></el-icon>
          <span>时间信息</span>
        </div>
        
        <!-- 截止日期 -->
        <div :class="[styles['info-item'], { [styles['disabled']]: !isFieldEditable('due_date') }]">
          <div :class="styles['info-label']">截止日期</div>
          <div :class="styles['info-content']">
            <div :class="styles['date-selector']">
              <!-- 快捷日期标签 -->
              <div :class="styles['quick-date-tags']">
                <el-tag
                    v-for="quickDate in quickDates"
                    :key="quickDate.value"
                    :type="isQuickDateSelected(quickDate.value) ? 'primary' : 'info'"
                    :effect="isQuickDateSelected(quickDate.value) ? 'light' : 'plain'"
                    :class="[styles['tag-item'], { [styles['disabled']]: !isFieldEditable('due_date') }]"
                    @click="isFieldEditable('due_date') ? selectQuickDate(quickDate.value) : null"
                >
                  {{ quickDate.label }}
                </el-tag>
              </div>
              
              <!-- 自定义日期选择 -->
              <div :class="styles['custom-date']">
                <el-date-picker
                    v-model="taskForm.due_date"
                    type="datetime"
                    placeholder="选择自定义日期"
                    :disabled="!isFieldEditable('due_date')"
                    :shortcuts="dateShortcuts"
                    :disabled-date="disabledDate"
                    :class="styles['date-picker']"
                />
                <el-button
                    v-if="taskForm.due_date && isFieldEditable('due_date')"
                    type="text"
                    size="small"
                    @click="clearDueDate"
                >
                  清除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 工时信息区域 -->
      <div :class="styles['task-hours-section']">
        <div :class="styles['section-title']">
          <el-icon><Timer /></el-icon>
          <span>工时信息</span>
        </div>
        
        <!-- 预估工时 -->
        <div :class="[styles['info-item'], { [styles['disabled']]: !isFieldEditable('estimated_hours') }]">
          <div :class="styles['info-label']">预估工时</div>
          <div :class="styles['info-content']">
            <div :class="styles['hours-selector']">
              <div :class="styles['hours-slider']">
                <el-slider
                    v-model="taskForm.estimated_hours"
                    :min="0"
                    :max="40"
                    :step="0.5"
                    :disabled="!isFieldEditable('estimated_hours')"
                    show-input
                    input-size="small"
                    :class="styles['hours-slider']"
                />
                <div :class="styles['hours-labels']">
                  <span>0小时</span>
                  <span>40小时</span>
                </div>
              </div>
              <div :class="styles['hours-input']">
          <el-input-number
              v-model="taskForm.estimated_hours"
              :min="0"
              :max="1000"
              :precision="1"
                    :disabled="!isFieldEditable('estimated_hours')"
                    placeholder="手动输入"
                    size="small"
                />
                <span :class="styles['hours-unit']">小时</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div :class="styles['drawer-footer']">
        <el-button @click="close">取消</el-button>
        <el-button
            v-if="task"
            type="primary"
            @click="submit"
            :loading="submitting"
        >
          更新任务
        </el-button>
        <el-button
            v-else
            type="primary"
            @click="submit"
            :loading="submitting"
        >
          创建任务
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  InfoFilled,
  Clock,
  Timer,
  Plus,
  Close,
  Check,
  Search,
  Star,
  StarFilled,
  Warning,
  CircleCloseFilled,
  VideoPlay,
  Edit,
  Calendar,
  User,
  ArrowDown
} from '@element-plus/icons-vue'
import type { Task } from '@/api/task'
import type { Team } from '@/api/team'
import type { Project } from '@/api/project'
import { projectApi } from '@/api/project'
import { taskApi } from '@/api/task'
import { teamApi } from '@/api/team'
import styles from './TaskDetail.module.css'

// Props
interface Props {
  visible?: boolean
  task?: Task | null
  teams?: Team[]
  projects?: Project[]
  teamMembers?: any[]
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  task: null,
  teams: () => [],
  projects: () => [],
  teamMembers: () => []
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'submit': []
  'close': []
}>()

// 本地状态
const visible = ref(props.visible)
const submitting = ref(false)
const taskFormRef = ref()
const teamProjects = ref<Project[]>([])
const localTeamMembers = ref<any[]>([])

// 任务表单
const taskForm = ref({
  title: '',
  description: '',
  team_id: undefined as number | undefined,
  project_id: undefined as number | undefined,
  assignee_id: undefined as number | undefined,
  status: 'pending' as string,
  priority: 'medium' as string,
  task_type: 'feature' as string,
  estimated_hours: undefined as number | undefined,
  due_date: null as Date | null,
  tags: ''
})

// 任务类型配置
const taskTypes = [
  { label: '功能开发', value: 'feature', icon: VideoPlay },
  { label: 'Bug修复', value: 'bug', icon: Warning },
  { label: '改进优化', value: 'improvement', icon: Edit },
  { label: '文档工作', value: 'documentation', icon: Document },
  { label: '其他', value: 'other', icon: User }
];

// 优先级配置
const priorities = [
  { label: '低', value: 'low', type: 'info', icon: Star },
  { label: '中', value: 'medium', type: 'warning', icon: StarFilled },
  { label: '高', value: 'high', type: 'danger', icon: Warning },
  { label: '紧急', value: 'urgent', type: 'danger', icon: CircleCloseFilled }
];

// 快捷日期配置
const quickDates = [
  { label: '今天', value: 'today' },
  { label: '明天', value: 'tomorrow' },
  { label: '本周', value: 'this_week' },
  { label: '下周', value: 'next_week' },
  { label: '本月', value: 'this_month' }
];

// 日期快捷选项
const dateShortcuts = [
  {
    text: '今天',
    value: new Date()
  },
  {
    text: '明天',
    value: () => {
      const date = new Date()
      date.setTime(date.getTime() + 3600 * 1000 * 24)
      return date
    }
  },
  {
    text: '一周后',
    value: () => {
      const date = new Date()
      date.setTime(date.getTime() + 3600 * 1000 * 24 * 7)
      return date
    }
  }
];

// 任务状态枚举
enum TaskStatus {
  PENDING = 'pending',
  ASSIGNED = 'assigned', 
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

// 状态流转配置
const statusTransitions = {
  [TaskStatus.PENDING]: [TaskStatus.ASSIGNED],
  [TaskStatus.ASSIGNED]: [TaskStatus.IN_PROGRESS],
  [TaskStatus.IN_PROGRESS]: [TaskStatus.COMPLETED, TaskStatus.CANCELLED],
  [TaskStatus.COMPLETED]: [],
  [TaskStatus.CANCELLED]: []
}

// 字段编辑权限配置
const fieldEditPermissions = {
  // 核心信息项（始终可编辑）
  title: () => true,
  description: () => true,
  task_type: () => true,
  priority: () => true,
  
  // 分配相关（状态限制）
  project_id: (status: TaskStatus) => {
    return [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS].includes(status)
  },
  assignee_id: (status: TaskStatus) => {
    return [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS].includes(status)
  },
  
  // 时间相关（状态限制）
  due_date: (status: TaskStatus) => {
    return [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS].includes(status)
  },
  estimated_hours: (status: TaskStatus) => {
    return [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS].includes(status)
  },
  
  // 状态管理
  status: (status: TaskStatus) => {
    return statusTransitions[status]?.length > 0
  }
}

// 计算属性
const selectedProject = computed(() => {
  return teamProjects.value.find(p => p.id === taskForm.value.project_id)
})

const selectedAssignee = computed(() => {
  return localTeamMembers.value.find(m => m.user_id === taskForm.value.assignee_id)
})

// 禁用过去的日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7
}

// 监听visible变化
watch(visible, (newValue) => {
  emit('update:visible', newValue)
})

watch(() => props.visible, (newValue) => {
  visible.value = newValue
})

// 监听task变化，填充表单
watch(() => props.task, (newTask) => {
  if (newTask) {
    taskForm.value = {
      title: newTask.title,
      description: newTask.description || '',
      team_id: newTask.team_id,
      project_id: newTask.project_id,
      assignee_id: newTask.assignee_id,
      status: newTask.status,
      priority: newTask.priority,
      task_type: newTask.task_type,
      estimated_hours: newTask.estimated_hours,
      due_date: newTask.due_date ? new Date(newTask.due_date) : null,
      tags: newTask.tags || ''
    }
    
    // 加载团队项目和成员
    if (newTask.team_id) {
      handleTeamSelect(newTask.team_id)
      fetchTeamMembers(newTask.team_id)
    }
    
    // 加载项目信息（如果任务有项目但不在当前团队项目列表中）
    if (newTask.project_id) {
      fetchProjectInfo(newTask.project_id)
    }
  } else {
    // 重置表单
    taskForm.value = {
      title: '',
      description: '',
      team_id: undefined,
      project_id: undefined,
      assignee_id: undefined,
      status: 'pending',
      priority: 'medium',
      task_type: 'feature',
      estimated_hours: undefined,
      due_date: null,
      tags: ''
    }
    teamProjects.value = []
    localTeamMembers.value = []
  }
}, { immediate: true })

// 处理团队选择
const handleTeamSelect = async (teamId: number) => {
  // 只有在创建新任务时才清除项目ID，编辑现有任务时保留项目ID
  if (!props.task) {
  taskForm.value.project_id = undefined
  }
  
  if (teamId) {
    try {
      const response = await projectApi.getProjects(teamId)
      teamProjects.value = Array.isArray(response) ? response : []
    } catch (error) {
      ElMessage.error('获取团队项目失败')
      teamProjects.value = []
    }
  } else {
    teamProjects.value = []
  }
}

// 获取团队成员
const fetchTeamMembers = async (teamId: number) => {
  if (!teamId) {
    localTeamMembers.value = []
    return
  }
  
  try {
    const response = await teamApi.getTeamMembers(teamId)
    const members = response.data || response
    localTeamMembers.value = Array.isArray(members) ? members : []
  } catch (error) {
    console.error('获取团队成员失败:', error)
    ElMessage.error('获取团队成员失败')
    localTeamMembers.value = []
  }
}

// 获取项目信息（包括当前任务的项目）
const fetchProjectInfo = async (projectId: number) => {
  if (!projectId) return
  
  try {
    console.log('开始获取项目信息:', projectId)
    console.log('当前团队项目列表:', teamProjects.value)
    
    // 如果当前团队项目列表中已经包含该项目，不需要额外获取
    const existingProject = teamProjects.value.find(p => p.id === projectId)
    if (existingProject) {
      console.log('项目已存在于列表中:', existingProject)
      return
    }
    
    // 否则获取项目详情
    const response = await projectApi.getProject(projectId)
    const project = response.data
    console.log('获取到的项目信息:', project)
    
    if (project && !teamProjects.value.find(p => p.id === project.id)) {
      teamProjects.value.push(project)
      console.log('项目已添加到列表，当前列表:', teamProjects.value)
    }
  } catch (error) {
    console.error('获取项目信息失败:', error)
  }
}

// 方法
const getProjectTagType = (project: Project | undefined) => {
  if (!project) return 'info'
  // 可以根据项目类型返回不同的颜色
  return 'primary'
}

const selectTaskType = (type: string) => {
  taskForm.value.task_type = type
}

const selectPriority = (priority: string) => {
  taskForm.value.priority = priority
}

const selectProject = async (project: Project) => {
  if (await confirmSensitiveOperation('更改项目')) {
    taskForm.value.project_id = project.id
  }
}

const selectAssignee = async (member: any) => {
  if (await confirmSensitiveOperation('重新分配负责人')) {
    taskForm.value.assignee_id = member.user_id
  }
}

const clearProject = async () => {
  if (await confirmSensitiveOperation('清除项目')) {
    taskForm.value.project_id = undefined
  }
}

const clearAssignee = async () => {
  if (await confirmSensitiveOperation('清除负责人')) {
    taskForm.value.assignee_id = undefined
  }
}

const selectQuickDate = async (quickDate: string) => {
  if (await confirmSensitiveOperation('更改截止日期')) {
    const now = new Date()
    switch (quickDate) {
      case 'today':
        taskForm.value.due_date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 18, 0, 0)
        break
      case 'tomorrow':
        taskForm.value.due_date = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 18, 0, 0)
        break
      case 'this_week':
        const daysUntilFriday = 5 - now.getDay()
        taskForm.value.due_date = new Date(now.getFullYear(), now.getMonth(), now.getDate() + daysUntilFriday, 18, 0, 0)
        break
      case 'next_week':
        const daysUntilNextMonday = 8 - now.getDay()
        taskForm.value.due_date = new Date(now.getFullYear(), now.getMonth(), now.getDate() + daysUntilNextMonday, 18, 0, 0)
        break
      case 'this_month':
        taskForm.value.due_date = new Date(now.getFullYear(), now.getMonth() + 1, 0, 18, 0, 0)
        break
    }
  }
}

const isQuickDateSelected = (quickDate: string) => {
  if (!taskForm.value.due_date) return false
  const dueDate = taskForm.value.due_date
  const now = new Date()
  
  switch (quickDate) {
    case 'today':
      return dueDate.toDateString() === now.toDateString()
    case 'tomorrow':
      const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)
      return dueDate.toDateString() === tomorrow.toDateString()
    case 'this_week':
      const daysUntilFriday = 5 - now.getDay()
      const thisWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() + daysUntilFriday)
      return dueDate.toDateString() === thisWeek.toDateString()
    case 'next_week':
      const daysUntilNextMonday = 8 - now.getDay()
      const nextWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() + daysUntilNextMonday)
      return dueDate.toDateString() === nextWeek.toDateString()
    case 'this_month':
      const thisMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      return dueDate.toDateString() === thisMonth.toDateString()
    default:
      return false
  }
}

const clearDueDate = async () => {
  if (await confirmSensitiveOperation('清除截止日期')) {
    taskForm.value.due_date = null
  }
}

const close = () => {
  visible.value = false
  emit('close')
}

const submit = async () => {
  try {
    submitting.value = true
    
    if (props.task) {
      // 更新任务
      const updateData: any = {
        title: taskForm.value.title,
        description: taskForm.value.description,
        project_id: taskForm.value.project_id,
        assignee_id: taskForm.value.assignee_id,
        priority: taskForm.value.priority as any,
        due_date: taskForm.value.due_date?.toISOString(),
        estimated_hours: taskForm.value.estimated_hours,
        task_type: taskForm.value.task_type as any,
        tags: taskForm.value.tags
      }
      
      // 只有当用户手动改变了状态时，才发送状态字段
      // 如果状态没有变化，让后端根据负责人分配情况自动判断
      if (props.task.status !== taskForm.value.status) {
        updateData.status = taskForm.value.status as any
      }
      
      await taskApi.updateTask(props.task.id, updateData)
      ElMessage.success('任务更新成功')
    } else {
      // 创建任务
      const createData = {
        title: taskForm.value.title,
        description: taskForm.value.description,
        team_id: taskForm.value.team_id!,
        project_id: taskForm.value.project_id,
        assignee_id: taskForm.value.assignee_id,
        status: taskForm.value.status as any,
        priority: taskForm.value.priority as any,
        due_date: taskForm.value.due_date?.toISOString(),
        estimated_hours: taskForm.value.estimated_hours,
        task_type: taskForm.value.task_type as any,
        tags: taskForm.value.tags
      }
      
      await taskApi.createTask(createData)
      ElMessage.success('任务创建成功')
    }
    
    emit('submit')
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 计算当前任务状态
const currentTaskStatus = computed(() => {
  return taskForm.value.status as TaskStatus
})

// 检查字段是否可编辑
const isFieldEditable = (fieldName: string) => {
  const permission = fieldEditPermissions[fieldName as keyof typeof fieldEditPermissions]
  if (!permission) return false
  
  if (typeof permission === 'function') {
    return permission(currentTaskStatus.value)
  }
  
  return permission
}

// 获取可用的状态选项
const availableStatuses = computed(() => {
  const currentStatus = currentTaskStatus.value
  const transitions = statusTransitions[currentStatus] || []
  
  return transitions.map(status => ({
    label: getStatusLabel(status),
    value: status,
    type: getStatusType(status)
  }))
})

// 状态标签映射
const getStatusLabel = (status: TaskStatus) => {
  const labels = {
    [TaskStatus.PENDING]: '待处理',
    [TaskStatus.ASSIGNED]: '已分配',
    [TaskStatus.IN_PROGRESS]: '进行中',
    [TaskStatus.COMPLETED]: '已完成',
    [TaskStatus.CANCELLED]: '已取消'
  }
  return labels[status] || status
}

// 状态类型映射
const getStatusType = (status: TaskStatus) => {
  const types = {
    [TaskStatus.PENDING]: 'info',
    [TaskStatus.ASSIGNED]: 'warning',
    [TaskStatus.IN_PROGRESS]: 'primary',
    [TaskStatus.COMPLETED]: 'success',
    [TaskStatus.CANCELLED]: 'danger'
  }
  return types[status] || 'info'
}

// 状态变更确认
const confirmStatusChange = async (newStatus: TaskStatus) => {
  const currentStatus = currentTaskStatus.value
  
  // 特殊状态变更确认
  if (currentStatus === TaskStatus.IN_PROGRESS && newStatus === TaskStatus.CANCELLED) {
    try {
      await ElMessageBox.confirm(
        '确定要取消这个正在进行的任务吗？',
        '确认取消',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return false
    }
  }
  
  if (currentStatus === TaskStatus.ASSIGNED && newStatus === TaskStatus.IN_PROGRESS) {
    try {
      await ElMessageBox.confirm(
        '确定要开始执行这个任务吗？',
        '确认开始',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      )
    } catch {
      return false
    }
  }
  
  return true
}

// 敏感操作确认
const confirmSensitiveOperation = async (operation: string) => {
  const currentStatus = currentTaskStatus.value
  
  if (currentStatus === TaskStatus.IN_PROGRESS) {
    try {
      await ElMessageBox.confirm(
        `任务正在进行中，确定要${operation}吗？`,
        '确认操作',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      return true
    } catch {
      return false
    }
  }
  
  return true
}

// 状态变更逻辑
const changeStatus = async (newStatus: TaskStatus) => {
  if (await confirmStatusChange(newStatus)) {
    taskForm.value.status = newStatus
  }
}

// 状态提示功能
const getStatusHintTitle = () => {
  const currentStatus = currentTaskStatus.value
  const labels = {
    [TaskStatus.PENDING]: '待处理',
    [TaskStatus.ASSIGNED]: '已分配',
    [TaskStatus.IN_PROGRESS]: '进行中',
    [TaskStatus.COMPLETED]: '已完成',
    [TaskStatus.CANCELLED]: '已取消'
  }
  return `当前任务状态：${labels[currentStatus] || currentStatus}`
}

const getStatusHintDescription = () => {
  const currentStatus = currentTaskStatus.value
  const labels = {
    [TaskStatus.PENDING]: '任务等待分配',
    [TaskStatus.ASSIGNED]: '任务已分配',
    [TaskStatus.IN_PROGRESS]: '任务进行中',
    [TaskStatus.COMPLETED]: '任务已完成',
    [TaskStatus.CANCELLED]: '任务已取消'
  }
  return labels[currentStatus] || '任务状态未知'
}

const getStatusHintType = () => {
  const currentStatus = currentTaskStatus.value
  const types = {
    [TaskStatus.PENDING]: 'info',
    [TaskStatus.ASSIGNED]: 'warning',
    [TaskStatus.IN_PROGRESS]: 'primary',
    [TaskStatus.COMPLETED]: 'success',
    [TaskStatus.CANCELLED]: 'danger'
  }
  return types[currentStatus] || 'info'
}
</script> 
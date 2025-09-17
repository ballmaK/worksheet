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
        <div :class="[styles['info-item'], { [styles['disabled']]: !isFieldEditable('assignee_id') }]" data-field="assignee_id">
          <div :class="styles['info-label']">
            负责人
            <el-tag v-if="showAssigneeRequired" type="warning" size="small" style="margin-left: 8px;">
              请选择负责人
            </el-tag>
          </div>
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

        <!-- 实际工时（已完成任务显示） -->
        <div v-if="task && task.actual_hours !== undefined && task.actual_hours > 0" :class="styles['info-item']">
          <div :class="styles['info-label']">实际工时</div>
          <div :class="styles['info-content']">
            <div :class="styles['actual-hours-display']">
              <el-tag type="success" size="large">
                <el-icon><Timer /></el-icon>
                {{ task.actual_hours.toFixed(1) }} 小时
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 实际工时录入（仅在完成任务时显示） -->
        <div v-if="showActualHoursInput" :class="styles['info-item']">
          <div :class="styles['info-label']">实际工时</div>
          <div :class="styles['info-content']">
            <!-- 起始时间显示 -->
            <div :class="styles['start-time-display']">
              <div :class="styles['start-time-label']">起始时间</div>
              <div :class="styles['time-display']">
                <el-icon :class="styles['time-icon']"><Clock /></el-icon>
                <span v-if="!isEditingStartTime" :class="styles['time-text']">{{ formatTaskStartTime(getTaskStartTime()) }}</span>
                <el-date-picker
                  v-if="isEditingStartTime"
                  v-model="editableStartTime"
                  type="datetime"
                  placeholder="选择起始时间"
                  size="small"
                  :class="styles['start-time-picker']"
                  format="YYYY-MM-DD HH:mm"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  @change="updateStartTime"
                />
                <el-button
                  v-if="!isEditingStartTime"
                  type="primary"
                  size="small"
                  :class="styles['edit-button']"
                  @click="startEditingStartTime"
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <div v-if="isEditingStartTime" :class="styles['edit-actions']">
                  <el-button type="primary" size="small" @click="saveStartTime">保存</el-button>
                  <el-button size="small" @click="cancelEditingStartTime">取消</el-button>
                </div>
              </div>
            </div>
            
            <div :class="styles['hours-selector']">
              <div :class="styles['time-range-selector']">
                <div :class="styles['range-slider']">
                  <div :class="styles['slider-container']">
                    <el-slider
                      v-model="workLogForm.timeRange"
                      range
                      :min="0"
                      :max="Math.max(timeScale.length - 1, 1)"
                      :step="1"
                      :class="styles['range-slider']"
                      :show-tooltip="false"
                      :show-input="false"
                      :show-stops="false"
                      @change="updateActualHours"
                      v-if="timeScale.length > 0"
                    />
                    <!-- 游标时间显示 -->
                    <div :class="styles['cursor-times']">
                      <div :class="styles['cursor-time-start']" :style="getStartCursorStyle()">
                        <div :class="styles['cursor-time-label']">
                          {{ getStartTimeLabel() }}
                        </div>
                      </div>
                      <div :class="styles['cursor-time-end']" :style="getEndCursorStyle()">
                        <div :class="styles['cursor-time-label']">
                          {{ getEndTimeLabel() }}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div :class="styles['time-scale']">
                    <div v-for="(timePoint, index) in getDisplayTimeScale()" :key="index" :class="styles['scale-item']">
                      <span :class="styles['scale-label']">{{ timePoint.label }}</span>
                      <span :class="styles['scale-date']">{{ timePoint.date }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 快速工时选择 -->
            <div :class="styles['quick-hours-section']">
              <div :class="styles['quick-hours-label']">快速选择工时</div>
              <div :class="styles['quick-hours-tags']">
                <el-tag
                  v-for="hours in quickHoursOptions"
                  :key="hours"
                  :type="workLogForm.actualHours === hours ? 'success' : 'info'"
                  :effect="workLogForm.actualHours === hours ? 'light' : 'plain'"
                  :class="styles['quick-hours-tag']"
                  @click="selectQuickHours(hours)"
                >
                  {{ hours }}h
                </el-tag>
              </div>
            </div>
            
            <!-- 工作内容输入 -->
            <div :class="styles['work-content-section']">
              <el-input
                v-model="workLogForm.workContent"
                type="textarea"
                :rows="2"
                placeholder="工作内容描述（可选）"
                maxlength="500"
                show-word-limit
                size="small"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div :class="styles['drawer-footer']">
        <el-button @click="close">取消</el-button>
        <el-button
            v-if="task && currentTaskStatus === TaskStatus.COMPLETED"
            type="success"
            @click="completeTaskWithWorkLog"
            :loading="submitting"
            :disabled="workLogForm.actualHours <= 0"
        >
          完成任务
        </el-button>
        <el-button
            v-else-if="task"
            type="primary"
            @click="submit"
            :loading="submitting"
            :disabled="showAssigneeRequired"
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
import { ref, watch, computed, nextTick } from 'vue'
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
  targetStatus?: string // 拖拽时的目标状态
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  task: null,
  teams: () => [],
  projects: () => [],
  teamMembers: () => [],
  targetStatus: undefined
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

// 工作日志表单
const workLogForm = ref({
  timeRange: [0, 16] as [number, number], // [开始时间索引, 结束时间索引]
  startDateTime: '',
  endDateTime: '',
  actualHours: 8,
  workContent: ''
})

// 时间刻度（30分钟间隔，3天范围）
const timeScale = ref<Array<{label: string, date: string, datetime: Date}>>([])

// 起始时间编辑状态
const isEditingStartTime = ref(false)
const editableStartTime = ref('')

// 快速工时选择选项
const quickHoursOptions = [0.5, 1, 2, 4, 6, 8, 12, 16, 24]

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
  tags: '',
  started_at: '' as string
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
  if (newValue && props.task) {
    // 重置工时表单
    resetWorkLogForm()
  }
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
  // 如果当前没有负责人，直接分配
  if (!taskForm.value.assignee_id) {
    taskForm.value.assignee_id = member.user_id
  } else {
    // 如果已有负责人，需要确认重新分配
    if (await confirmSensitiveOperation('重新分配负责人')) {
      taskForm.value.assignee_id = member.user_id
    }
  }
}

// 重置工时表单
const resetWorkLogForm = () => {
  workLogForm.value = {
    timeRange: [0, 16],
    startDateTime: '',
    endDateTime: '',
    actualHours: 8,
    workContent: ''
  }
}

// 完成任务并创建工作日志
const completeTaskWithWorkLog = async () => {
  if (!props.task || workLogForm.value.actualHours <= 0) {
    ElMessage.warning('请先录入实际工时')
    return
  }
  
  try {
    submitting.value = true
    await taskApi.completeTask(
      props.task.id,
      workLogForm.value.actualHours,
      workLogForm.value.workContent || undefined
    )
    ElMessage.success('任务完成成功')
    emit('submit')
  } catch (error: any) {
    ElMessage.error('完成任务失败：' + (error.response?.data?.detail || '未知错误'))
  } finally {
    submitting.value = false
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

// 计算是否显示实际工时录入界面
const showActualHoursInput = computed(() => {
  // 当任务状态为已完成时显示实际工时录入界面
  return currentTaskStatus.value === TaskStatus.COMPLETED && props.task
})

// 计算是否显示负责人完善界面
const showAssigneeRequired = computed(() => {
  // 当任务状态为已分配或进行中，但没有负责人时显示负责人完善界面
  return (currentTaskStatus.value === TaskStatus.ASSIGNED || currentTaskStatus.value === TaskStatus.IN_PROGRESS) 
    && props.task 
    && !taskForm.value.assignee_id
})

// 监听任务状态变化，安全地初始化工作日志表单
watch(() => currentTaskStatus.value, (newStatus) => {
  if (newStatus === TaskStatus.COMPLETED && props.task) {
    // 使用nextTick确保DOM更新完成后再初始化
    nextTick(() => {
      setTimeout(() => {
        initializeWorkLogForm()
      }, 100)
    })
  }
})

// 监听targetStatus变化，设置任务状态为目标状态
watch(() => props.targetStatus, (targetStatus) => {
  if (targetStatus && props.task) {
    taskForm.value.status = targetStatus as TaskStatus
    
    // 如果目标状态是已完成，立即初始化工作日志表单
    if (targetStatus === TaskStatus.COMPLETED) {
      nextTick(() => {
        setTimeout(() => {
          initializeWorkLogForm()
          // 滚动到最下方，显示工时录入区域
          scrollToBottom()
        }, 100)
      })
    }
    // 如果目标状态是需要负责人的状态，滚动到负责人选择区域
    else if (targetStatus === TaskStatus.ASSIGNED || targetStatus === TaskStatus.IN_PROGRESS) {
      nextTick(() => {
        setTimeout(() => {
          // 滚动到负责人选择区域
          scrollToAssigneeSection()
        }, 100)
      })
    }
  }
}, { immediate: true })

// 移除复杂的watch监听，改为在模板中直接处理
// watch(currentTaskStatus, (newStatus, oldStatus) => {
//   if (newStatus === TaskStatus.COMPLETED && oldStatus !== TaskStatus.COMPLETED && props.task) {
//     setTimeout(() => {
//       try {
//         initializeWorkLogForm()
//       } catch (error) {
//         console.error('初始化工时表单失败:', error)
//         workLogForm.value.actualHours = props.task?.estimated_hours || 8
//         workLogForm.value.workContent = `完成任务：${props.task?.title || ''}`
//       }
//     }, 500)
//   }
// })

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

// 生成时间刻度（根据实际时间跨度，30分钟精度）
const generateTimeScale = (startDate: Date, endDate: Date) => {
  const scale: Array<{label: string, date: string, datetime: Date}> = []
  
  let current = new Date(startDate)
  current.setMinutes(Math.floor(current.getMinutes() / 30) * 30, 0, 0) // 对齐到30分钟
  
  // 确保结束时间也对齐到30分钟，并确保包含当前时间
  const alignedEndDate = new Date(endDate)
  alignedEndDate.setMinutes(Math.ceil(endDate.getMinutes() / 30) * 30, 0, 0)
  
  // 获取当前时间并对齐到30分钟
  const now = new Date()
  const alignedNow = new Date(now)
  alignedNow.setMinutes(Math.ceil(now.getMinutes() / 30) * 30, 0, 0)
  
  // 如果当前时间晚于对齐的结束时间，更新结束时间
  if (alignedNow > alignedEndDate) {
    alignedEndDate.setTime(alignedNow.getTime())
  }
  
  while (current <= alignedEndDate && scale.length < 200) { // 限制最大长度，保持30分钟精度
    const timeStr = current.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    })
    const dateStr = current.toLocaleDateString('zh-CN', { 
      month: '2-digit', 
      day: '2-digit' 
    })
    
    scale.push({
      label: timeStr,
      date: dateStr,
      datetime: new Date(current)
    })
    
    current.setMinutes(current.getMinutes() + 30)
  }
  
  return scale
}

// 获取要显示的时间轴刻度（根据实际跨度动态计算4个刻度）
const getDisplayTimeScale = () => {
  if (timeScale.value.length === 0) return []
  
  const totalPoints = timeScale.value.length
  
  // 如果刻度点少于等于4个，直接返回所有点
  if (totalPoints <= 4) {
    return timeScale.value
  }
  
  // 计算4个均匀分布的时间点，确保包含最后一个点
  const displayPoints = []
  
  // 总是包含第一个点
  displayPoints.push(timeScale.value[0])
  
  // 计算中间2个点
  const step = (totalPoints - 1) / 3 // 分成3段，4个点
  for (let i = 1; i < 3; i++) {
    const index = Math.round(i * step)
    displayPoints.push(timeScale.value[index])
  }
  
  // 总是包含最后一个点
  displayPoints.push(timeScale.value[totalPoints - 1])
  
  return displayPoints
}

// 更新时间范围（从滑块）
const updateActualHours = (value: [number, number]) => {
  const maxIndex = Math.max(timeScale.value.length - 1, 1)
  const safeValue: [number, number] = [
    Math.max(0, Math.min(value[0], maxIndex)),
    Math.max(0, Math.min(value[1], maxIndex))
  ]
  
  workLogForm.value.timeRange = safeValue
  const startTime = timeScale.value[safeValue[0]]
  const endTime = timeScale.value[safeValue[1]]
  
  if (startTime && endTime) {
    workLogForm.value.startDateTime = startTime.datetime.toISOString().slice(0, 19).replace('T', ' ')
    workLogForm.value.endDateTime = endTime.datetime.toISOString().slice(0, 19).replace('T', ' ')
    
    // 计算实际工时
    const diffMs = endTime.datetime.getTime() - startTime.datetime.getTime()
    workLogForm.value.actualHours = diffMs / (1000 * 60 * 60)
  }
}

// 更新时间范围（从日期时间选择器）
const updateTimeRangeFromDateTime = () => {
  if (!workLogForm.value.startDateTime || !workLogForm.value.endDateTime) return
  
  const startDate = new Date(workLogForm.value.startDateTime)
  const endDate = new Date(workLogForm.value.endDateTime)
  
  // 找到最接近的时间刻度索引
  const startIndex = timeScale.value.findIndex(point => 
    Math.abs(point.datetime.getTime() - startDate.getTime()) < 15 * 60 * 1000 // 15分钟内
  )
  const endIndex = timeScale.value.findIndex(point => 
    Math.abs(point.datetime.getTime() - endDate.getTime()) < 15 * 60 * 1000 // 15分钟内
  )
  
  if (startIndex >= 0 && endIndex >= 0 && startIndex < endIndex) {
    workLogForm.value.timeRange = [startIndex, endIndex]
    
    // 计算实际工时
    const diffMs = endDate.getTime() - startDate.getTime()
    workLogForm.value.actualHours = diffMs / (1000 * 60 * 60)
  }
}

// 获取开始时间标签
const getStartTimeLabel = () => {
  if (timeScale.value.length === 0) {
    // 如果没有时间刻度，使用任务开始时间作为默认值
    if (props.task?.started_at) {
      const taskStart = new Date(props.task.started_at)
      const timeStr = taskStart.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
      const dateStr = taskStart.toLocaleDateString('zh-CN', { 
        month: '2-digit', 
        day: '2-digit' 
      })
      return `${timeStr}\n${dateStr}`
    }
    return '09:00\n12/25'
  }
  const startIndex = workLogForm.value.timeRange[0]
  const timePoint = timeScale.value[startIndex]
  if (timePoint) {
    return `${timePoint.label}\n${timePoint.date}`
  }
  return '09:00\n12/25'
}

// 获取结束时间标签
const getEndTimeLabel = () => {
  if (timeScale.value.length === 0) {
    // 如果没有时间刻度，使用当前时间作为默认值
    const now = new Date()
    const timeStr = now.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    })
    const dateStr = now.toLocaleDateString('zh-CN', { 
      month: '2-digit', 
      day: '2-digit' 
    })
    return `${timeStr}\n${dateStr}`
  }
  const endIndex = workLogForm.value.timeRange[1]
  const timePoint = timeScale.value[endIndex]
  if (timePoint) {
    return `${timePoint.label}\n${timePoint.date}`
  }
  return '17:00\n12/25'
}

// 计算开始游标位置样式
const getStartCursorStyle = () => {
  if (timeScale.value.length === 0) return { left: '0%' }
  const maxIndex = Math.max(timeScale.value.length - 1, 1)
  const percentage = (workLogForm.value.timeRange[0] / maxIndex) * 100
  return { left: `${percentage}%` }
}

// 计算结束游标位置样式
const getEndCursorStyle = () => {
  if (timeScale.value.length === 0) return { left: '100%' }
  const maxIndex = Math.max(timeScale.value.length - 1, 1)
  const percentage = (workLogForm.value.timeRange[1] / maxIndex) * 100
  return { left: `${percentage}%` }
}

// 初始化工作日志表单
const initializeWorkLogForm = () => {
  if (!props.task) return
  
  const estimatedHours = props.task.estimated_hours || 8
  workLogForm.value.actualHours = estimatedHours
  workLogForm.value.workContent = `完成任务：${props.task.title}`
  
  // 使用任务的开始时间作为时间轴起始点，当前时间作为结束点
  const taskStartTime = getTaskStartTime()
  const taskStartDate = taskStartTime ? new Date(taskStartTime) : new Date()
  const now = new Date()
  
  // 结束时间总是当前时间，确保时间轴包含到当前时间
  const endDate = now
  
  console.log('初始化工作日志表单:', {
    taskStartTime,
    taskStartDate: taskStartDate.toISOString(),
    endDate: endDate.toISOString(),
    now: now.toISOString()
  })
  
  timeScale.value = generateTimeScale(taskStartDate, endDate)
  
  console.log('生成的时间轴:', {
    length: timeScale.value.length,
    first: timeScale.value[0]?.datetime.toISOString(),
    last: timeScale.value[timeScale.value.length - 1]?.datetime.toISOString()
  })
  
  // 设置默认时间范围（从起始时间到当前时间）
  const startTime = getTaskStartTime()
  const startDate = startTime ? new Date(startTime) : new Date()
  
  // 找到最接近当前时间的刻度索引
  let endIndex = timeScale.value.length - 1
  let closestIndex = 0
  let minDiff = Infinity
  
  for (let i = 0; i < timeScale.value.length; i++) {
    const timePoint = timeScale.value[i]
    const diff = Math.abs(timePoint.datetime.getTime() - now.getTime())
    
    if (diff < minDiff) {
      minDiff = diff
      closestIndex = i
    }
    
    // 如果当前时间点不晚于当前时间，也记录这个索引
    if (timePoint.datetime.getTime() <= now.getTime()) {
      endIndex = i
    }
  }
  
  // 使用最接近当前时间的索引，但不超过当前时间
  endIndex = Math.min(closestIndex, endIndex)
  
  workLogForm.value.timeRange = [0, endIndex]
  
  // 设置默认日期时间
  if (timeScale.value.length > 0) {
    workLogForm.value.startDateTime = timeScale.value[0].datetime.toISOString().slice(0, 19).replace('T', ' ')
    workLogForm.value.endDateTime = timeScale.value[endIndex].datetime.toISOString().slice(0, 19).replace('T', ' ')
  }
}

// 获取任务起始时间（优先使用taskForm.started_at，否则使用props.task的数据）
const getTaskStartTime = () => {
  if (!props.task) return ''
  
  // 优先使用taskForm中的started_at（用户编辑后的值）
  if (taskForm.value.started_at) {
    return taskForm.value.started_at
  }
  
  // 否则使用props.task中的started_at或created_at
  const startTime = props.task.started_at || props.task.created_at
  return startTime || ''
}

// 开始编辑起始时间
const startEditingStartTime = () => {
  const currentStartTime = getTaskStartTime()
  editableStartTime.value = currentStartTime
  isEditingStartTime.value = true
}

// 取消编辑起始时间
const cancelEditingStartTime = () => {
  isEditingStartTime.value = false
  editableStartTime.value = ''
}

// 保存起始时间
const saveStartTime = () => {
  if (editableStartTime.value) {
    // 更新任务表单中的started_at字段
    taskForm.value.started_at = editableStartTime.value
    
    // 重新生成时间轴（使用实际时间跨度）
    const taskStartDate = new Date(editableStartTime.value)
    const now = new Date()
    
    // 结束时间总是当前时间，确保时间轴包含到当前时间
    const endDate = now
    
    timeScale.value = generateTimeScale(taskStartDate, endDate)
    
    // 重置时间范围（从新的起始时间到当前时间）
    let endIndex = timeScale.value.length - 1
    let closestIndex = 0
    let minDiff = Infinity
    
    for (let i = 0; i < timeScale.value.length; i++) {
      const timePoint = timeScale.value[i]
      const diff = Math.abs(timePoint.datetime.getTime() - now.getTime())
      
      if (diff < minDiff) {
        minDiff = diff
        closestIndex = i
      }
      
      // 如果当前时间点不晚于当前时间，也记录这个索引
      if (timePoint.datetime.getTime() <= now.getTime()) {
        endIndex = i
      }
    }
    
    // 使用最接近当前时间的索引，但不超过当前时间
    endIndex = Math.min(closestIndex, endIndex)
    
    workLogForm.value.timeRange = [0, endIndex]
    
    // 更新默认日期时间
    if (timeScale.value.length > 0) {
      workLogForm.value.startDateTime = timeScale.value[0].datetime.toISOString().slice(0, 19).replace('T', ' ')
      workLogForm.value.endDateTime = timeScale.value[endIndex].datetime.toISOString().slice(0, 19).replace('T', ' ')
    }
    
    isEditingStartTime.value = false
    ElMessage.success('起始时间已更新')
  }
}

// 更新起始时间（实时更新）
const updateStartTime = () => {
  if (editableStartTime.value) {
    // 实时更新任务表单
    taskForm.value.started_at = editableStartTime.value
  }
}

// 格式化任务起始时间
const formatTaskStartTime = (startedAt: string) => {
  if (!startedAt) return '未设置'
  
  const date = new Date(startedAt)
  const timeStr = date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  })
  const dateStr = date.toLocaleDateString('zh-CN', { 
    year: 'numeric',
    month: '2-digit', 
    day: '2-digit' 
  })
  
  return `${dateStr} ${timeStr}`
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

// 滚动到抽屉底部
const scrollToBottom = () => {
  nextTick(() => {
    // 查找抽屉的滚动容器
    const drawer = document.querySelector('.el-drawer__body')
    if (drawer) {
      drawer.scrollTop = drawer.scrollHeight
    }
  })
}

// 滚动到负责人选择区域
const scrollToAssigneeSection = () => {
  nextTick(() => {
    // 查找负责人选择区域
    const assigneeSection = document.querySelector('[data-field="assignee_id"]')
    if (assigneeSection) {
      assigneeSection.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

// 选择快速工时
const selectQuickHours = (hours: number) => {
  workLogForm.value.actualHours = hours
  
  // 根据工时调整时间轴范围
  if (timeScale.value.length > 0) {
    const startIndex = workLogForm.value.timeRange[0]
    const endIndex = Math.min(startIndex + Math.round(hours * 2), timeScale.value.length - 1) // 每小时2个30分钟刻度
    
    workLogForm.value.timeRange = [startIndex, endIndex]
    
    // 更新时间范围
    const startTime = timeScale.value[startIndex]
    const endTime = timeScale.value[endIndex]
    
    if (startTime && endTime) {
      workLogForm.value.startDateTime = startTime.datetime.toISOString().slice(0, 19).replace('T', ' ')
      workLogForm.value.endDateTime = endTime.datetime.toISOString().slice(0, 19).replace('T', ' ')
    }
  }
}
</script> 
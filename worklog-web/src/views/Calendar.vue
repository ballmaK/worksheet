<template>
  <div class="calendar-container">
    <div class="header">
      <h1>工作日志日历</h1>
      <div class="actions">
        <div class="display-controls">
          <el-checkbox v-model="showWorkLogs" label="显示工作日志" />
          <el-checkbox v-model="showTasks" label="显示任务" />
        </div>
        <el-button type="primary" @click="goToTeamView" v-if="currentTeam">
          团队视图
        </el-button>
      </div>
    </div>
    <Qalendar
      v-model="selectedDate"
      :events="events"
      :config="config"
      @event-click="onEventClick"
      @day-click="onDayClick"
      @interval-was-clicked="onIntervalClick"
      @mode-change="onModeChange"
      @updated-period="onPeriodChange"
      @event-was-updated="onEventUpdated"
      @event-was-dragged="onEventDragged"
      @event-was-resized="onEventResized"
    />
    
    <!-- 工作日志表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑工作日志' : '记录工作日志'" width="600px">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入工作标题" />
        </el-form-item>
        <el-form-item label="工作类型" prop="work_type">
          <el-select v-model="form.work_type" placeholder="请选择工作类型">
            <el-option label="功能开发" value="feature" />
            <el-option label="Bug修复" value="bug" />
            <el-option label="改进优化" value="improvement" />
            <el-option label="文档工作" value="documentation" />
            <el-option label="会议" value="meeting" />
            <el-option label="调研" value="research" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入工作内容"
          />
        </el-form-item>
        <el-form-item label="时间范围" prop="start_time">
          <div class="time-range-picker">
            <el-date-picker
              v-model="form.start_time"
              type="datetime"
              placeholder="开始时间"
              format="YYYY-MM-DD HH:mm"
              :default-time="new Date(2000, 1, 1, 9, 0, 0)"
              :disabled-date="disabledDate"
              :disabled-hours="disabledHours"
              style="width: 200px; margin-right: 10px;"
            />
            <span class="separator">至</span>
            <el-date-picker
              v-model="form.end_time"
              type="datetime"
              placeholder="结束时间"
              format="YYYY-MM-DD HH:mm"
              :default-time="new Date(2000, 1, 1, 18, 0, 0)"
              :disabled-date="disabledDate"
              :disabled-hours="disabledHours"
              style="width: 200px;"
            />
          </div>
        </el-form-item>
        <el-form-item label="所属团队" prop="team_id">
          <el-select
            v-model="form.team_id"
            placeholder="请选择团队"
            @change="handleTeamChange"
          >
            <el-option
              v-for="team in teams"
              :key="team.id"
              :label="team.name"
              :value="team.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属项目" prop="project_id">
          <el-select
            v-model="form.project_id"
            placeholder="请选择项目"
            :disabled="!form.team_id"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 工作日志详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="工作日志详情"
      width="600px"
    >
      <div v-if="currentWorkLog" class="worklog-detail">
        <h3>{{ currentWorkLog.title }}</h3>
        <p class="time-range">
          {{ formatDateTime(currentWorkLog.start_time) }} 至
          {{ formatDateTime(currentWorkLog.end_time) }}
        </p>
        <p class="content">{{ currentWorkLog.content }}</p>
        <div class="meta">
          <el-tag size="small">团队：{{ currentWorkLog.team_name }}</el-tag>
          <el-tag size="small" type="success" v-if="currentWorkLog.project_name">
            项目：{{ currentWorkLog.project_name }}
          </el-tag>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="editWorkLog">编辑</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 任务详情弹窗 -->
    <el-dialog
      v-model="taskDetailDialogVisible"
      title="任务详情"
      width="600px"
    >
      <div v-if="currentTask" class="task-detail">
        <h3>{{ currentTask.title }}</h3>
        <div class="task-meta">
          <el-tag :type="getTaskStatusType(currentTask.status)" size="small">
            {{ getTaskStatusText(currentTask.status) }}
          </el-tag>
          <el-tag :type="getTaskPriorityType(currentTask.priority)" size="small">
            {{ getTaskPriorityText(currentTask.priority) }}
          </el-tag>
          <el-tag type="info" size="small" v-if="currentTask.task_type">
            {{ getTaskTypeText(currentTask.task_type) }}
          </el-tag>
        </div>
        <p class="description" v-if="currentTask.description">{{ currentTask.description }}</p>
        <div class="task-info">
          <p><strong>创建时间：</strong>{{ formatDateTime(currentTask.created_at) }}</p>
          <p v-if="currentTask.due_date"><strong>截止时间：</strong>{{ formatDateTime(currentTask.due_date) }}</p>
          <p v-if="currentTask.assignee"><strong>负责人：</strong>{{ currentTask.assignee.username }}</p>
          <p v-if="currentTask.estimated_hours"><strong>预估工时：</strong>{{ currentTask.estimated_hours }}小时</p>
          <p v-if="currentTask.actual_hours"><strong>实际工时：</strong>{{ currentTask.actual_hours }}小时</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="taskDetailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="goToTaskManagement">查看任务管理</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { workLogApi, type WorkLog, type WorkLogCreate } from '@/api/workLog'
import { teamApi, type Team } from '@/api/team'
import { projectApi, type Project } from '@/api/project'
import { taskApi, type Task } from '@/api/task'
import { Qalendar } from 'qalendar'
import 'qalendar/dist/style.css'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage as ElementPlusElMessage } from 'element-plus'

const selectedDate = ref(new Date())
const worklogs = ref<WorkLog[]>([])
const tasks = ref<Task[]>([])
const teams = ref<Team[]>([])
const projects = ref<Project[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const taskDetailDialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentWorkLog = ref<WorkLog | null>(null)
const currentTask = ref<Task | null>(null)
const formRef = ref<FormInstance>()
const router = useRouter()
const route = useRoute()
const currentTeam = ref<number | null>(null)
const showTasks = ref(true) // 控制是否显示任务
const showWorkLogs = ref(true) // 控制是否显示工作日志

const defaultTime = [
  new Date(2000, 1, 1, 9, 0, 0),  // 默认开始时间 9:00
  new Date(2000, 1, 1, 18, 0, 0)  // 默认结束时间 18:00
]

const form = reactive<Omit<WorkLogCreate, 'start_time' | 'end_time'> & { 
  start_time: Date | null;
  end_time: Date | null;
}>({
  title: '',
  work_type: 'feature',
  content: '',
  start_time: null,
  end_time: null,
  team_id: undefined,
  project_id: undefined
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  work_type: [{ required: true, message: '请选择工作类型', trigger: 'change' }],
  team_id: [{ required: true, message: '请选择团队', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

// Qalendar 配置
const config = {
  locale: 'zh-CN',
  defaultMode: 'week',
  week: {
    nDays: 7,
    startsToday: true,
    scrollToHour: 8
  },
  dayIntervals: {
    length: 30,
    height: 50,
    displayClickableInterval: true
  },
  style: {
    colorSchemes: {
      // 工作日志颜色方案
      feature: {
        color: '#ffffff',
        backgroundColor: '#409EFF',
        borderColor: '#409EFF'
      },
      bug: {
        color: '#ffffff',
        backgroundColor: '#F56C6C',
        borderColor: '#F56C6C'
      },
      improvement: {
        color: '#ffffff',
        backgroundColor: '#67C23A',
        borderColor: '#67C23A'
      },
      documentation: {
        color: '#ffffff',
        backgroundColor: '#E6A23C',
        borderColor: '#E6A23C'
      },
      meeting: {
        color: '#ffffff',
        backgroundColor: '#909399',
        borderColor: '#909399'
      },
      research: {
        color: '#ffffff',
        backgroundColor: '#9C27B0',
        borderColor: '#9C27B0'
      },
      other: {
        color: '#ffffff',
        backgroundColor: '#607D8B',
        borderColor: '#607D8B'
      },
      // 任务状态颜色方案
      'task-pending-priority-low': {
        color: '#ffffff',
        backgroundColor: '#E4E7ED',
        borderColor: '#E4E7ED'
      },
      'task-pending-priority-medium': {
        color: '#ffffff',
        backgroundColor: '#F0F9FF',
        borderColor: '#409EFF'
      },
      'task-pending-priority-high': {
        color: '#ffffff',
        backgroundColor: '#FFF7E6',
        borderColor: '#E6A23C'
      },
      'task-pending-priority-urgent': {
        color: '#ffffff',
        backgroundColor: '#FEF0F0',
        borderColor: '#F56C6C'
      },
      'task-assigned-priority-low': {
        color: '#ffffff',
        backgroundColor: '#E1F3D8',
        borderColor: '#67C23A'
      },
      'task-assigned-priority-medium': {
        color: '#ffffff',
        backgroundColor: '#E1F3D8',
        borderColor: '#67C23A'
      },
      'task-assigned-priority-high': {
        color: '#ffffff',
        backgroundColor: '#E1F3D8',
        borderColor: '#67C23A'
      },
      'task-assigned-priority-urgent': {
        color: '#ffffff',
        backgroundColor: '#E1F3D8',
        borderColor: '#67C23A'
      },
      'task-progress-priority-low': {
        color: '#ffffff',
        backgroundColor: '#409EFF',
        borderColor: '#409EFF'
      },
      'task-progress-priority-medium': {
        color: '#ffffff',
        backgroundColor: '#409EFF',
        borderColor: '#409EFF'
      },
      'task-progress-priority-high': {
        color: '#ffffff',
        backgroundColor: '#E6A23C',
        borderColor: '#E6A23C'
      },
      'task-progress-priority-urgent': {
        color: '#ffffff',
        backgroundColor: '#F56C6C',
        borderColor: '#F56C6C'
      },
      'task-review-priority-low': {
        color: '#ffffff',
        backgroundColor: '#9C27B0',
        borderColor: '#9C27B0'
      },
      'task-review-priority-medium': {
        color: '#ffffff',
        backgroundColor: '#9C27B0',
        borderColor: '#9C27B0'
      },
      'task-review-priority-high': {
        color: '#ffffff',
        backgroundColor: '#9C27B0',
        borderColor: '#9C27B0'
      },
      'task-review-priority-urgent': {
        color: '#ffffff',
        backgroundColor: '#9C27B0',
        borderColor: '#9C27B0'
      },
      'task-completed-priority-low': {
        color: '#ffffff',
        backgroundColor: '#67C23A',
        borderColor: '#67C23A'
      },
      'task-completed-priority-medium': {
        color: '#ffffff',
        backgroundColor: '#67C23A',
        borderColor: '#67C23A'
      },
      'task-completed-priority-high': {
        color: '#ffffff',
        backgroundColor: '#67C23A',
        borderColor: '#67C23A'
      },
      'task-completed-priority-urgent': {
        color: '#ffffff',
        backgroundColor: '#67C23A',
        borderColor: '#67C23A'
      },
      'task-cancelled-priority-low': {
        color: '#ffffff',
        backgroundColor: '#909399',
        borderColor: '#909399'
      },
      'task-cancelled-priority-medium': {
        color: '#ffffff',
        backgroundColor: '#909399',
        borderColor: '#909399'
      },
      'task-cancelled-priority-high': {
        color: '#ffffff',
        backgroundColor: '#909399',
        borderColor: '#909399'
      },
      'task-cancelled-priority-urgent': {
        color: '#ffffff',
        backgroundColor: '#909399',
        borderColor: '#909399'
      }
    }
  }
}

// 获取工作日志列表
const fetchWorkLogs = async () => {
  try {
    loading.value = true
    console.log('【fetchWorkLogs】开始获取工作日志...')
    
    // 计算时间范围
    const startDate = new Date(selectedDate.value)
    startDate.setDate(startDate.getDate() - 7) // 获取前7天
    const endDate = new Date(selectedDate.value)
    endDate.setDate(endDate.getDate() + 7) // 获取后7天
    
    const params = {
      page: 1,
      page_size: 100, // 获取更多数据
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    }
    
    console.log('【fetchWorkLogs】请求参数:', params)
    const response = await workLogApi.getWorkLogs(params)
    console.log('【fetchWorkLogs】API响应:', response)
    console.log('【fetchWorkLogs】响应类型:', typeof response)
    console.log('【fetchWorkLogs】响应结构:', JSON.stringify(response, null, 2))
    
    // 简化响应处理逻辑
    let workLogData: any[] = []
    
    if (response && typeof response === 'object') {
      const responseData = response as any
      if (responseData.data) {
        if (responseData.data.items && Array.isArray(responseData.data.items)) {
          workLogData = responseData.data.items
        } else if (Array.isArray(responseData.data)) {
          workLogData = responseData.data
        }
      } else if (responseData.items && Array.isArray(responseData.items)) {
        workLogData = responseData.items
      } else if (Array.isArray(responseData)) {
        workLogData = responseData
      }
    }
    
    console.log('【fetchWorkLogs】解析后的工作日志数据:', workLogData)
    console.log('【fetchWorkLogs】工作日志数量:', workLogData.length)
    worklogs.value = workLogData
    
    console.log('【fetchWorkLogs】最终工作日志数据:', worklogs.value)
  } catch (error: any) {
    console.error('【fetchWorkLogs】获取工作日志失败:', error)
    ElementPlusElMessage.error(error.response?.data?.message || '获取工作日志失败')
    worklogs.value = []
  } finally {
    loading.value = false
  }
}

// 获取任务列表
const fetchTasks = async () => {
  try {
    console.log('【fetchTasks】开始获取任务...')
    
    const params = {
      page: 1,
      page_size: 100
    }
    
    console.log('【fetchTasks】请求参数:', params)
    const response = await taskApi.getTasks(params)
    console.log('【fetchTasks】API响应:', response)
    console.log('【fetchTasks】响应类型:', typeof response)
    console.log('【fetchTasks】响应结构:', JSON.stringify(response, null, 2))
    
    // 简化响应处理逻辑
    let taskData: any[] = []
    
    if (response && typeof response === 'object') {
      const responseData = response as any
      if (responseData.data) {
        if (responseData.data.items && Array.isArray(responseData.data.items)) {
          taskData = responseData.data.items
        } else if (Array.isArray(responseData.data)) {
          taskData = responseData.data
        }
      } else if (responseData.items && Array.isArray(responseData.items)) {
        taskData = responseData.items
      } else if (Array.isArray(responseData)) {
        taskData = responseData
      }
    }
    
    console.log('【fetchTasks】解析后的任务数据:', taskData)
    console.log('【fetchTasks】任务数量:', taskData.length)
    tasks.value = taskData
  } catch (error: any) {
    console.error('【fetchTasks】获取任务失败:', error)
    ElementPlusElMessage.error(error.response?.data?.message || '获取任务失败')
    tasks.value = []
  }
}

// 添加 formatDate 函数
function formatDate(date: Date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}`
}

// 修复日期解析函数
function parseDate(dateString: string): Date {
  // 处理不完整的ISO格式（缺少时区信息）
  if (dateString && !dateString.includes('Z') && !dateString.includes('+')) {
    // 添加本地时区信息
    dateString = dateString + 'Z'
  }
  return new Date(dateString)
}

// 修改 events 计算属性
const events = computed(() => {
  console.log('【events computed】开始计算事件...')
  console.log('【events computed】showWorkLogs:', showWorkLogs.value)
  console.log('【events computed】worklogs:', worklogs.value)
  console.log('【events computed】showTasks:', showTasks.value)
  console.log('【events computed】tasks:', tasks.value)
  
  const allEvents = []
  
  // 添加工作日志事件
  if (showWorkLogs.value && worklogs.value && worklogs.value.length > 0) {
    console.log('【events computed】处理工作日志事件，数量:', worklogs.value.length)
    
    const worklogEvents = worklogs.value.map((worklog: any) => {
      try {
        console.log('【events computed】处理工作日志:', worklog)
        console.log('【events computed】工作日志时间:', {
          start_time: worklog.start_time,
          end_time: worklog.end_time
        })
        
        const startDate = parseDate(worklog.start_time)
        const endDate = parseDate(worklog.end_time)
        
        console.log('【events computed】解析后的时间:', {
          startDate: startDate.toISOString(),
          endDate: endDate.toISOString(),
          startValid: !isNaN(startDate.getTime()),
          endValid: !isNaN(endDate.getTime())
        })
        
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
          console.error('【events computed】无效的工作日志日期:', worklog)
          return null
        }
        
        const event = {
          id: `worklog_${worklog.id}`,
          title: worklog.title || worklog.description || `工作日志 #${worklog.id}`,
          time: {
            start: formatDate(startDate),
            end: formatDate(endDate)
          },
          colorScheme: getWorkTypeColor(worklog.work_type),
          isEditable: true,
          description: worklog.content || worklog.description || '',
          disableDnD: [], // 允许在所有模式下拖拽
          disableResize: [], // 允许在所有模式下调整大小
          type: 'worklog',
          data: worklog
        }
        
        console.log('【events computed】转换后的工作日志事件:', event)
        return event
      } catch (error) {
        console.error('【events computed】转换工作日志事件时出错:', error, worklog)
        return null
      }
    }).filter(Boolean)
    
    console.log('【events computed】有效的工作日志事件数量:', worklogEvents.length)
    allEvents.push(...worklogEvents)
  }
  
  // 添加任务事件
  if (showTasks.value && tasks.value && tasks.value.length > 0) {
    console.log('【events computed】处理任务事件，数量:', tasks.value.length)
    
    const taskEvents = tasks.value.map((task: any) => {
      try {
        // 根据任务状态和截止日期创建事件
        const createdDate = new Date(task.created_at)
        const dueDate = task.due_date ? new Date(task.due_date) : null
        
        if (isNaN(createdDate.getTime())) {
          console.error('【events computed】无效的任务创建日期:', task)
          return null
        }
        
        // 如果任务有截止日期，使用截止日期；否则使用创建日期
        const eventDate = dueDate && !isNaN(dueDate.getTime()) ? dueDate : createdDate
        const endDate = new Date(eventDate)
        endDate.setHours(endDate.getHours() + 1) // 任务默认显示1小时
        
        const event = {
          id: `task_${task.id}`,
          title: `📋 ${task.title}`,
          time: {
            start: formatDate(eventDate),
            end: formatDate(endDate)
          },
          colorScheme: getTaskStatusColor(task.status, task.priority),
          isEditable: false, // 任务不可直接编辑
          description: task.description || '',
          disableDnD: [], // 允许拖拽
          disableResize: [], // 允许调整大小
          type: 'task',
          data: task
        }
        
        console.log('【events computed】转换后的任务事件:', event)
        return event
      } catch (error) {
        console.error('【events computed】转换任务事件时出错:', error)
        return null
      }
    }).filter(Boolean)
    
    console.log('【events computed】有效的任务事件数量:', taskEvents.length)
    allEvents.push(...taskEvents)
  }
  
  console.log('【events computed】最终事件列表:', allEvents)
  console.log('【events computed】最终事件数量:', allEvents.length)
  return allEvents
})

// 监听日期变化，自动获取对应时间段的工作日志
watch(selectedDate, (newDate) => {
  console.log('【watch selectedDate】日期变化:', newDate)
  fetchWorkLogs()
  fetchTasks()
}, { immediate: true })

// 监听时间段变化
const onPeriodChange = (period: { start: Date; end: Date }) => {
  console.log('【onPeriodChange】时间范围改变:', period)
  // 更新选中的日期，但不立即获取数据
  selectedDate.value = period.start
}

// 获取工作类型对应的颜色方案
const getWorkTypeColor = (type: string) => {
  return type // 直接返回类型名称作为颜色方案
}

// 获取任务状态对应的颜色方案
const getTaskStatusColor = (status: string, priority: string) => {
  // 根据状态和优先级组合返回颜色方案
  const statusColors: { [key: string]: string } = {
    'pending': 'task-pending',
    'assigned': 'task-assigned', 
    'in_progress': 'task-progress',
    'review': 'task-review',
    'completed': 'task-completed',
    'cancelled': 'task-cancelled'
  }
  
  const priorityColors: { [key: string]: string } = {
    'low': 'priority-low',
    'medium': 'priority-medium',
    'high': 'priority-high',
    'urgent': 'priority-urgent'
  }
  
  return `${statusColors[status] || 'task-default'}-${priorityColors[priority] || 'priority-medium'}`
}

// 事件点击处理
const onEventClick = (event: any) => {
  console.log('【onEventClick】事件被点击:', event)
  
  if (event.type === 'task') {
    // 处理任务点击
    const task = tasks.value.find((t: any) => t.id === parseInt(event.id.replace('task_', '')))
    if (task) {
      currentTask.value = task
      showTaskDetail()
    }
  } else {
    // 处理工作日志点击
    const worklog = worklogs.value.find((w: any) => String(w.id) === event.id)
    if (worklog) {
      currentWorkLog.value = worklog
      detailDialogVisible.value = true
    }
  }
}

// 显示任务详情
const showTaskDetail = () => {
  if (currentTask.value) {
    taskDetailDialogVisible.value = true
  }
}

// 获取任务状态类型
const getTaskStatusType = (status: string) => {
  const statusTypes: { [key: string]: string } = {
    'pending': 'info',
    'assigned': 'warning',
    'in_progress': 'primary',
    'review': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusTypes[status] || 'info'
}

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const statusTexts: { [key: string]: string } = {
    'pending': '待分派',
    'assigned': '已分派',
    'in_progress': '进行中',
    'review': '审核中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusTexts[status] || status
}

// 获取任务优先级类型
const getTaskPriorityType = (priority: string) => {
  const priorityTypes: { [key: string]: string } = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger',
    'urgent': 'danger'
  }
  return priorityTypes[priority] || 'info'
}

// 获取任务优先级文本
const getTaskPriorityText = (priority: string) => {
  const priorityTexts: { [key: string]: string } = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'urgent': '紧急'
  }
  return priorityTexts[priority] || priority
}

// 获取任务类型文本
const getTaskTypeText = (type: string) => {
  const typeTexts: { [key: string]: string } = {
    'feature': '功能开发',
    'bug': 'Bug修复',
    'improvement': '改进优化',
    'documentation': '文档工作',
    'other': '其他'
  }
  return typeTexts[type] || type
}

// 跳转到任务管理页面
const goToTaskManagement = () => {
  router.push('/task-management')
}

// 时间段点击处理
const onIntervalClick = (payload: { intervalStart: string; intervalEnd: string }) => {
  console.log('【onIntervalClick】时间段被点击:', payload)
  
  // 重置表单
  form.title = ''
  form.content = ''
  form.work_type = 'dev'
  form.team_id = undefined
  form.project_id = undefined
  
  // 设置时间范围
  form.start_time = new Date(payload.intervalStart)
  form.end_time = new Date(payload.intervalEnd)
  console.log('Form times set to:', { 
    start: form.start_time?.toLocaleString(), 
    end: form.end_time?.toLocaleString() 
  })
  
  // 显示弹窗
  isEdit.value = false
  dialogVisible.value = true
}

// 日期点击处理
const onDayClick = (payload: { date: Date }) => {
  console.log('【onDayClick】日期被点击:', payload)
  const date = payload.date
  
  // 重置表单
  form.title = ''
  form.content = ''
  form.work_type = 'dev'
  form.team_id = undefined
  form.project_id = undefined
  
  // 设置时间范围为当天的 9:00-18:00
  const startDate = new Date(date)
  startDate.setHours(9, 0, 0, 0)
  const endDate = new Date(date)
  endDate.setHours(18, 0, 0, 0)
  
  form.start_time = startDate
  form.end_time = endDate
  
  // 显示弹窗
  isEdit.value = false
  dialogVisible.value = true
}

const onModeChange = (mode: string) => {
  console.log('【onModeChange】视图模式改变:', mode)
}

// 编辑工作日志
const editWorkLog = () => {
  if (!currentWorkLog.value) return
  
  // 设置表单数据
  form.title = currentWorkLog.value.title || ''
  form.content = currentWorkLog.value.content || ''
  form.work_type = currentWorkLog.value.work_type || 'dev'
  form.team_id = currentWorkLog.value.team_id
  form.project_id = currentWorkLog.value.project_id
  form.start_time = new Date(currentWorkLog.value.start_time)
  form.end_time = new Date(currentWorkLog.value.end_time)
  
  // 显示编辑弹窗
  isEdit.value = true
  dialogVisible.value = true
  detailDialogVisible.value = false
}

// 团队/项目
const handleTeamChange = async (teamId: number) => {
  form.project_id = undefined
  if (teamId) {
    await fetchProjects(teamId)
  } else {
    projects.value = []
  }
}

// 重置表单
const resetForm = () => {
  form.title = ''
  form.content = ''
  form.work_type = 'dev'
  form.team_id = undefined
  form.project_id = undefined
  form.start_time = null
  form.end_time = null
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        // 创建新的日期对象并设置时区
        const startTime = new Date(form.start_time!)
        
        // 转换为本地时间
        const localStartTime = new Date(startTime.getTime() - (startTime.getTimezoneOffset() * 60000))
        
        const workLogData: WorkLogCreate = {
          title: form.title,
          work_type: form.work_type,
          content: form.content,
          start_time: localStartTime.toISOString(),
          team_id: form.team_id as number,
          project_id: form.project_id
        }
        
        // 只有在明确设置了结束时间时才包含
        if (form.end_time) {
          const endTime = new Date(form.end_time)
          const localEndTime = new Date(endTime.getTime() - (endTime.getTimezoneOffset() * 60000))
          workLogData.end_time = localEndTime.toISOString()
        }
        
        if (isEdit.value && currentWorkLog.value) {
          await workLogApi.updateWorkLog(currentWorkLog.value.id, workLogData)
          ElementPlusElMessage.success('工作日志更新成功')
        } else {
          await workLogApi.createWorkLog(workLogData)
          ElementPlusElMessage.success('工作日志创建成功')
        }
        
        dialogVisible.value = false
        resetForm()
        fetchWorkLogs()
      } catch (error: any) {
        ElementPlusElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

const fetchTeams = async () => {
  try {
    const response = await teamApi.getTeams()
    teams.value = response.data || response
    // 如果用户有团队，设置第一个团队为当前团队
    if (teams.value.length > 0) {
      currentTeam.value = teams.value[0].id
      form.team_id = teams.value[0].id
      // 加载第一个团队的项目
      await fetchProjects(teams.value[0].id)
    }
  } catch (error) {
    console.error('获取团队列表失败:', error)
    ElMessage.error('获取团队列表失败')
  }
}

const fetchProjects = async (teamId: number) => {
  try {
    const response = await projectApi.getProjects(teamId)
    projects.value = response.data || response
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '获取项目列表失败')
  }
}

// 格式化日期时间
function formatDateTime(date: string) {
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

const timeShortcuts = [
  {
    text: '今天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setHours(9, 0, 0)
      end.setHours(17, 0, 0)
      return [start, end]
    }
  },
  {
    text: '明天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setDate(start.getDate() + 1)
      end.setDate(end.getDate() + 1)
      start.setHours(9, 0, 0)
      end.setHours(17, 0, 0)
      return [start, end]
    }
  }
]

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7 // 禁用今天之前的日期
}

const disabledHours = () => {
  const hours = []
  for (let i = 0; i < 24; i++) {
    if (i < 9 || i > 18) { // 只允许 9:00-18:00
      hours.push(i)
    }
  }
  return hours
}

const goToTeamView = () => {
  if (currentTeam.value) {
    router.push(`/teams/${currentTeam.value}/work-logs`)
  }
}

onMounted(async () => {
  await fetchTeams()
  await fetchWorkLogs()
})

const styles = `
.time-range-picker {
  display: flex;
  align-items: center;
}

.separator {
  margin: 0 10px;
  color: #606266;
}

.meta {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.task-detail {
  padding: 16px;
}

.task-detail h3 {
  margin: 0 0 12px 0;
  color: #303133;
}

.task-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.description {
  margin: 16px 0;
  line-height: 1.6;
  color: #606266;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.task-info {
  margin-top: 16px;
}

.task-info p {
  margin: 8px 0;
  color: #606266;
  line-height: 1.5;
}

.task-info strong {
  color: #303133;
  margin-right: 8px;
}
`

// 处理事件拖拽
const onEventDragged = async (event: any) => {
  console.log('【onEventDragged】事件被拖拽:', JSON.stringify(event, null, 2))
  try {
    // 确保事件对象包含必要的属性
    if (!event || !event.id || !event.time || !event.time.start || !event.time.end) {
      console.error('【onEventDragged】事件数据不完整:', event)
      ElementPlusElMessage.error('事件数据不完整')
      return
    }

    const worklog = worklogs.value.find((w: any) => String(w.id) === event.id)
    console.log('【onEventDragged】查找到的 worklog:', worklog)
    if (!worklog) {
      console.error('【onEventDragged】未找到对应的工作日志，id=', event.id)
      ElementPlusElMessage.error('未找到对应的工作日志')
      return
    }

    // 解析新的时间
    console.log('【onEventDragged】event.time:', event.time)
    const [startDate, startTime] = event.time.start.split(' ')
    const [endDate, endTime] = event.time.end.split(' ')
    
    // 创建本地时间对象
    const newStartTime = new Date(`${startDate}T${startTime}:00`)
    const newEndTime = new Date(`${endDate}T${endTime}:00`)
    
    // 获取本地时间的 ISO 字符串，但保持本地时间
    const formatLocalTime = (date: Date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
    }

    console.log('【onEventDragged】解析后的时间:', {
      newStartTime: formatLocalTime(newStartTime),
      newEndTime: formatLocalTime(newEndTime)
    })

    // 验证时间是否有效
    if (isNaN(newStartTime.getTime()) || isNaN(newEndTime.getTime())) {
      console.error('【onEventDragged】无效的时间格式')
      ElementPlusElMessage.error('无效的时间格式')
      return
    }

    // 验证时间范围
    if (newStartTime >= newEndTime) {
      console.error('【onEventDragged】结束时间必须晚于开始时间')
      ElementPlusElMessage.error('结束时间必须晚于开始时间')
      return
    }

    // 更新工作日志
    const workLogData: WorkLogCreate = {
      title: worklog.title || '',
      work_type: worklog.work_type || 'dev',
      content: worklog.content || '',
      start_time: formatLocalTime(newStartTime),
      end_time: formatLocalTime(newEndTime),
      team_id: worklog.team_id as number,
      project_id: worklog.project_id
    }
    console.log('【onEventDragged】准备提交的数据:', JSON.stringify(workLogData, null, 2))

    // 显示加载状态
    loading.value = true
    
    // 调用后端接口
    console.log('【onEventDragged】开始调用后端接口...')
    const response = await workLogApi.updateWorkLog(worklog.id, workLogData)
    console.log('【onEventDragged】后端接口响应:', response)
    
    ElementPlusElMessage.success('工作日志时间已更新')
    
    // 保存当前选中的日期
    const currentDate = selectedDate.value
    
    // 重新获取工作日志列表
    console.log('【onEventDragged】开始刷新工作日志列表...')
    await fetchWorkLogs()
    
    // 恢复选中的日期
    selectedDate.value = currentDate
    console.log('【onEventDragged】工作日志已刷新，恢复日期:', currentDate)
  } catch (error: any) {
    console.error('【onEventDragged】更新工作日志失败:', error)
    // 显示具体的错误信息
    const errorMessage = error.response?.data?.message || '更新工作日志失败'
    ElementPlusElMessage.error(errorMessage)
    
    // 保存当前选中的日期
    const currentDate = selectedDate.value
    
    // 如果更新失败，重新获取工作日志以恢复原始状态
    await fetchWorkLogs()
    
    // 恢复选中的日期
    selectedDate.value = currentDate
  } finally {
    loading.value = false
  }
}

// 处理事件大小调整
const onEventResized = async (event: any) => {
  console.log('【onEventResized】事件大小被调整:', JSON.stringify(event, null, 2))
  // 使用与拖拽相同的逻辑处理大小调整
  await onEventDragged(event)
}

// 处理事件更新（拖拽后）
const onEventUpdated = async (event: any) => {
  console.log('【onEventUpdated】事件更新触发，完整事件数据:', JSON.stringify(event, null, 2))
  try {
    // 确保事件对象包含必要的属性
    if (!event || !event.id || !event.time || !event.time.start || !event.time.end) {
      console.error('【onEventUpdated】事件数据不完整:', event)
      ElementPlusElMessage.error('事件数据不完整')
      return
    }

    const worklog = worklogs.value.find((w: any) => String(w.id) === event.id)
    console.log('【onEventUpdated】查找到的 worklog:', worklog)
    if (!worklog) {
      console.error('【onEventUpdated】未找到对应的工作日志，id=', event.id)
      ElementPlusElMessage.error('未找到对应的工作日志')
      return
    }

    // 解析新的时间
    console.log('【onEventUpdated】event.time:', event.time)
    const [startDate, startTime] = event.time.start.split(' ')
    const [endDate, endTime] = event.time.end.split(' ')
    const newStartTime = new Date(`${startDate}T${startTime}`)
    const newEndTime = new Date(`${endDate}T${endTime}`)
    console.log('【onEventUpdated】解析后的时间:', {
      newStartTime: newStartTime.toISOString(),
      newEndTime: newEndTime.toISOString()
    })

    // 验证时间是否有效
    if (isNaN(newStartTime.getTime()) || isNaN(newEndTime.getTime())) {
      console.error('【onEventUpdated】无效的时间格式')
      ElementPlusElMessage.error('无效的时间格式')
      return
    }

    // 验证时间范围
    if (newStartTime >= newEndTime) {
      console.error('【onEventUpdated】结束时间必须晚于开始时间')
      ElementPlusElMessage.error('结束时间必须晚于开始时间')
      return
    }

    // 更新工作日志
    const workLogData: WorkLogCreate = {
      title: worklog.title,
      work_type: worklog.work_type,
      content: worklog.content,
      start_time: newStartTime.toISOString(),
      end_time: newEndTime.toISOString(),
      team_id: worklog.team_id as number,
      project_id: worklog.project_id
    }
    console.log('【onEventUpdated】准备提交的数据:', JSON.stringify(workLogData, null, 2))

    // 显示加载状态
    loading.value = true
    
    // 调用后端接口
    console.log('【onEventUpdated】开始调用后端接口...')
    const response = await workLogApi.updateWorkLog(worklog.id, workLogData)
    console.log('【onEventUpdated】后端接口响应:', response)
    
    ElementPlusElMessage.success('工作日志时间已更新')
    
    // 重新获取工作日志列表
    console.log('【onEventUpdated】开始刷新工作日志列表...')
    await fetchWorkLogs()
    console.log('【onEventUpdated】工作日志已刷新')
  } catch (error: any) {
    console.error('【onEventUpdated】更新工作日志失败:', error)
    // 显示具体的错误信息
    const errorMessage = error.response?.data?.message || '更新工作日志失败'
    ElementPlusElMessage.error(errorMessage)
    
    // 如果更新失败，重新获取工作日志以恢复原始状态
    await fetchWorkLogs()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import 'qalendar/dist/style.css';

.calendar-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.display-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.display-controls .el-checkbox {
  margin-right: 0;
}

.time-range-picker {
  display: flex;
  align-items: center;
}

.separator {
  margin: 0 8px;
  color: #606266;
}

.worklog-detail {
  padding: 16px;
}

.worklog-detail h3 {
  margin: 0 0 12px 0;
  color: #303133;
}

.time-range {
  color: #606266;
  font-size: 14px;
  margin: 8px 0;
}

.content {
  margin: 16px 0;
  line-height: 1.6;
  color: #303133;
}

.meta {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

/* 任务事件样式 */
:deep(.qalendar-event) {
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

:deep(.qalendar-event[data-type="task"]) {
  border-left: 3px solid;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .actions {
    justify-content: space-between;
  }
  
  .display-controls {
    flex-direction: column;
    gap: 8px;
  }
}
</style> 
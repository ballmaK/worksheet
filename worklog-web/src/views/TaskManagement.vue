<!-- TaskManagement.vue -->
<template>
  <div class="task-management" @keydown="handleGlobalKeyDown" :tabindex="0">
    <!-- 页面头部 -->
    <TaskHeader
      v-model:searchKeyword="searchKeyword"
      v-model:filterPriority="filterPriority"
      v-model:filterTaskType="filterTaskType"
      v-model:filterStatus="filterStatus"
      :viewMode="viewMode"
      :selectedTeamId="selectedTeamId"
      :selectedProjectId="selectedProjectId"
      :selectedAssigneeIds="selectedAssigneeIds"
      @search="handleSearch"
      @filter="handleFilter"
      @create="showCreateDialog"
      @showFilter="showFilterDrawer"
    />

    <!-- 侧边抽屉筛选 -->
    <el-drawer
      v-model="drawerVisible"
      title="筛选条件"
      size="400px"
      direction="rtl"
      :with-header="true"
      :close-on-click-modal="true"
      :destroy-on-close="false"
      custom-class="filter-drawer"
    >
      <TaskFilters
        v-model:viewMode="viewMode"
        v-model:selectedTeamId="selectedTeamId"
        v-model:selectedProjectId="selectedProjectId"
        v-model:selectedAssigneeIds="selectedAssigneeIds"
        v-model:filterPriority="filterPriority"
        v-model:filterTaskType="filterTaskType"
        v-model:filterStatus="filterStatus"
        :teams="teams"
        :projects="projects"
        :teamMembers="teamMembers"
        @teamChange="handleTeamChange"
        @projectChange="handleProjectChange"
        @assigneeChange="handleAssigneeChange"
        @switchToMyTasks="switchToMyTasks"
        @switchToAllTasks="switchToAllTasks"
      />
    </el-drawer>

    <!-- 任务看板 -->
    <TaskKanban
        :tasks="filteredTasks"
        :loading="loading"
        :viewMode="viewMode"
        :teams="teams"
        :projects="projects"
        :teamMembers="teamMembers"
        @refresh="refreshTasks"
        @view-task="viewTask"
        @edit-task="editTask"
        @workflow-action="handleWorkflowAction"
        @show-assign-dialog="showAssignDialog"
        @show-create-dialog="showCreateDialog"
    />

    <!-- 任务详情抽屉 -->
    <TaskDetail
        v-model:visible="taskDetailVisible"
        :task="currentTask"
        :isEditing="isEditing"
        :teams="teams"
        :projects="projects"
        :teamMembers="teamMembers"
        @submit="handleSubmit"
        @close="closeTaskDetail"
    />

    <!-- 分配任务对话框 -->
    <AssignTaskDialog
        v-model:visible="showAssignDialogVisible"
        :task="currentTask"
        :availableMembers="availableMembers"
        @assign="handleAssignTask"
    />

    <!-- 快速创建任务组件 -->
    <QuickCreateTask
        ref="quickCreateTaskRef"
        @taskCreated="handleTaskCreated"
        @taskCreateError="handleTaskCreateError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Plus } from '@element-plus/icons-vue'
import TaskHeader from '@/components/TaskHeader.vue'
import TaskFilters from '@/components/TaskFilters.vue'
import TaskKanban from '@/components/TaskKanban.vue'
import TaskDetail from '@/components/TaskDetail.vue'
import AssignTaskDialog from '@/components/AssignTaskDialog.vue'
import QuickCreateTask from '@/components/QuickCreateTask.vue'
import { teamApi } from '@/api/team'
import { projectApi } from '@/api/project'
import { taskApi } from '@/api/task'
import type { Task } from '@/api/task'
import type { Team } from '@/api/team'
import type { Project } from '@/api/project'

// 响应式数据
const viewMode = ref('all')
const selectedTeamId = ref<number>()
const selectedProjectId = ref<number>()
const selectedAssigneeIds = ref<number[]>([])
const teams = ref<Team[]>([])
const projects = ref<Project[]>([])
const tasks = ref<Task[]>([])
const teamMembers = ref<any[]>([])
const availableMembers = ref<any[]>([])
const loading = ref(false)
const drawerVisible = ref(false)

// 搜索和过滤
const searchKeyword = ref('')
const filterPriority = ref('')
const filterTaskType = ref('')
const filterStatus = ref('')

// 快速创建任务相关
const quickTaskTitle = ref('')
const quickCreating = ref(false)
const quickCreateTaskRef = ref()

// 任务详情相关
const taskDetailVisible = ref(false)
const isEditing = ref(false)
const currentTask = ref<Task | null>(null)
const showAssignDialogVisible = ref(false)

// 双击空格键相关
const lastSpaceTime = ref(0)
const spaceKeyCount = ref(0)

// 计算属性
const filteredTasks = computed(() => {
  let result = tasks.value

  // 关键字搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(task =>
        task.title.toLowerCase().includes(keyword) ||
        task.description?.toLowerCase().includes(keyword)
    )
  }

  // 优先级过滤（支持多选）
  if (filterPriority.value) {
    const priorities = filterPriority.value.split(',').filter(Boolean)
    if (priorities.length > 0) {
      result = result.filter(task => priorities.includes(task.priority))
    }
  }

  // 任务类型过滤（支持多选）
  if (filterTaskType.value) {
    const types = filterTaskType.value.split(',').filter(Boolean)
    if (types.length > 0) {
      result = result.filter(task => types.includes(task.task_type))
    }
  }

  // 状态过滤（支持多选）
  if (filterStatus.value) {
    const statuses = filterStatus.value.split(',').filter(Boolean)
    if (statuses.length > 0) {
      result = result.filter(task => statuses.includes(task.status))
    }
  }

  // 负责人过滤（支持多选）
  if (selectedAssigneeIds.value.length > 0) {
    result = result.filter(task => 
      task.assignee_id && selectedAssigneeIds.value.includes(task.assignee_id)
    )
  }

  return result
})

// 全局键盘事件处理 - 双击空格键快速创建任务
const handleGlobalKeyDown = (event: KeyboardEvent) => {
  // 如果当前在输入框中，不处理空格键
  const target = event.target as HTMLElement
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.contentEditable === 'true') {
    return
  }
  
  // 检测双击空格键
  if (event.code === 'Space') {
    event.preventDefault() // 阻止默认的空格行为
    
    const currentTime = Date.now()
    if (currentTime - lastSpaceTime.value < 300) { // 300ms内的双击
      spaceKeyCount.value++
      if (spaceKeyCount.value >= 2) {
        showQuickCreateDialog()
        spaceKeyCount.value = 0
        lastSpaceTime.value = 0 // 重置时间
      }
    } else {
      spaceKeyCount.value = 1
    }
    lastSpaceTime.value = currentTime
  }
}

// 显示快速创建任务弹窗
const showQuickCreateDialog = () => {
  if (quickCreateTaskRef.value && typeof quickCreateTaskRef.value.showQuickCreateDialog === 'function') {
    quickCreateTaskRef.value.showQuickCreateDialog()
  } else {
    // 备用方案：直接显示任务详情弹窗
    showCreateDialog()
  }
}

// 方法
const fetchTeams = async () => {
  try {
    const response = await teamApi.getTeams()
    teams.value = response.data || response
  } catch (error) {
    ElMessage.error('获取团队列表失败')
  }
}

const fetchProjects = async () => {
  try {
    const response = await projectApi.getProjects()
    projects.value = response.data || response
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

const fetchTeamMembers = async (teamId: number) => {
  if (!teamId) return
  try {
    const response = await teamApi.getTeamMembers(teamId)
    const members = response.data || response
    teamMembers.value = members
    availableMembers.value = members
  } catch (error) {
    console.error('获取团队成员失败:', error)
    ElMessage.error('获取团队成员失败')
    teamMembers.value = []
    availableMembers.value = []
  }
}

const fetchTasks = async () => {
  loading.value = true
  try {
    let response
    switch (viewMode.value) {
      case 'my':
        const userId = parseInt(localStorage.getItem('userId') || '0')
        if (!userId) return
        response = await taskApi.getTasks({ assignee_id: userId })
        break
      case 'team':
        if (selectedTeamId.value) {
          response = await taskApi.getTasks({ team_id: selectedTeamId.value })
        }
        break
      case 'project':
        if (selectedProjectId.value) {
          response = await taskApi.getTasks({ project_id: selectedProjectId.value })
        }
        break
      default:
        response = await taskApi.getTasks({})
        break
    }
    if (response) {
      const data = response.data || response
      tasks.value = data?.items || data || []
    }
  } catch (error) {
    ElMessage.error('获取任务失败')
  } finally {
    loading.value = false
  }
}

const refreshTasks = async () => {
  await fetchTasks()
}

const handleSearch = () => {
  // 搜索时不需要特殊处理，因为使用了计算属性
}

const handleFilter = () => {
  // 过滤时不需要特殊处理，因为使用了计算属性
}

const handleTeamChange = async (teamId: number | undefined) => {
  selectedTeamId.value = teamId
  selectedProjectId.value = undefined
  selectedAssigneeIds.value = []
  
  if (teamId) {
    viewMode.value = 'team'
    await fetchTeamMembers(teamId)
    await fetchTasks()
  } else {
    viewMode.value = 'all'
    tasks.value = []
    // 重新加载所有团队成员
    await loadAllTeamMembers()
  }
}

const handleProjectChange = async (projectId: number | undefined) => {
  selectedProjectId.value = projectId
  selectedTeamId.value = undefined
  selectedAssigneeIds.value = []
  
  if (projectId) {
    viewMode.value = 'project'
    await fetchTasks()
  } else {
    viewMode.value = 'all'
    tasks.value = []
  }
  // 确保有团队成员数据用于筛选
  if (teamMembers.value.length === 0) {
    await loadAllTeamMembers()
  }
}

const switchToMyTasks = async () => {
  viewMode.value = 'my'
  selectedTeamId.value = undefined
  selectedProjectId.value = undefined
  selectedAssigneeIds.value = []
  // 加载所有团队的成员数据，用于负责人筛选
  await loadAllTeamMembers()
  await fetchTasks()
}

const switchToAllTasks = async () => {
  viewMode.value = 'all'
  selectedTeamId.value = undefined
  selectedProjectId.value = undefined
  selectedAssigneeIds.value = []
  // 加载所有团队的成员数据，用于负责人筛选
  await loadAllTeamMembers()
  await fetchTasks()
}

// 加载所有团队的成员数据
const loadAllTeamMembers = async () => {
  try {
    console.log('开始加载所有团队成员...')
    const allMembers: any[] = []
    for (const team of teams.value) {
      try {
        console.log(`正在加载团队 ${team.id} (${team.name}) 的成员...`)
        const response = await teamApi.getTeamMembers(team.id)
        const members = response.data || response
        console.log(`团队 ${team.id} 成员数据:`, members)
        allMembers.push(...members)
      } catch (error) {
        console.error(`获取团队${team.id}成员失败:`, error)
      }
    }
    // 去重，避免重复的成员
    const uniqueMembers = allMembers.filter((member, index, self) => 
      index === self.findIndex(m => m.id === member.id)
    )
    console.log('去重后的所有成员:', uniqueMembers)
    teamMembers.value = uniqueMembers
    availableMembers.value = uniqueMembers
  } catch (error) {
    console.error('加载团队成员失败:', error)
    teamMembers.value = []
    availableMembers.value = []
  }
}

// 快速创建任务 - 兼容原有的输入框
const handleQuickCreateTask = async () => {
  if (!quickTaskTitle.value.trim()) {
    ElMessage.warning('请输入任务标题')
    return
  }
  
  if (!teams.value.length) {
    ElMessage.warning('请先创建团队')
    return
  }
  
  try {
    quickCreating.value = true
    
    const taskData = {
      title: quickTaskTitle.value.trim(),
      description: '',
      team_id: teams.value[0].id,
      status: 'pending' as const,
      priority: 'medium' as const,
      task_type: 'other' as const
    }
    
    await taskApi.createTask(taskData)
    
    ElMessage.success('任务创建成功')
    quickTaskTitle.value = ''
    
    // 刷新任务列表
    await fetchTasks()
  } catch (error: any) {
    console.error('快速创建任务失败:', error)
    ElMessage.error(error.response?.data?.message || '创建任务失败')
  } finally {
    quickCreating.value = false
  }
}

// 处理QuickCreateTask组件的事件
const handleTaskCreated = async (task: any) => {
  // 刷新任务列表
  await fetchTasks()
}

const handleTaskCreateError = (error: any) => {
  console.error('任务创建失败:', error)
  ElMessage.error('创建任务失败')
}

// 任务详情相关
const showCreateDialog = () => {
  isEditing.value = true
  currentTask.value = null
  taskDetailVisible.value = true
}

const viewTask = (task: Task) => {
  isEditing.value = false
  currentTask.value = task
  taskDetailVisible.value = true
}

const editTask = (task: Task) => {
  isEditing.value = true
  currentTask.value = task
  taskDetailVisible.value = true
}

const closeTaskDetail = () => {
  taskDetailVisible.value = false
  currentTask.value = null
}

const handleSubmit = async () => {
  await fetchTasks()
  closeTaskDetail()
}

// 工作流操作
const handleWorkflowAction = async (command: string) => {
  const [action, taskId] = command.split(':')
  const taskIdNum = parseInt(taskId)

  try {
    switch (action) {
      case 'claim':
        await taskApi.claimTask(taskIdNum)
        ElMessage.success('任务认领成功')
        break
      case 'start':
        await taskApi.startTaskWork(taskIdNum)
        ElMessage.success('任务工作已开始')
        break
      case 'complete':
        await taskApi.completeTask(taskIdNum)
        ElMessage.success('任务已完成')
        break
      case 'submit':
        await taskApi.submitTaskForReview(taskIdNum)
        ElMessage.success('任务已提交审核')
        break
      case 'approve':
        await taskApi.approveTask(taskIdNum)
        ElMessage.success('任务审核通过')
        break
      case 'update-status':
        const [, , status] = command.split(':')
        await taskApi.updateTask(taskIdNum, { status: status as any })
        ElMessage.success('任务状态更新成功')
        break
    }

    // 刷新数据
    await refreshTasks()
  } catch (error: any) {
    ElMessage.error('操作失败：' + (error.response?.data?.detail || '未知错误'))
  }
}

// 分配任务
const showAssignDialog = (task: Task) => {
  currentTask.value = task
  showAssignDialogVisible.value = true
}

const handleAssignTask = async (assigneeId: number) => {
  if (!currentTask.value) return
  
  try {
    await taskApi.assignTask(currentTask.value.id, assigneeId)
    ElMessage.success('任务分配成功')
    showAssignDialogVisible.value = false
    await refreshTasks()
  } catch (error: any) {
    ElMessage.error('分配任务失败：' + (error.response?.data?.detail || '未知错误'))
  }
}

const handleAssigneeChange = async (assigneeIds: number[]) => {
  selectedAssigneeIds.value = assigneeIds
  // 负责人筛选不需要重新获取数据，使用计算属性过滤即可
}

const showFilterDrawer = () => {
  drawerVisible.value = true
}

onMounted(async () => {
  await fetchTeams()
  await fetchProjects()
  await loadAllTeamMembers() // 加载所有团队成员
  await fetchTasks()
  
  // 确保页面获得焦点以便接收键盘事件
  await nextTick()
  const taskManagementEl = document.querySelector('.task-management') as HTMLElement
  if (taskManagementEl) {
    taskManagementEl.focus()
    console.log('TaskManagement 页面已获得焦点')
  } else {
    console.error('找不到 .task-management 元素')
  }
  
  // 移除全局键盘事件监听，避免与QuickCreateTask组件冲突
  // document.addEventListener('keydown', handleGlobalKeyDown)
  console.log('TaskManagement 页面初始化完成')
})
</script>

<style scoped>
.task-management {
  padding: 24px;
  height: calc(100vh - 60px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  outline: none; /* 移除tabindex的默认边框 */
}

.filter-drawer {
  padding-top: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-management {
    padding: 8px;
  }
  .filter-drawer {
    width: 100vw !important;
    max-width: 100vw !important;
    min-width: 0 !important;
  }
}
</style> 
<template>
  <div class="project-management">
    <el-page-header @back="goBack" :title="project.name || '项目管理'" />
    
    <!-- 项目概览 -->
    <el-card class="project-overview" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>项目概览</span>
          <el-button @click="refreshData" type="primary" :icon="Refresh" size="small">刷新</el-button>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="project.id">
        <el-row :gutter="20">
          <el-col :span="16">
            <div class="project-info">
              <h2>{{ project.name }}</h2>
              <p class="description">{{ project.description || '暂无描述' }}</p>
              <div class="project-meta">
                <el-tag :type="getStatusType(project.status)" size="large">
                  {{ getStatusLabel(project.status) }}
                </el-tag>
                <span class="date-range">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(project.start_date) }} ~ {{ formatDate(project.end_date) }}
                </span>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="progress-info">
              <div class="progress-circle">
                <el-progress 
                  type="dashboard" 
                  :percentage="statistics.completion_rate || 0"
                  :color="getProgressColor"
                />
                <div class="progress-label">完成率</div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 统计卡片 -->
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.total_tasks || 0 }}</div>
                <div class="stat-label">总任务数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.completed_tasks || 0 }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.in_progress_tasks || 0 }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.pending_tasks || 0 }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 工时统计 -->
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card>
              <template #header>工时统计</template>
              <div class="hours-stats">
                <div class="hours-item">
                  <span class="hours-label">预估工时：</span>
                  <span class="hours-value">{{ statistics.total_estimated_hours || 0 }}h</span>
                </div>
                <div class="hours-item">
                  <span class="hours-label">实际工时：</span>
                  <span class="hours-value">{{ statistics.total_actual_hours || 0 }}h</span>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>项目成员</template>
              <div class="members-list">
                <div v-for="member in teamMembers" :key="member.id" class="member-item">
                  <el-avatar :size="32">{{ member.username.charAt(0) }}</el-avatar>
                  <span class="member-name">{{ member.username }}</span>
                  <el-tag size="small" :type="member.role === 'team_admin' ? 'danger' : 'info'">
                    {{ member.role === 'team_admin' ? '管理员' : '成员' }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 标签页切换 -->
    <el-card style="margin-top: 20px;">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="任务管理" name="tasks">
          <div class="tab-content">
            <div class="tab-header">
              <div class="filters">
                <el-select v-model="taskFilters.status" placeholder="状态筛选" clearable style="width: 120px;">
                  <el-option label="全部" value="" />
                  <el-option label="待处理" value="pending" />
                  <el-option label="进行中" value="in_progress" />
                  <el-option label="已完成" value="completed" />
                </el-select>
                <el-select v-model="taskFilters.priority" placeholder="优先级" clearable style="width: 120px;">
                  <el-option label="全部" value="" />
                  <el-option label="低" value="low" />
                  <el-option label="中" value="medium" />
                  <el-option label="高" value="high" />
                  <el-option label="紧急" value="urgent" />
                </el-select>
                <el-input 
                  v-model="taskFilters.keyword" 
                  placeholder="搜索任务" 
                  style="width: 200px;"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <el-button @click="createTask" type="primary" :icon="Plus">新建任务</el-button>
            </div>
            
            <el-table :data="tasks" v-loading="tasksLoading" style="margin-top: 20px;">
              <el-table-column prop="title" label="任务标题" min-width="200">
                <template #default="{ row }">
                  <div class="task-title">
                    <span>{{ row.title }}</span>
                    <el-tag v-if="row.task_type" size="small" style="margin-left: 8px;">
                      {{ getTaskTypeLabel(row.task_type) }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getTaskStatusType(row.status)" size="small">
                    {{ getTaskStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="priority" label="优先级" width="100">
                <template #default="{ row }">
                  <el-tag :type="getPriorityType(row.priority)" size="small">
                    {{ getPriorityLabel(row.priority) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="assignee" label="负责人" width="120">
                <template #default="{ row }">
                  <span v-if="row.assignee">{{ row.assignee.username }}</span>
                  <span v-else class="text-muted">未分配</span>
                </template>
              </el-table-column>
              <el-table-column prop="due_date" label="截止日期" width="120">
                <template #default="{ row }">
                  <span v-if="row.due_date">{{ formatDate(row.due_date) }}</span>
                  <span v-else class="text-muted">无</span>
                </template>
              </el-table-column>
              <el-table-column prop="estimated_hours" label="预估工时" width="100">
                <template #default="{ row }">
                  <span v-if="row.estimated_hours">{{ row.estimated_hours }}h</span>
                  <span v-else class="text-muted">-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button @click="editTask(row)" size="small" type="primary">编辑</el-button>
                  <el-button @click="viewTaskDetail(row)" size="small">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="taskPagination.page"
                v-model:page-size="taskPagination.pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="taskPagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleTaskPageSizeChange"
                @current-change="handleTaskPageChange"
              />
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="项目动态" name="activities">
          <div class="tab-content">
            <div class="activities-list">
              <div v-for="activity in activities" :key="activity.id" class="activity-item">
                <div class="activity-header">
                  <el-avatar :size="32">{{ activity.user.username.charAt(0) }}</el-avatar>
                  <div class="activity-info">
                    <span class="activity-title">{{ activity.title }}</span>
                    <span class="activity-time">{{ formatDateTime(activity.created_at) }}</span>
                  </div>
                </div>
                <div v-if="activity.content" class="activity-content">
                  {{ activity.content }}
                </div>
              </div>
              
              <div v-if="activities.length === 0" class="empty-state">
                <el-empty description="暂无项目动态" />
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="taskDialogVisible" title="创建任务" width="600px">
      <el-form ref="taskFormRef" :model="taskForm" :rules="taskFormRules" label-width="100px">
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="请输入任务描述" />
        </el-form-item>
        <el-form-item label="任务类型" prop="task_type">
          <el-select v-model="taskForm.task_type" placeholder="请选择任务类型">
            <el-option label="功能开发" value="feature" />
            <el-option label="Bug修复" value="bug" />
            <el-option label="改进优化" value="improvement" />
            <el-option label="文档工作" value="documentation" />
            <el-option label="会议" value="meeting" />
            <el-option label="调研" value="research" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人" prop="assignee_id">
          <el-select v-model="taskForm.assignee_id" placeholder="请选择负责人" clearable>
            <el-option 
              v-for="member in teamMembers" 
              :key="member.id" 
              :label="member.username" 
              :value="member.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker 
            v-model="taskForm.due_date" 
            type="datetime" 
            placeholder="请选择截止日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="预估工时" prop="estimated_hours">
          <el-input-number 
            v-model="taskForm.estimated_hours" 
            :min="0" 
            :precision="1" 
            placeholder="请输入预估工时"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button @click="submitTask" type="primary" :loading="taskSubmitting">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Calendar, 
  Plus, 
  Search, 
  Refresh,
  Edit,
  View
} from '@element-plus/icons-vue'
import { projectManagementApi } from '@/api/projectManagement'
import { taskApi } from '@/api/task'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

// 响应式数据
const loading = ref(false)
const tasksLoading = ref(false)
const taskDialogVisible = ref(false)
const taskSubmitting = ref(false)
const activeTab = ref('tasks')

const project = ref<any>({})
const statistics = ref<any>({})
const teamMembers = ref<any[]>([])
const tasks = ref<any[]>([])
const activities = ref<any[]>([])

// 任务筛选
const taskFilters = ref({
  status: '',
  priority: '',
  keyword: ''
})

// 任务分页
const taskPagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 任务表单
const taskForm = ref({
  title: '',
  description: '',
  task_type: 'feature',
  priority: 'medium',
  assignee_id: null,
  due_date: null,
  estimated_hours: null
})

const taskFormRules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' }
  ],
  task_type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

// 计算属性
const getProgressColor = computed(() => {
  const rate = statistics.value.completion_rate || 0
  if (rate >= 80) return '#67C23A'
  if (rate >= 60) return '#E6A23C'
  if (rate >= 40) return '#F56C6C'
  return '#909399'
})

// 方法
const goBack = () => {
  router.back()
}

const refreshData = async () => {
  await Promise.all([
    loadProjectOverview(),
    loadTasks(),
    loadActivities()
  ])
}

const loadProjectOverview = async () => {
  try {
    loading.value = true
    const response = await projectManagementApi.getProjectOverview(projectId)
    project.value = response.project
    statistics.value = response.statistics
    teamMembers.value = response.team_members
  } catch (error: any) {
    ElMessage.error(error.message || '加载项目概览失败')
  } finally {
    loading.value = false
  }
}

const loadTasks = async () => {
  try {
    tasksLoading.value = true
    const params = {
      skip: (taskPagination.value.page - 1) * taskPagination.value.pageSize,
      limit: taskPagination.value.pageSize,
      ...taskFilters.value
    }
    
    const response = await projectManagementApi.getProjectTasks(projectId, params)
    tasks.value = response
    taskPagination.value.total = response.length // 这里需要后端返回总数
  } catch (error: any) {
    ElMessage.error(error.message || '加载任务列表失败')
  } finally {
    tasksLoading.value = false
  }
}

const loadActivities = async () => {
  try {
    const response = await projectManagementApi.getProjectActivities(projectId)
    activities.value = response.activities || []
  } catch (error: any) {
    console.error('加载项目动态失败:', error)
  }
}

const handleTabClick = (tab: any) => {
  if (tab.props.name === 'activities' && activities.value.length === 0) {
    loadActivities()
  }
}

const handleTaskPageSizeChange = (size: number) => {
  taskPagination.value.pageSize = size
  taskPagination.value.page = 1
  loadTasks()
}

const handleTaskPageChange = (page: number) => {
  taskPagination.value.page = page
  loadTasks()
}

const createTask = () => {
  taskForm.value = {
    title: '',
    description: '',
    task_type: 'feature',
    priority: 'medium',
    assignee_id: null,
    due_date: null,
    estimated_hours: null
  }
  taskDialogVisible.value = true
}

const submitTask = async () => {
  try {
    taskSubmitting.value = true
    await projectManagementApi.createProjectTask(projectId, taskForm.value)
    ElMessage.success('任务创建成功')
    taskDialogVisible.value = false
    loadTasks()
    loadActivities()
  } catch (error: any) {
    ElMessage.error(error.message || '创建任务失败')
  } finally {
    taskSubmitting.value = false
  }
}

const editTask = (task: any) => {
  ElMessage.info('编辑任务功能待实现')
}

const viewTaskDetail = (task: any) => {
  ElMessage.info('查看任务详情功能待实现')
}

// 工具方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'not_started': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'paused': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    'not_started': '未开始',
    'in_progress': '进行中',
    'completed': '已完成',
    'paused': '已暂停'
  }
  return statusMap[status] || '未知'
}

const getTaskStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': 'info',
    'assigned': 'warning',
    'in_progress': 'primary',
    'review': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

const getTaskStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待处理',
    'assigned': '已分配',
    'in_progress': '进行中',
    'review': '待审核',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || '未知'
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

const getPriorityLabel = (priority: string) => {
  const priorityMap: Record<string, string> = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'urgent': '紧急'
  }
  return priorityMap[priority] || '未知'
}

const getTaskTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    'feature': '功能',
    'bug': 'Bug',
    'improvement': '改进',
    'documentation': '文档',
    'meeting': '会议',
    'research': '调研',
    'other': '其他'
  }
  return typeMap[type] || '未知'
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 监听筛选条件变化
watch(taskFilters, () => {
  taskPagination.value.page = 1
  loadTasks()
}, { deep: true })

// 生命周期
onMounted(() => {
  if (projectId) {
    refreshData()
  }
})
</script>

<style scoped>
.project-management {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  padding: 20px;
}

.project-info h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.description {
  color: #606266;
  margin: 10px 0;
  line-height: 1.6;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 15px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 14px;
}

.progress-info {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.progress-circle {
  text-align: center;
}

.progress-label {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.hours-stats {
  padding: 10px 0;
}

.hours-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.hours-label {
  color: #606266;
}

.hours-value {
  font-weight: bold;
  color: #303133;
}

.members-list {
  max-height: 200px;
  overflow-y: auto;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.member-item:last-child {
  border-bottom: none;
}

.member-name {
  flex: 1;
  font-size: 14px;
}

.tab-content {
  padding: 20px 0;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}

.task-title {
  display: flex;
  align-items: center;
}

.text-muted {
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.activities-list {
  max-height: 600px;
  overflow-y: auto;
}

.activity-item {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.activity-info {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #303133;
  margin-right: 10px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

.activity-content {
  color: #606266;
  line-height: 1.5;
  margin-left: 42px;
}

.empty-state {
  padding: 40px;
  text-align: center;
}
</style>

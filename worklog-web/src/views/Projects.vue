<!-- Projects.vue -->
<template>
  <div class="projects-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>项目列表</h2>
        <span class="project-count">共 {{ totalProjects }} 个项目</span>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleCreateProject" v-if="hasCreatePermission">
          <el-icon><Plus /></el-icon>
          创建项目
        </el-button>
      </div>
    </div>

    <!-- 项目统计 -->
    <el-row :gutter="20" style="margin-bottom: 20px;" v-if="hasViewPermission">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total }}</div>
            <div class="stat-label">总项目数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.in_progress }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.my_projects }}</div>
            <div class="stat-label">我的项目</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <el-card style="margin-bottom: 20px;" v-if="hasViewPermission">
      <div class="filter-section">
        <div class="filter-left">
          <el-select v-model="filters.team_id" placeholder="选择团队" clearable style="width: 150px; margin-right: 10px;">
            <el-option
              v-for="team in teams"
              :key="team.id"
              :label="team.name"
              :value="team.id"
            />
          </el-select>
          <el-select v-model="filters.status" placeholder="项目状态" clearable style="width: 120px; margin-right: 10px;">
            <el-option label="未开始" value="not_started" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已暂停" value="on_hold" />
          </el-select>
          <el-select v-model="filters.role" placeholder="我的角色" clearable style="width: 120px;">
            <el-option label="我创建的" value="creator" />
            <el-option label="我参与的" value="member" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索项目名称"
            style="width: 200px; margin-right: 10px;"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>
    </el-card>

    <!-- 权限提示 -->
    <el-alert
      v-if="!hasViewPermission"
      title="权限不足"
      description="您没有查看项目的权限。请联系管理员获取访问权限。"
      type="warning"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    />

    <!-- 项目列表 -->
    <div v-if="hasViewPermission">
      <!-- 列表视图 -->
      <el-card v-if="viewMode === 'list'">
        <el-table :data="filteredProjects" v-loading="loading" style="width: 100%">
          <el-table-column prop="name" label="项目名称" min-width="200">
            <template #default="{ row }">
              <div class="project-name-cell">
                <span class="project-name">{{ row.name }}</span>
                <el-tag v-if="row.is_my_project" type="success" size="small">我的</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
          <el-table-column prop="team_name" label="所属团队" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="120">
            <template #default="{ row }">
              <el-progress :percentage="row.progress || 0" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="120">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewProject(row)">查看</el-button>
              <el-button size="small" type="primary" @click="manageProject(row)" v-if="canManageProject(row)">
                管理
              </el-button>
              <el-button size="small" type="danger" @click="deleteProject(row)" v-if="canDeleteProject(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalProjects"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>

      <!-- 卡片视图 -->
      <div v-else class="projects-grid">
        <el-card v-for="project in filteredProjects" :key="project.id" class="project-card">
          <template #header>
            <div class="card-header">
              <div class="project-title">
                <span class="project-name">{{ project.name }}</span>
                <el-tag v-if="project.is_my_project" type="success" size="small">我的</el-tag>
              </div>
              <div class="header-actions">
                <el-dropdown @command="handleProjectAction">
                  <el-button type="primary" link>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'view', project }">查看</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'manage', project }" v-if="canManageProject(project)">
                        管理
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'edit', project }" v-if="canEditProject(project)">
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'delete', project }" v-if="canDeleteProject(project)" divided>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          
          <div class="project-info">
            <div class="project-description">{{ project.description || '暂无描述' }}</div>
            
            <div class="info-grid">
              <div class="info-item">
                <span class="label">所属团队：</span>
                <span class="value">{{ project.team_name }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态：</span>
                <el-tag :type="getStatusType(project.status)" size="small">
                  {{ getStatusText(project.status) }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">进度：</span>
                <el-progress :percentage="project.progress || 0" :stroke-width="6" style="width: 80px;" />
              </div>
              <div class="info-item">
                <span class="label">创建时间：</span>
                <span class="value">{{ formatDate(project.created_at) }}</span>
              </div>
            </div>

            <div class="project-stats">
              <div class="stat-item">
                <span class="stat-number">{{ project.task_count || 0 }}</span>
                <span class="stat-label">任务</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ project.member_count || 0 }}</span>
                <span class="stat-label">成员</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ project.worklog_count || 0 }}</span>
                <span class="stat-label">日志</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="filteredProjects.length === 0 && !loading" description="暂无项目" />
    </div>

    <!-- 视图切换 -->
    <div class="view-toggle" v-if="hasViewPermission">
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button label="list">
          <el-icon><List /></el-icon>
          列表
        </el-radio-button>
        <el-radio-button label="card">
          <el-icon><Grid /></el-icon>
          卡片
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建项目"
      width="500px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item label="所属团队" prop="team_id">
          <el-select v-model="createForm.team_id" placeholder="请选择团队" style="width: 100%">
            <el-option
              v-for="team in availableTeams"
              :key="team.id"
              :label="team.name"
              :value="team.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="createForm.status" placeholder="请选择项目状态">
            <el-option label="未开始" value="not_started" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已暂停" value="on_hold" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="createForm.start_date" type="date" placeholder="选择开始日期" />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker v-model="createForm.end_date" type="date" placeholder="选择结束日期" />
        </el-form-item>
        <el-form-item label="进度" prop="progress">
          <el-input-number v-model="createForm.progress" :min="0" :max="100" placeholder="请输入进度" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateProjectSubmit" :loading="creating">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, MoreFilled, List, Grid } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { projectApi } from '@/api/project'
import { teamApi } from '@/api/team'

const router = useRouter()
const userStore = useUserStore()

// 数据定义
const projects = ref([])
const teams = ref([])
const loading = ref(false)
const creating = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalProjects = ref(0)
const viewMode = ref<'list' | 'card'>('card')
const searchKeyword = ref('')

// 筛选条件
const filters = ref({
  team_id: null,
  status: null,
  role: null
})

// 统计信息
const statistics = ref({
  total: 0,
  in_progress: 0,
  completed: 0,
  my_projects: 0
})

// 创建项目相关
const showCreateDialog = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = ref({
  name: '',
  description: '',
  team_id: null,
  status: 'not_started',
  start_date: '',
  end_date: '',
  progress: 0
})

const createRules: FormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 50, message: '项目名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  team_id: [
    { required: true, message: '请选择所属团队', trigger: 'change' }
  ],
  progress: [
    { type: 'number', min: 0, max: 100, message: '进度必须在 0 到 100 之间', trigger: 'blur' }
  ]
}

// 计算属性
const hasViewPermission = computed(() => {
  // 这里可以根据用户角色判断是否有查看权限
  return true
})

const hasCreatePermission = computed(() => {
  // 这里可以根据用户角色判断是否有创建权限
  return true
})

const availableTeams = computed(() => {
  // 返回用户有权限的团队
  return teams.value
})

const filteredProjects = computed(() => {
  let result = projects.value

  // 搜索过滤
  if (searchKeyword.value) {
    result = result.filter(project => 
      project.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      project.description?.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }

  // 团队过滤
  if (filters.value.team_id) {
    result = result.filter(project => project.team_id === filters.value.team_id)
  }

  // 状态过滤
  if (filters.value.status) {
    result = result.filter(project => project.status === filters.value.status)
  }

  // 角色过滤
  if (filters.value.role) {
    if (filters.value.role === 'creator') {
      result = result.filter(project => project.creator_id === userStore.userId)
    } else if (filters.value.role === 'member') {
      result = result.filter(project => project.is_my_project)
    }
  }

  return result
})

// 生命周期
onMounted(async () => {
  await fetchProjects()
  await fetchTeams()
  await fetchStatistics()
})

// 获取项目列表
const fetchProjects = async () => {
  try {
    loading.value = true
    const response = await projectApi.getProjects()
    projects.value = response || []
    
    // 标记我的项目
    projects.value = projects.value.map(project => ({
      ...project,
      is_my_project: project.creator_id === userStore.userId
    }))
    
    totalProjects.value = projects.value.length
  } catch (error: any) {
    ElMessage.error('获取项目列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取团队列表
const fetchTeams = async () => {
  try {
    const response = await teamApi.getTeams()
    teams.value = response || []
  } catch (error: any) {
    console.error('获取团队列表失败:', error)
  }
}

// 获取统计信息
const fetchStatistics = async () => {
  try {
    // 这里应该调用统计API，暂时使用计算
    const total = projects.value.length
    const in_progress = projects.value.filter(p => p.status === 'in_progress').length
    const completed = projects.value.filter(p => p.status === 'completed').length
    const my_projects = projects.value.filter(p => p.creator_id === userStore.userId).length
    
    statistics.value = { total, in_progress, completed, my_projects }
  } catch (error: any) {
    console.error('获取统计信息失败:', error)
  }
}

// 创建项目
const handleCreateProject = () => {
  createForm.value = {
    name: '',
    description: '',
    team_id: null,
    status: 'not_started',
    start_date: '',
    end_date: '',
    progress: 0
  }
  showCreateDialog.value = true
}

// 提交创建项目
const handleCreateProjectSubmit = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
  } catch (error) {
    return
  }

  try {
    creating.value = true
    await projectApi.createProject(createForm.value)
    
    ElMessage.success('项目创建成功')
    showCreateDialog.value = false
    await fetchProjects() // 刷新项目列表
    await fetchStatistics() // 刷新统计信息
  } catch (error: any) {
    ElMessage.error('创建项目失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    creating.value = false
  }
}

// 查看项目
const viewProject = (project: any) => {
  router.push(`/projects/${project.id}`)
}

// 管理项目
const manageProject = (project: any) => {
  router.push(`/projects/${project.id}`)
}

// 编辑项目
const editProject = (project: any) => {
  router.push(`/projects/${project.id}/edit`)
}

// 删除项目
const deleteProject = async (project: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${project.name}" 吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    
    await projectApi.deleteProject(project.id)
    ElMessage.success('项目已删除')
    await fetchProjects() // 刷新项目列表
    await fetchStatistics() // 刷新统计信息
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除项目失败: ' + error.message)
    }
  }
}

// 项目操作处理
const handleProjectAction = (command: any) => {
  const { action, project } = command
  switch (action) {
    case 'view':
      viewProject(project)
      break
    case 'manage':
      manageProject(project)
      break
    case 'edit':
      editProject(project)
      break
    case 'delete':
      deleteProject(project)
      break
  }
}

// 权限判断
const canManageProject = (project: any) => {
  return project.creator_id === userStore.userId || project.is_admin
}

const canEditProject = (project: any) => {
  return project.creator_id === userStore.userId
}

const canDeleteProject = (project: any) => {
  return project.creator_id === userStore.userId
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    team_id: null,
    status: null,
    role: null
  }
  searchKeyword.value = ''
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 工具函数
function formatDate(date: string) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

function getStatusType(status: string) {
  const statusMap = {
    'not_started': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'on_hold': 'danger'
  }
  return statusMap[status] || 'info'
}

function getStatusText(status: string) {
  const statusMap = {
    'not_started': '未开始',
    'in_progress': '进行中',
    'completed': '已完成',
    'on_hold': '已暂停'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.projects-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.project-count {
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-left {
  display: flex;
  align-items: center;
}

.filter-right {
  display: flex;
  align-items: center;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.project-card {
  transition: all 0.3s;
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-name {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.project-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.project-description {
  color: #606266;
  line-height: 1.5;
  min-height: 40px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #909399;
  font-size: 14px;
}

.value {
  font-weight: 500;
  color: #303133;
}

.project-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-number {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  display: block;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #909399;
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.view-toggle {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 
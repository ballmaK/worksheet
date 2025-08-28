<template>
  <div class="my-teams">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>我的团队</h2>
        <span class="team-count">共 {{ totalTeams }} 个团队</span>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          创建团队
        </el-button>
      </div>
    </div>

    <!-- 团队统计 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total }}</div>
            <div class="stat-label">总团队数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.my_teams }}</div>
            <div class="stat-label">我创建的</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.member_teams }}</div>
            <div class="stat-label">我参与的</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total_members }}</div>
            <div class="stat-label">总成员数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <el-card style="margin-bottom: 20px;">
      <div class="filter-section">
        <div class="filter-left">
          <el-select v-model="filters.role" placeholder="我的角色" clearable style="width: 120px; margin-right: 10px;">
            <el-option label="我创建的" value="creator" />
            <el-option label="我参与的" value="member" />
            <el-option label="我是管理员" value="admin" />
          </el-select>
          <el-select v-model="filters.status" placeholder="团队状态" clearable style="width: 120px;">
            <el-option label="活跃" value="active" />
            <el-option label="归档" value="archived" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索团队名称"
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

    <!-- 团队列表 -->
    <div>
      <!-- 列表视图 -->
      <el-card v-if="viewMode === 'list'">
        <el-table :data="filteredTeams" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="团队名称" min-width="200">
            <template #default="{ row }">
              <div class="team-name-cell">
                <span class="team-name">{{ row.name }}</span>
                <el-tag v-if="row.is_my_team" type="success" size="small">我的</el-tag>
                <el-tag v-if="row.is_admin" type="danger" size="small">管理员</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
          <el-table-column prop="member_count" label="成员数" width="100">
            <template #default="{ row }">
              <el-tag type="info">{{ row.member_count || 0 }} 人</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="project_count" label="项目数" width="100">
            <template #default="{ row }">
              <el-tag type="warning">{{ row.project_count || 0 }} 个</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="120">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="300" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewTeam(row)">查看</el-button>
              <el-button size="small" type="primary" @click="goToMembers(row)">成员</el-button>
              <el-button size="small" type="warning" @click="goToProjects(row)">项目</el-button>
              <el-button size="small" type="info" @click="editTeam(row)" v-if="canEditTeam(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteTeam(row)" v-if="canDeleteTeam(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalTeams"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>

      <!-- 卡片视图 -->
      <div v-else class="teams-grid">
        <el-card v-for="team in filteredTeams" :key="team.id" class="team-card">
          <template #header>
            <div class="card-header">
              <div class="team-title">
                <span class="team-name">{{ team.name }}</span>
                <div class="team-tags">
                  <el-tag v-if="team.is_my_team" type="success" size="small">我的</el-tag>
                  <el-tag v-if="team.is_admin" type="danger" size="small">管理员</el-tag>
                </div>
              </div>
              <div class="header-actions">
                <el-dropdown @command="handleTeamAction">
                  <el-button type="primary" link>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'view', team }">查看</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'members', team }">成员管理</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'projects', team }">项目管理</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'edit', team }" v-if="canEditTeam(team)">编辑</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'delete', team }" v-if="canDeleteTeam(team)" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          
          <div class="team-info">
            <div class="team-description">{{ team.description || '暂无描述' }}</div>
            
            <div class="info-grid">
              <div class="info-item">
                <span class="label">成员数：</span>
                <span class="value">{{ team.member_count || 0 }} 人</span>
              </div>
              <div class="info-item">
                <span class="label">项目数：</span>
                <span class="value">{{ team.project_count || 0 }} 个</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间：</span>
                <span class="value">{{ formatDate(team.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">我的角色：</span>
                <el-tag :type="getRoleType(team.my_role)" size="small">
                  {{ getRoleText(team.my_role) }}
                </el-tag>
              </div>
            </div>

            <div class="team-stats">
              <div class="stat-item">
                <span class="stat-number">{{ team.active_projects || 0 }}</span>
                <span class="stat-label">活跃项目</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ team.pending_invites || 0 }}</span>
                <span class="stat-label">待处理邀请</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ team.recent_activities || 0 }}</span>
                <span class="stat-label">最近活动</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="filteredTeams.length === 0 && !loading" description="暂无团队" />
    </div>

    <!-- 视图切换 -->
    <div class="view-toggle">
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

    <!-- 创建团队对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="创建团队"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入团队描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑团队对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑团队"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入团队描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, MoreFilled, List, Grid } from '@element-plus/icons-vue'
import { teamApi, type Team } from '@/api/team'
import { teamMemberApi } from '@/api/team-member'
import { useUserStore } from '@/stores/user'
import { formatDate } from '@/utils/date'

const router = useRouter()
const userStore = useUserStore()

// 数据定义
const teams = ref<Team[]>([])
const loading = ref(false)
const submitting = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalTeams = ref(0)
const viewMode = ref<'list' | 'card'>('card')
const searchKeyword = ref('')

// 筛选条件
const filters = ref({
  role: null,
  status: null
})

// 统计信息
const statistics = ref({
  total: 0,
  my_teams: 0,
  member_teams: 0,
  total_members: 0
})

// 创建团队相关
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  description: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入团队名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 编辑团队相关
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive({
  id: 0,
  name: '',
  description: ''
})

// 计算属性
const filteredTeams = computed(() => {
  let result = teams.value

  // 搜索过滤
  if (searchKeyword.value) {
    result = result.filter(team => 
      team.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      team.description?.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }

  // 角色过滤
  if (filters.value.role) {
    if (filters.value.role === 'creator') {
      result = result.filter(team => team.is_my_team)
    } else if (filters.value.role === 'member') {
      result = result.filter(team => team.is_member)
    } else if (filters.value.role === 'admin') {
      result = result.filter(team => team.is_admin)
    }
  }

  // 状态过滤
  if (filters.value.status) {
    result = result.filter(team => team.status === filters.value.status)
  }

  return result
})

// 生命周期
onMounted(async () => {
  await fetchTeams()
  await fetchStatistics()
})

// 获取团队列表
const fetchTeams = async () => {
  try {
    loading.value = true
    const response = await teamApi.getTeams()
    teams.value = response || []
    
    // 处理团队数据，添加用户角色信息
    for (const team of teams.value) {
      await enrichTeamData(team)
    }
    
    totalTeams.value = teams.value.length
  } catch (error: any) {
    ElMessage.error('获取团队列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 丰富团队数据
const enrichTeamData = async (team: any) => {
  try {
    // 获取团队成员列表
    const members = await teamMemberApi.getTeamMembers(team.id)
    team.member_count = members.length
    
    // 确定当前用户在团队中的角色
    const currentUserId = userStore.userId
    const currentMember = members.find(member => member.user_id === currentUserId)
    
    if (currentMember) {
      team.my_role = currentMember.role
      team.is_member = true
      team.is_admin = currentMember.role === 'team_admin'
      team.is_my_team = team.creator_id === currentUserId
    } else {
      team.my_role = null
      team.is_member = false
      team.is_admin = false
      team.is_my_team = false
    }
    
    // 添加模拟数据（实际应该从API获取）
    team.project_count = Math.floor(Math.random() * 10) + 1
    team.active_projects = Math.floor(Math.random() * 5) + 1
    team.pending_invites = Math.floor(Math.random() * 3)
    team.recent_activities = Math.floor(Math.random() * 20) + 5
    
  } catch (error) {
    console.error('丰富团队数据失败:', error)
  }
}

// 获取统计信息
const fetchStatistics = async () => {
  try {
    const total = teams.value.length
    const my_teams = teams.value.filter(t => t.is_my_team).length
    const member_teams = teams.value.filter(t => t.is_member).length
    const total_members = teams.value.reduce((sum, team) => sum + (team.member_count || 0), 0)
    
    statistics.value = { total, my_teams, member_teams, total_members }
  } catch (error: any) {
    console.error('获取统计信息失败:', error)
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        await teamApi.createTeam(form)
        ElMessage.success('团队创建成功')
        dialogVisible.value = false
        await fetchTeams() // 刷新团队列表
        await fetchStatistics() // 刷新统计信息
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '创建团队失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 查看团队
const viewTeam = (team: any) => {
  router.push(`/teams/${team.id}`)
}

// 跳转到成员管理
const goToMembers = (row: any) => {
  router.push(`/teams/${row.id}/members`)
}

// 跳转到项目管理
const goToProjects = (row: any) => {
  router.push(`/teams/${row.id}/projects`)
}

// 编辑团队
const editTeam = (row: Team) => {
  editForm.id = row.id
  editForm.name = row.name
  editForm.description = row.description
  editDialogVisible.value = true
}

// 提交编辑表单
const handleEditSubmit = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        await teamApi.updateTeam(editForm)
        ElMessage.success('团队更新成功')
        editDialogVisible.value = false
        await fetchTeams() // 刷新团队列表
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '更新团队失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 删除团队
const deleteTeam = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除团队 ${row.name} 吗？`,
      '提示',
      { type: 'warning' }
    )
    await teamApi.deleteTeam(row.id)
    ElMessage.success('团队删除成功')
    await fetchTeams() // 刷新团队列表
    await fetchStatistics() // 刷新统计信息
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除团队失败')
    }
  }
}

// 团队操作处理
const handleTeamAction = (command: any) => {
  const { action, team } = command
  switch (action) {
    case 'view':
      viewTeam(team)
      break
    case 'members':
      goToMembers(team)
      break
    case 'projects':
      goToProjects(team)
      break
    case 'edit':
      editTeam(team)
      break
    case 'delete':
      deleteTeam(team)
      break
  }
}

// 权限判断
const canEditTeam = (team: any) => {
  return team.is_my_team
}

const canDeleteTeam = (team: any) => {
  return team.is_my_team
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    role: null,
    status: null
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
function getRoleType(role: string) {
  switch (role) {
    case 'team_admin': return 'danger'
    case 'team_member': return 'info'
    default: return 'info'
  }
}

function getRoleText(role: string) {
  switch (role) {
    case 'team_admin': return '管理员'
    case 'team_member': return '成员'
    default: return '未知'
  }
}
</script>

<style scoped>
.my-teams {
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

.team-count {
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

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.team-card {
  transition: all 0.3s;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.team-name {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.team-tags {
  display: flex;
  gap: 4px;
}

.team-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.team-description {
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

.team-stats {
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

.team-name-cell {
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
  gap: 10px;
}
</style> 
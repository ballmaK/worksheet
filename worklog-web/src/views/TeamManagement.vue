<template>
  <div class="team-management">
    <!-- 团队信息 -->
    <el-card class="team-info">
      <div class="header">
        <el-avatar :src="team.avatar" size="large" />
        <div class="info-text">
          <h2>{{ team.name }}</h2>
          <p>{{ team.description }}</p>
          <span>创建于：{{ formatDate(team.created_at) }}</span>
        </div>
        <div class="actions">
          <el-button type="primary" @click="editTeam" v-if="isAdmin">编辑团队</el-button>
        </div>
      </div>
    </el-card>

    <!-- 权限提示 -->
    <el-alert
      v-if="!isMember"
      title="权限不足"
      description="您不是该团队的成员，无法查看团队详细信息。请联系团队管理员获取访问权限。"
      type="warning"
      :closable="false"
      show-icon
      style="margin-top: 20px"
    />

    <!-- 成员管理 -->
    <el-card class="team-members" style="margin-top: 20px;" v-if="isMember">
      <div class="card-header">
        <span>团队成员 ({{ members.length }})</span>
        <el-button type="primary" @click="showInviteDialog = true" v-if="isAdmin">
          <el-icon><Plus /></el-icon>
          邀请成员
        </el-button>
      </div>
      
      <!-- 成员列表 -->
      <el-table :data="members" v-loading="loading">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'team_admin' ? 'danger' : 'info'">
              {{ row.role === 'team_admin' ? '管理员' : '成员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="joined_at" label="加入时间">
          <template #default="{ row }">
            {{ formatDate(row.joined_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" v-if="isAdmin">
          <template #default="{ row }">
            <el-button size="small" @click="changeRole(row)" v-if="isAdmin">变更角色</el-button>
            <el-button size="small" type="danger" @click="removeMember(row)" v-if="isAdmin">移除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 邀请列表 -->
      <div v-if="isAdmin" style="margin-top: 20px;">
        <h4>待处理的邀请 ({{ invites.length }})</h4>
        <div v-if="invites.length === 0" style="text-align: center; color: #999; padding: 20px;">
          暂无待处理的邀请
        </div>
        <el-table v-else :data="invites" v-loading="loading">
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="role" label="角色">
            <template #default="{ row }">
              <el-tag :type="row.role === 'team_admin' ? 'danger' : 'info'">
                {{ row.role === 'team_admin' ? '管理员' : '成员' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'accepted' ? 'success' : 'danger'">
                {{ row.status === 'pending' ? '待处理' : row.status === 'accepted' ? '已接受' : '已拒绝' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="邀请时间">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click="resendInvite(row)" v-if="row.status === 'pending'">重新发送</el-button>
              <el-button size="small" type="danger" @click="cancelInvite(row)" v-if="row.status === 'pending'">撤销邀请</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 邀请成员对话框 -->
    <el-dialog
      v-model="showInviteDialog"
      title="邀请新成员"
      width="500px"
    >
      <el-alert
        title="邀请方式说明"
        description="系统将向被邀请者的邮箱发送6位数字验证码，验证码10分钟内有效。被邀请者需要登录后使用验证码完成邀请验证。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      
      <el-form
        ref="inviteFormRef"
        :model="inviteForm"
        :rules="inviteRules"
        label-width="80px"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="inviteForm.email" 
            placeholder="请输入邮箱地址"
            type="email"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="inviteForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="团队成员" value="team_member" />
            <el-option label="团队管理员" value="team_admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInviteDialog = false">取消</el-button>
          <el-button type="primary" @click="handleInvite" :loading="inviting">
            发送邀请
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 变更角色对话框 -->
    <el-dialog
      v-model="showRoleDialog"
      title="变更成员角色"
      width="400px"
    >
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        label-width="80px"
      >
        <el-form-item label="成员">
          <span>{{ selectedMember?.username }}</span>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="roleForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="团队成员" value="team_member" />
            <el-option label="团队管理员" value="team_admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRoleDialog = false">取消</el-button>
          <el-button type="primary" @click="handleChangeRole" :loading="changingRole">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 任务统计与入口 -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="isMember">
      <el-col :span="6">
        <el-card>任务总数：{{ statistics.total }}</el-card>
      </el-col>
      <el-col :span="6">
        <el-card>进行中：{{ statistics.in_progress }}</el-card>
      </el-col>
      <el-col :span="6">
        <el-card>已完成：{{ statistics.completed }}</el-card>
      </el-col>
      <el-col :span="6">
        <el-button type="primary" @click="goToTaskBoard">进入任务管理</el-button>
      </el-col>
    </el-row>

    <!-- 项目列表 -->
    <el-card class="team-projects" style="margin-top: 20px;" v-if="isMember">
      <div class="card-header">
        <span>团队项目</span>
        <el-button type="primary" @click="createProject" v-if="isAdmin">新建项目</el-button>
      </div>
      <el-table :data="projects">
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="progress" label="进度" />
        <el-table-column prop="owner" label="负责人" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="viewProject(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 团队动态 -->
    <el-card class="team-logs" style="margin-top: 20px;" v-if="isMember">
      <div class="card-header">团队动态</div>
      <el-timeline>
        <el-timeline-item v-for="log in logs" :key="log.id" :timestamp="formatDate(log.created_at)">
          {{ log.user_name }}：{{ log.content }}
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { teamMemberApi, type TeamMember } from '@/api/team-member'
import { teamInviteApi, type TeamInvite } from '@/api/team-invite'
import { teamApi } from '@/api/team'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const teamId = computed(() => Number(route.params.teamId))

// 数据定义
const team = ref({
  id: '',
  name: '',
  description: '',
  avatar: '',
  created_at: '',
})
const members = ref<TeamMember[]>([])
const invites = ref<TeamInvite[]>([])
const statistics = ref({ total: 0, in_progress: 0, completed: 0 })
const projects = ref([])
const logs = ref([])
const currentUserRole = ref('') // 当前用户在团队中的角色
const loading = ref(false)

// 计算属性：判断当前用户是否是团队管理员
const isAdmin = computed(() => currentUserRole.value === 'team_admin')

// 计算属性：判断当前用户是否是团队成员（包括管理员）
const isMember = computed(() => currentUserRole.value === 'team_admin' || currentUserRole.value === 'team_member')

// 邀请相关
const showInviteDialog = ref(false)
const inviting = ref(false)
const inviteFormRef = ref<FormInstance>()
const inviteForm = ref({
  email: '',
  role: 'team_member'
})

const inviteRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 角色变更相关
const showRoleDialog = ref(false)
const changingRole = ref(false)
const roleFormRef = ref<FormInstance>()
const roleForm = ref({
  role: 'team_member'
})
const selectedMember = ref<TeamMember | null>(null)

// 生命周期加载数据
onMounted(async () => {
  await fetchTeamData()
  await fetchMembers()
  await fetchInvites()
})

// 获取团队数据
const fetchTeamData = async () => {
  try {
    const response = await teamApi.getTeam(teamId.value)
    team.value = response
  } catch (error: any) {
    ElMessage.error('获取团队信息失败: ' + error.message)
  }
}

// 获取成员列表
const fetchMembers = async () => {
  try {
    loading.value = true
    const response = await teamMemberApi.getTeamMembers(teamId.value)
    members.value = response || []
    
    // 确定当前用户在团队中的角色
    const currentUserId = userStore.userId
    if (currentUserId) {
      const currentMember = members.value.find(member => member.user_id === currentUserId)
      currentUserRole.value = currentMember?.role || ''
    }
  } catch (error: any) {
    ElMessage.error('获取成员列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取邀请列表
const fetchInvites = async () => {
  try {
    console.log('开始获取邀请列表，团队ID:', teamId.value)
    const response = await teamInviteApi.getInvites(teamId.value)
    console.log('邀请列表响应:', response)
    invites.value = response || []
    console.log('邀请列表数据:', invites.value)
  } catch (error) {
    console.error('获取邀请列表失败:', error)
  }
}

// 发送邀请
const handleInvite = async () => {
  if (!inviteFormRef.value) return
  
  try {
    await inviteFormRef.value.validate()
  } catch (error) {
    return
  }

  try {
    inviting.value = true
    console.log('发送邀请数据:', inviteForm.value)
    await teamMemberApi.inviteMember(teamId.value, {
      email: inviteForm.value.email,
      role: inviteForm.value.role
    })
    
    ElMessage.success('邀请发送成功')
    showInviteDialog.value = false
    inviteForm.value = { email: '', role: 'team_member' }
    console.log('邀请发送成功，开始刷新邀请列表')
    await fetchInvites() // 刷新邀请列表
    console.log('邀请列表刷新完成')
  } catch (error: any) {
    console.error('发送邀请失败:', error)
    ElMessage.error('发送邀请失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    inviting.value = false
  }
}

// 重新发送邀请
const resendInvite = async (invite: TeamInvite) => {
  try {
    await teamInviteApi.resendInvite(invite.id)
    ElMessage.success('邀请重新发送成功')
  } catch (error: any) {
    ElMessage.error('重新发送邀请失败: ' + error.message)
  }
}

// 撤销邀请
const cancelInvite = async (invite: TeamInvite) => {
  try {
    await ElMessageBox.confirm(
      `确定要撤销对 ${invite.email} 的邀请吗？`,
      '确认撤销',
      { type: 'warning' }
    )
    
    await teamInviteApi.deleteInvite(invite.id)
    ElMessage.success('邀请已撤销')
    await fetchInvites() // 刷新邀请列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('撤销邀请失败: ' + error.message)
    }
  }
}

// 变更角色
const changeRole = (member: TeamMember) => {
  selectedMember.value = member
  roleForm.value.role = member.role
  showRoleDialog.value = true
}

// 处理角色变更
const handleChangeRole = async () => {
  if (!selectedMember.value) return

  try {
    changingRole.value = true
    await teamMemberApi.updateMemberRole(teamId.value, selectedMember.value.id, {
      role: roleForm.value.role
    })
    
    ElMessage.success('角色变更成功')
    showRoleDialog.value = false
    await fetchMembers() // 刷新成员列表
  } catch (error: any) {
    ElMessage.error('角色变更失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    changingRole.value = false
  }
}

// 移除成员
const removeMember = async (member: TeamMember) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除成员 ${member.username} 吗？`,
      '确认移除',
      { type: 'warning' }
    )
    
    await teamMemberApi.removeMember(teamId.value, member.id)
    ElMessage.success('成员已移除')
    await fetchMembers() // 刷新成员列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('移除成员失败: ' + error.message)
    }
  }
}

// 工具函数
function formatDate(date: string) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

function editTeam() {
  ElMessage.info('编辑团队功能开发中')
}

function goToTaskBoard() {
  router.push({ name: 'team-tasks', params: { teamId: team.value.id } })
}

function createProject() {
  router.push({ path: '/project/create', query: { teamId: team.value.id } })
}

function viewProject(row: any) {
  ElMessage.info('查看项目功能开发中')
}
</script>

<style scoped>
.team-management {
  padding: 20px;
}

.team-info {
  margin-bottom: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.info-text {
  flex: 1;
}

.info-text h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.info-text p {
  margin: 0 0 8px 0;
  color: #606266;
}

.info-text span {
  color: #909399;
  font-size: 14px;
}

.actions {
  margin-left: auto;
}

.team-members {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
}

.card-header span {
  font-size: 16px;
  color: #303133;
}

.team-projects {
  margin-bottom: 20px;
}

.team-logs {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 
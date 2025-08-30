<template>
  <el-card class="team-members">
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
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { teamMemberApi, type TeamMember } from '@/api/team-member'
import { teamInviteApi, type TeamInvite } from '@/api/team-invite'

interface Props {
  teamId: number
  isAdmin: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  refresh: []
}>()

// 数据定义
const members = ref<TeamMember[]>([])
const invites = ref<TeamInvite[]>([])
const loading = ref(false)

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

// 生命周期
onMounted(async () => {
  await fetchMembers()
  await fetchInvites()
})

// 获取成员列表
const fetchMembers = async () => {
  try {
    loading.value = true
    const response = await teamMemberApi.getTeamMembers(props.teamId)
    members.value = response || []
  } catch (error: any) {
    ElMessage.error('获取成员列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取邀请列表
const fetchInvites = async () => {
  try {
    const response = await teamInviteApi.getInvites(props.teamId)
    invites.value = response || []
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
    await teamMemberApi.inviteMember(props.teamId, {
      email: inviteForm.value.email,
      role: inviteForm.value.role
    })
    
    ElMessage.success('邀请发送成功')
    showInviteDialog.value = false
    inviteForm.value = { email: '', role: 'team_member' }
    await fetchInvites()
    emit('refresh')
  } catch (error: any) {
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
    await fetchInvites()
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
    await teamMemberApi.updateMemberRole(props.teamId, selectedMember.value.id, {
      role: roleForm.value.role
    })
    
    ElMessage.success('角色变更成功')
    showRoleDialog.value = false
    await fetchMembers()
    emit('refresh')
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
    
    await teamMemberApi.removeMember(props.teamId, member.id)
    ElMessage.success('成员已移除')
    await fetchMembers()
    emit('refresh')
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
</script>

<style scoped>
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

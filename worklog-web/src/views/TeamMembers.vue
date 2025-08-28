<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { teamInviteApi, type TeamInvite } from '@/api/team-invite'
import { teamMemberApi, type TeamMember } from '@/api/teamMember'
import { api } from '@/api'

const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const members = ref<TeamMember[]>([])
const invites = ref<TeamInvite[]>([])
const showInviteDialog = ref(false)
const inviteForm = ref({
  email: '',
  role: 'team_member'
})

interface MemberCard {
  id: number
  email: string
  role: string
  isInvite: boolean
  created_at: string
  joined_at: string
  username?: string
  team_id?: number
  user_id?: number
  inviter_id?: number
  status?: string
  updated_at?: string
  inviter_name?: string
  team_name?: string
}

const formatDate = (date: string | undefined) => {
  if (!date) return '未知'
  try {
    return new Date(date).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('日期格式化错误:', error)
    return '未知'
  }
}

const allMembers = computed<MemberCard[]>(() => {
  const inviteCards: MemberCard[] = invites.value.map(invite => ({
    ...invite,
    isInvite: true,
    joined_at: '',
    created_at: invite.created_at || '',
    email: invite.email || '',
    role: invite.role || 'team_member',
    id: invite.id || 0,
  }))
  const memberCards: MemberCard[] = members.value.map(member => {
    if (!member || !member.user) {
      console.warn('Invalid member data:', member)
      return {
        id: 0,
        email: '',
        role: '',
        isInvite: false,
        created_at: '',
        joined_at: '',
      }
    }
    console.log('处理成员数据:', {
      id: member.id,
      created_at: member.created_at,
      user: member.user
    })
    return {
      id: member.id,
      team_id: member.team_id,
      user_id: member.user.id,
      username: member.user.username,
      email: member.user.email,
      role: member.role,
      isInvite: false,
      created_at: member.created_at,
      joined_at: member.created_at,
    }
  })
  return [...memberCards, ...inviteCards]
})

const canRemoveMember = (member: MemberCard) => {
  return userStore.userId !== member.user_id
}

const handleInvite = async () => {
  try {
    const teamId = Number(route.params.teamId)
    await teamInviteApi.createInvite(teamId, {
      email: inviteForm.value.email,
      role: inviteForm.value.role
    })
    showInviteDialog.value = false
    inviteForm.value = {
      email: '',
      role: 'team_member'
    }
    await fetchTeamData()
    ElMessage.success('邀请已发送')
  } catch (error) {
    console.error('发送邀请失败:', error)
    ElMessage.error('发送邀请失败')
  }
}

const handleResendInvite = async (member: MemberCard) => {
  try {
    await teamInviteApi.resendInvite(member.id)
    ElMessage.success('邀请已重新发送')
  } catch (error) {
    console.error('重新发送邀请失败:', error)
    ElMessage.error('重新发送邀请失败')
  }
}

const handleRemoveMember = async (member: MemberCard) => {
  try {
    if (!member.isInvite && member.team_id && member.user_id) {
      // 移除团队成员
      await teamMemberApi.deleteTeamMember(member.team_id, member.user_id)
      ElMessage.success('成员已移除')
    } else {
      // 撤销邀请
      await teamInviteApi.deleteInvite(member.id)
      ElMessage.success('邀请已撤销')
    }
    await fetchTeamData()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

const fetchTeamData = async () => {
  loading.value = true
  try {
    const teamId = Number(route.params.teamId)
    const [membersResponse, invitesResponse] = await Promise.all([
      teamMemberApi.getTeamMembers(teamId),
      teamInviteApi.getInvites(teamId)
    ])
    console.log('团队成员数据:', membersResponse.data)
    console.log('团队邀请数据:', invitesResponse.data)
    members.value = membersResponse.data
    invites.value = invitesResponse.data
  } catch (error) {
    console.error('获取团队数据失败:', error)
    ElMessage.error('获取团队数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTeamData()
})
</script>

<template>
  <div class="team-members">
    <div class="header">
      <h2>团队成员</h2>
      <el-button type="primary" @click="showInviteDialog = true">
        <el-icon><Plus /></el-icon>邀请成员
      </el-button>
    </div>

    <div class="members-grid">
      <!-- 所有成员和邀请卡片 -->
      <el-card v-for="member in allMembers" :key="member.id" class="member-card">
        <div class="card-header">
          <div class="user-info">
            <span class="nickname">{{ member.username || member.email }}</span>
            <el-tag v-if="member.isInvite" type="warning" size="small" class="invite-tag">已邀请</el-tag>
            <el-tag v-else type="success" size="small" class="member-tag">正式成员</el-tag>
          </div>
        </div>
        <div class="card-content">
          <div class="info-item">
            <span class="label">邮箱：</span>
            <span class="value">{{ member.email }}</span>
          </div>
          <div class="info-item">
            <span class="label">角色：</span>
            <span class="value">{{ member.role === 'team_admin' ? '管理员' : '成员' }}</span>
          </div>
          <!-- 正式成员显示加入时间 -->
          <div v-if="!member.isInvite" class="info-item">
            <span class="label">加入时间：</span>
            <span class="value">{{ formatDate(member.joined_at) }}</span>
          </div>
          <!-- 邀请显示创建时间 -->
          <div v-else class="info-item">
            <span class="label">邀请时间：</span>
            <span class="value">{{ formatDate(member.created_at) }}</span>
          </div>
        </div>
        <div class="card-footer">
          <template v-if="member.isInvite">
            <el-button type="primary" link @click="handleResendInvite(member)">重新发送</el-button>
            <el-button type="danger" link @click="handleRemoveMember(member)">撤销邀请</el-button>
          </template>
          <template v-else>
            <el-button 
              v-if="canRemoveMember(member)"
              type="danger" 
              link 
              @click="handleRemoveMember(member)"
            >
              移除成员
            </el-button>
          </template>
        </div>
      </el-card>
    </div>

    <!-- 邀请对话框 -->
    <el-dialog
      v-model="showInviteDialog"
      title="邀请新成员"
      width="500px"
    >
      <el-form :model="inviteForm" label-width="80px">
        <el-form-item label="邮箱">
          <el-input v-model="inviteForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="inviteForm.role" placeholder="请选择角色">
            <el-option label="成员" value="team_member" />
            <el-option label="管理员" value="team_admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInviteDialog = false">取消</el-button>
          <el-button type="primary" @click="handleInvite">发送邀请</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.team-members {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.member-card {
  height: 100%;
}

.card-header {
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nickname {
  font-size: 16px;
  font-weight: 500;
}

.card-content {
  margin-bottom: 15px;
}

.info-item {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.label {
  color: #666;
  margin-right: 8px;
  min-width: 70px;
}

.value {
  color: #333;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.invite-card {
  border: 1px solid #e6a23c;
}

.invite-tag {
  background-color: #fdf6ec;
  border-color: #faecd8;
  color: #e6a23c;
}

.member-tag {
  background-color: #f0f9eb;
  border-color: #e1f3d8;
  color: #67c23a;
}
</style> 
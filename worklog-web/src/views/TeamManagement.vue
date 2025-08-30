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

    <!-- 功能导航标签 -->
    <el-tabs v-model="activeTab" class="team-tabs" v-if="isMember" @tab-change="handleTabChange">
      <!-- 成员管理标签页 -->
      <el-tab-pane label="成员管理" name="members">
        <TeamMembers 
          :team-id="teamId" 
          :is-admin="isAdmin" 
          @refresh="handleRefresh"
        />
      </el-tab-pane>

      <!-- 项目列表标签页 -->
      <el-tab-pane label="项目列表" name="projects">
        <TeamProjects 
          :team-id="teamId" 
          :is-admin="isAdmin" 
          @refresh="handleRefresh"
        />
      </el-tab-pane>

      <!-- 团队动态标签页 -->
      <el-tab-pane label="团队动态" name="activities">
        <TeamActivities :team-id="teamId" />
      </el-tab-pane>

      <!-- 团队统计标签页 -->
      <el-tab-pane label="团队统计" name="statistics">
        <TeamStatistics :team-id="teamId" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { teamApi } from '@/api/team'
import { useUserStore } from '@/stores/user'

// 导入组件
import TeamMembers from '@/components/team/TeamMembers.vue'
import TeamProjects from '@/components/team/TeamProjects.vue'
import TeamActivities from '@/components/team/TeamActivities.vue'
import TeamStatistics from '@/components/team/TeamStatistics.vue'

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
const currentUserRole = ref('') // 当前用户在团队中的角色
const activeTab = ref('members')

// 计算属性：判断当前用户是否是团队管理员
const isAdmin = computed(() => currentUserRole.value === 'team_admin')

// 计算属性：判断当前用户是否是团队成员（包括管理员）
const isMember = computed(() => currentUserRole.value === 'team_admin' || currentUserRole.value === 'team_member')

// 生命周期加载数据
onMounted(async () => {
  await fetchTeamData()
})

// 获取团队数据
const fetchTeamData = async () => {
  try {
    const response = await teamApi.getTeam(teamId.value)
    team.value = response
    
    // 确定当前用户在团队中的角色
    const currentUserId = userStore.userId
    if (currentUserId && response.members) {
      const currentMember = response.members.find((member: any) => member.user_id === currentUserId)
      currentUserRole.value = currentMember?.role || ''
      console.log('当前用户ID:', currentUserId, '团队成员:', response.members, '当前用户角色:', currentUserRole.value)
    }
  } catch (error: any) {
    ElMessage.error('获取团队信息失败: ' + error.message)
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

// 处理标签页切换
const handleTabChange = (tabName: string) => {
  activeTab.value = tabName
}

// 处理刷新事件
const handleRefresh = () => {
  fetchTeamData()
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

.team-tabs {
  margin-top: 20px;
}
</style> 
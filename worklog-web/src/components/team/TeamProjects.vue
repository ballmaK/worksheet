<template>
  <el-card class="team-projects">
    <div class="card-header">
      <span>团队项目</span>
      <el-button type="primary" @click="createProject" v-if="isAdmin">新建项目</el-button>
    </div>
    
    <!-- 筛选条件 -->
    <div class="filter-section" style="margin-bottom: 16px;">
      <el-select v-model="projectFilter.status" placeholder="项目状态" style="width: 150px; margin-right: 10px;">
        <el-option label="全部状态" value="" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已完成" value="completed" />
        <el-option label="已暂停" value="paused" />
      </el-select>
      <el-input 
        v-model="projectFilter.keyword" 
        placeholder="搜索项目" 
        style="width: 200px; margin-right: 10px;"
        clearable
      />
      <el-button @click="fetchTeamProjects">搜索</el-button>
    </div>

    <!-- 项目列表 -->
    <el-table :data="teamProjects" v-loading="projectsLoading">
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="description" label="项目描述" show-overflow-tooltip />
      <el-table-column prop="progress" label="进度">
        <template #default="{ row }">
          <el-progress :percentage="row.progress" :status="getProgressStatus(row.progress)" />
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="负责人" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="viewProject(row)">查看详情</el-button>
          <el-button size="small" @click="editProject(row)" v-if="isAdmin">编辑项目</el-button>
          <el-button size="small" type="danger" @click="disassociateProject(row)" v-if="isAdmin">解除关联</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { teamApi, type TeamProject } from '@/api/team'

interface Props {
  teamId: number
  isAdmin: boolean
}

const props = defineProps<Props>()
const router = useRouter()

const emit = defineEmits<{
  refresh: []
}>()

// 数据定义
const teamProjects = ref<TeamProject[]>([])
const projectsLoading = ref(false)

// 筛选条件
const projectFilter = ref({
  status: '',
  keyword: ''
})

// 生命周期
onMounted(async () => {
  await fetchTeamProjects()
})

// 获取团队项目列表
const fetchTeamProjects = async () => {
  try {
    projectsLoading.value = true
    const response = await teamApi.getTeamProjects(props.teamId, {
      status: projectFilter.value.status || undefined,
      keyword: projectFilter.value.keyword || undefined
    })
    teamProjects.value = response || []
  } catch (error: any) {
    ElMessage.error('获取团队项目失败: ' + error.message)
  } finally {
    projectsLoading.value = false
  }
}

// 创建项目
const createProject = () => {
  router.push({ path: '/project/create', query: { teamId: props.teamId.toString() } })
}

// 查看项目
const viewProject = (row: TeamProject) => {
  router.push({ path: `/project/${row.id}` })
}

// 编辑项目
const editProject = (row: TeamProject) => {
  router.push({ path: `/project/${row.id}/edit` })
}

// 解除项目关联
const disassociateProject = (row: TeamProject) => {
  ElMessageBox.confirm(
    `确定要解除项目 ${row.name} 与团队的关联吗？`,
    '确认解除关联',
    { type: 'warning' }
  ).then(async () => {
    try {
      await teamApi.disassociateProject(props.teamId, row.id)
      ElMessage.success('项目关联已解除')
      await fetchTeamProjects()
      emit('refresh')
    } catch (error: any) {
      ElMessage.error('解除项目关联失败: ' + error.message)
    }
  }).catch(() => {
    // 用户取消
  })
}

// 获取进度状态
function getProgressStatus(progress: number) {
  if (progress >= 100) return 'success'
  if (progress >= 80) return 'warning'
  return ''
}

// 获取状态类型
function getStatusType(status: string) {
  switch (status) {
    case 'in_progress': return 'primary'
    case 'completed': return 'success'
    case 'paused': return 'warning'
    default: return 'info'
  }
}

// 获取状态文本
function getStatusText(status: string) {
  switch (status) {
    case 'in_progress': return '进行中'
    case 'completed': return '已完成'
    case 'paused': return '已暂停'
    default: return '未知'
  }
}
</script>

<style scoped>
.team-projects {
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

.filter-section {
  display: flex;
  align-items: center;
}
</style>

<template>
  <el-card class="team-activities">
    <div class="card-header">
      <span>团队动态</span>
      <div class="filter-section">
        <el-select v-model="activityFilter.type" placeholder="动态类型" style="width: 150px; margin-right: 10px;">
          <el-option label="全部动态" value="" />
          <el-option label="任务相关" value="task" />
          <el-option label="成员相关" value="member" />
          <el-option label="项目相关" value="project" />
        </el-select>
        <el-button @click="fetchTeamActivities">筛选</el-button>
      </div>
    </div>
    
    <!-- 动态时间线 -->
    <el-timeline v-loading="activitiesLoading">
      <el-timeline-item 
        v-for="activity in teamActivities" 
        :key="activity.id" 
        :timestamp="formatDate(activity.created_at)"
        :type="getActivityType(activity.activity_type)"
      >
        <div class="activity-content">
          <div class="activity-title">{{ activity.title }}</div>
          <div class="activity-content-text" v-if="activity.content">{{ activity.content }}</div>
        </div>
      </el-timeline-item>
    </el-timeline>
    
    <!-- 加载更多 -->
    <div v-if="teamActivities.length > 0" style="text-align: center; margin-top: 20px;">
      <el-button @click="loadMoreActivities" :loading="loadingMore">加载更多</el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { teamApi, type TeamActivity } from '@/api/team'

interface Props {
  teamId: number
}

const props = defineProps<Props>()

// 数据定义
const teamActivities = ref<TeamActivity[]>([])
const activitiesLoading = ref(false)
const loadingMore = ref(false)

// 筛选条件
const activityFilter = ref({
  type: '',
  start_date: '',
  end_date: ''
})

// 生命周期
onMounted(async () => {
  await fetchTeamActivities()
})

// 获取团队动态
const fetchTeamActivities = async () => {
  try {
    activitiesLoading.value = true
    const response = await teamApi.getTeamActivities(props.teamId, {
      activity_type: activityFilter.value.type || undefined,
      start_date: activityFilter.value.start_date || undefined,
      end_date: activityFilter.value.end_date || undefined
    })
    teamActivities.value = response || []
  } catch (error: any) {
    ElMessage.error('获取团队动态失败: ' + error.message)
  } finally {
    activitiesLoading.value = false
  }
}

// 加载更多动态
const loadMoreActivities = async () => {
  try {
    loadingMore.value = true
    const currentCount = teamActivities.value.length
    const response = await teamApi.getTeamActivities(props.teamId, {
      skip: currentCount,
      limit: 20,
      activity_type: activityFilter.value.type || undefined,
      start_date: activityFilter.value.start_date || undefined,
      end_date: activityFilter.value.end_date || undefined
    })
    teamActivities.value.push(...(response || []))
  } catch (error: any) {
    ElMessage.error('加载更多动态失败: ' + error.message)
  } finally {
    loadingMore.value = false
  }
}

// 工具函数
function formatDate(date: string) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 获取动态类型
function getActivityType(activityType: string) {
  if (activityType.includes('task')) return 'primary'
  if (activityType.includes('member')) return 'success'
  if (activityType.includes('project')) return 'warning'
  return 'info'
}
</script>

<style scoped>
.team-activities {
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

.activity-content {
  padding: 8px 0;
}

.activity-title {
  font-weight: 500;
  margin-bottom: 4px;
  color: #303133;
}

.activity-content-text {
  color: #606266;
  font-size: 14px;
}
</style>

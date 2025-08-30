<template>
  <el-card class="team-statistics">
    <div class="card-header">
      <span>团队统计</span>
      <el-button @click="fetchTeamStatistics">刷新</el-button>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ teamStatistics.member_count }}</div>
          <div class="stat-label">团队成员</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ teamStatistics.project_count }}</div>
          <div class="stat-label">关联项目</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ teamStatistics.worklog_count }}</div>
          <div class="stat-label">工作日志</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ teamStatistics.task_count }}</div>
          <div class="stat-label">任务数量</div>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { teamApi, type TeamStatistics } from '@/api/team'

interface Props {
  teamId: number
}

const props = defineProps<Props>()

// 数据定义
const teamStatistics = ref<TeamStatistics>({
  member_count: 0,
  project_count: 0,
  worklog_count: 0,
  task_count: 0
})

// 生命周期
onMounted(async () => {
  await fetchTeamStatistics()
})

// 获取团队统计信息
const fetchTeamStatistics = async () => {
  try {
    const response = await teamApi.getTeamStatistics(props.teamId)
    teamStatistics.value = response
  } catch (error: any) {
    ElMessage.error('获取团队统计失败: ' + error.message)
  }
}
</script>

<style scoped>
.team-statistics {
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

.stat-card {
  text-align: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}
</style>

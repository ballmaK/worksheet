<template>
  <div class="team-detail">
    <div class="header">
      <h1>团队详情</h1>
      <div class="actions">
        <el-button type="primary" @click="goToMembers">成员管理</el-button>
        <el-button type="primary" @click="goToProjects">项目管理</el-button>
        <el-button type="primary" @click="goToWorkLogs">工作日志</el-button>
      </div>
    </div>
    <p>这里将展示团队详细信息。</p>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const teamId = route.params.id

const goToMembers = () => {
  router.push(`/teams/${teamId}/members`)
}

const goToProjects = () => {
  router.push(`/teams/${teamId}/projects`)
}

const goToWorkLogs = () => {
  router.push(`/teams/${teamId}/work-logs`)
}
</script>

<style scoped>
.team-detail {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
}

.actions {
  display: flex;
  gap: 10px;
}
</style> 
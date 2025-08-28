<template>
  <div class="project-management">
    <!-- 项目信息 -->
    <el-card class="project-info">
      <div class="header">
        <h2>{{ project.name }}</h2>
        <el-tag :type="statusType(project.status)">{{ project.statusLabel }}</el-tag>
        <span>负责人：<el-avatar :src="project.owner?.avatar" /> {{ project.owner?.name }}</span>
        <span>起止：{{ formatDate(project.start_date) }} ~ {{ formatDate(project.end_date) }}</span>
        <el-button @click="editProject" type="primary">编辑项目</el-button>
      </div>
      <p>{{ project.description }}</p>
    </el-card>

    <!-- 项目成员 -->
    <el-card class="project-members" style="margin-top: 20px;">
      <div class="card-header">
        <span>项目成员</span>
        <el-button @click="inviteMember" type="primary">邀请成员</el-button>
      </div>
      <el-table :data="members">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="role" label="角色" />
        <el-table-column prop="joined_at" label="加入时间" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button v-if="isOwner" @click="removeMember(row)" size="small">移除</el-button>
            <el-button v-if="isOwner" @click="changeRole(row)" size="small">变更角色</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 进度与统计 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card>
          <div>总任务数：{{ statistics.total }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div>进行中：{{ statistics.in_progress }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div>已完成：{{ statistics.completed }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div>逾期：{{ statistics.overdue }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-progress :percentage="progressPercent" style="margin: 20px 0;" />

    <!-- 任务列表/看板 -->
    <el-card class="project-tasks" style="margin-top: 20px;">
      <div class="card-header">
        <span>项目任务</span>
        <el-button @click="createTask" type="primary">新建任务</el-button>
      </div>
      <!-- 可切换列表/看板视图 -->
      <task-board :tasks="tasks" v-if="viewMode==='board'" />
      <task-list :tasks="tasks" v-else />
    </el-card>

    <!-- 项目文档/附件（可选） -->
    <el-card class="project-files" style="margin-top: 20px;">
      <div class="card-header">
        <span>项目文档/附件</span>
        <el-button @click="uploadFile" type="primary">上传文档</el-button>
      </div>
      <el-table :data="files">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="uploaded_by" label="上传人" />
        <el-table-column prop="uploaded_at" label="上传时间" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button @click="downloadFile(row)" size="small">下载</el-button>
            <el-button @click="previewFile(row)" size="small">预览</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 项目动态/日志 -->
    <el-card class="project-logs" style="margin-top: 20px;">
      <div class="card-header">
        <span>项目动态</span>
      </div>
      <el-timeline>
        <el-timeline-item
          v-for="log in logs"
          :key="log.id"
          :timestamp="formatDate(log.created_at)"
        >
          {{ log.content }}
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
// 这里假设你有对应的API模块
// import { projectApi, taskApi, fileApi, logApi } from '@/api/project'

const route = useRoute()
const projectId = route.params.projectId

const project = ref<any>({})
const members = ref<any[]>([])
const statistics = ref({
  total: 0,
  in_progress: 0,
  completed: 0,
  overdue: 0
})
const tasks = ref<any[]>([])
const files = ref<any[]>([])
const logs = ref<any[]>([])
const viewMode = ref<'board' | 'list'>('board')

const isOwner = computed(() => {
  // 判断当前用户是否为项目负责人
  // return project.value.owner?.id === currentUserId
  return true
})

const progressPercent = computed(() => {
  if (!statistics.value.total) return 0
  return Math.round((statistics.value.completed / statistics.value.total) * 100)
})

function statusType(status: string) {
  switch (status) {
    case '进行中': return 'success'
    case '已完成': return 'info'
    case '暂停': return 'warning'
    case '归档': return 'danger'
    default: return ''
  }
}

function formatDate(date: string) {
  if (!date) return ''
  return date.split('T')[0]
}

function editProject() {
  ElMessage.info('编辑项目功能待实现')
}
function inviteMember() {
  ElMessage.info('邀请成员功能待实现')
}
function removeMember(row: any) {
  ElMessage.info('移除成员功能待实现')
}
function changeRole(row: any) {
  ElMessage.info('变更角色功能待实现')
}
function createTask() {
  ElMessage.info('新建任务功能待实现')
}
function uploadFile() {
  ElMessage.info('上传文档功能待实现')
}
function downloadFile(row: any) {
  ElMessage.info('下载功能待实现')
}
function previewFile(row: any) {
  ElMessage.info('预览功能待实现')
}

onMounted(() => {
  // 这里预留API调用，实际开发时对接后端
  // projectApi.getProject(projectId).then(res => project.value = res.data)
  // projectApi.getMembers(projectId).then(res => members.value = res.data)
  // taskApi.getStatistics(projectId).then(res => statistics.value = res.data)
  // taskApi.getTasks(projectId).then(res => tasks.value = res.data)
  // fileApi.getFiles(projectId).then(res => files.value = res.data)
  // logApi.getLogs(projectId).then(res => logs.value = res.data)
})
</script>

<style scoped>
.project-management {
  padding: 20px;
}
.project-info .header {
  display: flex;
  align-items: center;
  gap: 20px;
}
.project-info h2 {
  margin: 0;
  font-size: 24px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
</style> 
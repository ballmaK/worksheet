<template>
  <div class="work-log-form">
    <div class="header">
      <h1>工作日志</h1>
      <div class="actions">
        <el-button type="primary" @click="goToTeamView" v-if="currentTeam">
          团队视图
        </el-button>
      </div>
    </div>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="日期">
        <el-date-picker
          v-model="form.date"
          type="date"
          placeholder="选择日期"
          :disabled-date="disabledDate"
        />
      </el-form-item>
      <el-form-item label="项目">
        <el-select v-model="form.project_id" placeholder="选择项目">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="工作内容">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="4"
          placeholder="请输入工作内容"
        />
      </el-form-item>
      <el-form-item label="工时">
        <el-input-number
          v-model="form.hours"
          :min="0.5"
          :max="24"
          :step="0.5"
          :precision="1"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { workLogApi, type WorkLogCreate } from '@/api/workLog'
import { useRouter, useRoute } from 'vue-router'
import { projectApi } from '@/api/project'
import type { Project } from '@/api/project'

const router = useRouter()
const route = useRoute()
const currentTeam = ref<number | null>(null)

const props = defineProps<{
  teamId: number
}>()

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'cancel'): void
}>()

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive<WorkLogCreate>({
  team_id: props.teamId,
  date: new Date(),
  project_id: undefined as number | undefined,
  content: '',
  hours: 8
})

const rules: FormRules = {
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  project_id: [
    { required: true, message: '请选择项目', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入工作内容', trigger: 'blur' }
  ],
  hours: [
    { required: true, message: '请输入工时', trigger: 'blur' }
  ]
}

const projects = ref<Project[]>([])

const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

const loadProjects = async () => {
  try {
    const response = await projectApi.getProjects(props.teamId)
    projects.value = response.data
    if (projects.value.length > 0) {
      form.project_id = projects.value[0].id
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        await workLogApi.createWorkLog(form)
        ElMessage.success('工作日志提交成功')
        form.content = ''
        form.hours = 8
        router.push(`/teams/${props.teamId}/work-logs`)
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '提交失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const goToTeamView = () => {
  if (currentTeam.value) {
    router.push(`/teams/${currentTeam.value}/work-logs`)
  }
}

onMounted(() => {
  loadProjects()
  // 从路由参数中获取当前团队ID
  const teamId = route.query.team_id
  if (teamId) {
    currentTeam.value = Number(teamId)
  }
})
</script>

<style scoped>
.work-log-form {
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
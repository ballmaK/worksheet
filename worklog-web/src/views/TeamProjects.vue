<template>
  <div class="team-projects">
    <div class="header">
      <h2>团队项目管理</h2>
      <el-button type="primary" @click="showCreateDialog">创建项目</el-button>
    </div>

    <div class="project-cards" v-loading="loading">
      <el-card v-for="project in projects" :key="project.id" class="project-card">
        <template #header>
          <div class="card-header">
            <h3>{{ project.name }}</h3>
            <div class="card-actions">
              <el-button-group>
                <el-button size="small" @click="editProject(project)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteProject(project)">删除</el-button>
              </el-button-group>
            </div>
          </div>
        </template>
        <div class="card-content">
          <p class="description">{{ project.description || '暂无描述' }}</p>
          <p class="created-at">创建时间：{{ formatDate(project.created_at) }}</p>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑项目' : '创建项目'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="projectForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { projectApi } from '@/api/project'
import type { Project } from '@/types/project'
import { formatDate } from '@/utils/date'

const route = useRoute()
const teamId = Number(route.params.teamId)
const projects = ref<Project[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

const projectForm = reactive<ProjectCreate & { id?: number }>({
  name: '',
  description: '',
  team_id: teamId
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 获取项目列表
const loadProjects = async () => {
  loading.value = true
  try {
    const data = await projectApi.getProjects(teamId)
    console.log('Projects data:', data)
    projects.value = data
  } catch (error) {
    console.error('Load projects error:', error)
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  projectForm.name = ''
  projectForm.description = ''
  dialogVisible.value = true
}

// 编辑项目
const editProject = (row: Project) => {
  isEdit.value = true
  projectForm.id = row.id
  projectForm.name = row.name
  projectForm.description = row.description
  dialogVisible.value = true
}

// 删除项目
const deleteProject = async (row: Project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 ${row.name} 吗？`,
      '提示',
      { type: 'warning' }
    )
    await projectApi.deleteProject(row.id)
    ElMessage.success('项目删除成功')
    await loadProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '项目删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        if (isEdit.value) {
          await projectApi.updateProject(projectForm.id!, projectForm)
          ElMessage.success('项目更新成功')
        } else {
          await projectApi.createProject(projectForm)
          ElMessage.success('项目创建成功')
        }
        dialogVisible.value = false
        await loadProjects()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.team-projects {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.project-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.project-card {
  transition: all 0.3s ease;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.card-content {
  padding: 10px 0;
}

.description {
  color: #606266;
  margin: 10px 0;
  line-height: 1.5;
  min-height: 40px;
}

.created-at {
  color: #909399;
  font-size: 14px;
  margin: 10px 0 0;
}

.card-actions {
  display: flex;
  gap: 8px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style> 
<template>
  <div class="team-list">
    <div class="header">
      <h2>我的团队</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog">创建团队</el-button>
        <el-button type="success" @click="handleJoinTeam">
          <el-icon><UserFilled /></el-icon>
          加入团队
        </el-button>
      </div>
    </div>

    <div class="team-cards" v-loading="loading">
      <el-card v-for="team in teams" :key="team.id" class="team-card">
        <template #header>
          <div class="card-header">
            <h3>{{ team.name }}</h3>
            <div class="card-actions">
              <el-button-group>
                <el-button size="small" @click="handleManage(team)">管理</el-button>
              </el-button-group>
            </div>
          </div>
        </template>
        <div class="card-content">
          <p class="description">{{ team.description }}</p>
          <p class="created-at">创建时间：{{ new Date(team.created_at).toLocaleString() }}</p>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑团队对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑团队' : '创建团队'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入团队描述"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { teamApi, type Team, type CreateTeamData } from '@/api/team'
import { useRouter } from 'vue-router'
import { User, Calendar, UserFilled } from '@element-plus/icons-vue'

const teams = ref<Team[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const router = useRouter()

const form = reactive<CreateTeamData & { id?: number }>({
  name: '',
  description: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入团队名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入团队描述', trigger: 'blur' },
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 获取团队列表
const fetchTeams = async () => {
  try {
    loading.value = true
    const { data } = await teamApi.getTeams()
    console.log('Teams data:', data)
    teams.value = data
    console.log('Teams after update:', teams.value)
  } catch (error: any) {
    console.error('Error fetching teams:', error)
    ElMessage.error(error.response?.data?.message || '获取团队列表失败')
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

// 加入团队
const handleJoinTeam = () => {
  console.log('加入团队按钮被点击')
  router.push('/join-teams')
}

// 显示编辑对话框
const handleEdit = (row: Team) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.description = row.description
  dialogVisible.value = true
}

// 处理删除
const handleDelete = async (row: Team) => {
  try {
    await ElMessageBox.confirm('确定要删除该团队吗？', '提示', {
      type: 'warning'
    })
    await teamApi.deleteTeam(row.id)
    ElMessage.success('删除成功')
    fetchTeams()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
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
        if (isEdit.value && form.id) {
          const { id, ...updateData } = form
          await teamApi.updateTeam(id, updateData)
          ElMessage.success('更新成功')
        } else {
          await teamApi.createTeam(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchTeams()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 处理管理
const handleManage = (row: Team) => {
  router.push(`/teams/${row.id}/manage`)
}

onMounted(() => {
  fetchTeams()
})
</script>

<style scoped>
.team-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header h2 {
  margin: 0;
}

.team-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.team-card {
  height: 100%;
  transition: all 0.3s ease;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  margin-bottom: 10px;
  line-height: 1.5;
}

.created-at {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.meta-info {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  color: #909399;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item .el-icon {
  font-size: 16px;
}
</style> 
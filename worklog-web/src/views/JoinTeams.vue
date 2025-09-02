<template>
  <div class="join-teams-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>加入团队</h2>
        <span class="subtitle">发现并加入您感兴趣的团队</span>
      </div>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card" style="margin-bottom: 20px;">
      <div class="search-form">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索团队名称或描述..."
          class="search-input"
          clearable
          @input="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch" :loading="searching">
          搜索
        </el-button>
      </div>
    </el-card>

    <!-- 团队列表 -->
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>搜索结果 ({{ totalTeams }} 个团队)</span>
          <el-button type="primary" @click="refreshResults" :loading="refreshing">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 团队卡片列表 -->
      <div v-if="teams.length > 0" class="teams-grid">
        <el-card v-for="team in teams" :key="team.id" class="team-card">
          <template #header>
            <div class="card-header">
              <div class="team-title">
                <span class="team-name">{{ team.name }}</span>
                <div class="team-tags">
                  <el-tag type="success" size="small">公开团队</el-tag>
                </div>
              </div>
            </div>
          </template>
          
          <div class="team-info">
            <p class="description">{{ team.description || '暂无描述' }}</p>
            <div class="team-stats">
              <div class="stat-item">
                <el-icon><User /></el-icon>
                <span>{{ team.member_count }} 名成员</span>
              </div>
              <div class="stat-item">
                <el-icon><Folder /></el-icon>
                <span>{{ team.project_count }} 个项目</span>
              </div>
              <div class="stat-item">
                <el-icon><Calendar /></el-icon>
                <span>创建于 {{ formatDate(team.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-actions">
            <el-button type="primary" @click="handleShowJoinDialog(team)" :loading="joiningTeam === team.id">
              申请加入
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="!loading" description="暂无搜索结果">
        <el-button type="primary" @click="handleSearch">重新搜索</el-button>
      </el-empty>

      <!-- 分页 -->
      <div v-if="totalTeams > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="totalTeams"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 申请加入对话框 -->
    <el-dialog
      v-model="showJoinDialog"
      title="申请加入团队"
      width="500px"
    >
      <el-form
        ref="joinFormRef"
        :model="joinForm"
        :rules="joinRules"
        label-width="80px"
      >
        <el-form-item label="团队名称">
          <el-input :value="selectedTeam?.name" disabled />
        </el-form-item>
        <el-form-item label="申请留言" prop="message">
          <el-input
            v-model="joinForm.message"
            type="textarea"
            :rows="4"
            placeholder="请简单介绍一下您为什么想加入这个团队..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showJoinDialog = false">取消</el-button>
          <el-button type="primary" @click="handleJoinTeam" :loading="joining">
            提交申请
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Search, Refresh, User, Folder, Calendar } from '@element-plus/icons-vue'
import { teamApi, type TeamSearchResult } from '@/api/team'
import { formatDate } from '@/utils/date'

// 数据定义
const teams = ref<TeamSearchResult[]>([])
const loading = ref(false)
const searching = ref(false)
const refreshing = ref(false)
const joining = ref(false)
const joiningTeam = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalTeams = ref(0)
const searchKeyword = ref('')

// 对话框相关
const showJoinDialog = ref(false)
const selectedTeam = ref<TeamSearchResult | null>(null)
const joinFormRef = ref<FormInstance>()
const joinForm = reactive({
  message: ''
})

const joinRules: FormRules = {
  message: [
    { required: true, message: '请输入申请留言', trigger: 'blur' },
    { min: 10, max: 200, message: '留言长度在 10 到 200 个字符', trigger: 'blur' }
  ]
}

// 生命周期
onMounted(() => {
  searchTeams()
})

// 搜索团队
const searchTeams = async () => {
  try {
    loading.value = true
    const response = await teamApi.searchPublicTeams({
      keyword: searchKeyword.value || undefined,
      page: currentPage.value,
      size: pageSize.value
    })
    
    if (Array.isArray(response)) {
      teams.value = response
      totalTeams.value = response.length // 注意：这里后端应该返回总数
    } else {
      teams.value = []
      totalTeams.value = 0
    }
  } catch (error: any) {
    ElMessage.error('搜索团队失败: ' + (error.response?.data?.detail || error.message))
    teams.value = []
    totalTeams.value = 0
  } finally {
    loading.value = false
    searching.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  searchTeams()
}

// 刷新结果
const refreshResults = async () => {
  refreshing.value = true
  await searchTeams()
  refreshing.value = false
}

// 显示加入对话框
const handleShowJoinDialog = (team: TeamSearchResult) => {
  selectedTeam.value = team
  joinForm.message = ''
  showJoinDialog.value = true
}

// 处理加入团队
const handleJoinTeam = async () => {
  if (!joinFormRef.value || !selectedTeam.value) return
  
  try {
    await joinFormRef.value.validate()
  } catch (error) {
    return
  }

  try {
    joining.value = true
    joiningTeam.value = selectedTeam.value.id
    
    await teamApi.joinTeam(selectedTeam.value.id, {
      message: joinForm.message
    })
    
    ElMessage.success('申请已提交，请等待管理员审核')
    showJoinDialog.value = false
    
    // 从列表中移除已申请的团队
    teams.value = teams.value.filter(t => t.id !== selectedTeam.value!.id)
    totalTeams.value = Math.max(0, totalTeams.value - 1)
    
  } catch (error: any) {
    ElMessage.error('申请失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    joining.value = false
    joiningTeam.value = null
  }
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  searchTeams()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  searchTeams()
}
</script>

<style scoped>
.join-teams-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.search-card {
  background: #f8f9fa;
}

.search-form {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.team-card {
  height: 100%;
  transition: all 0.3s ease;
}

.team-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.team-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.team-info {
  margin: 16px 0;
}

.description {
  color: #606266;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.team-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}

.card-actions {
  margin-top: 16px;
  text-align: right;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .teams-grid {
    grid-template-columns: 1fr;
  }
  
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    margin-bottom: 12px;
  }
}
</style>

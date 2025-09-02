<template>
  <div class="team-join-requests-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>团队加入申请管理</h2>
        <span class="subtitle">{{ teamName }}</span>
      </div>
      <div class="header-actions">
        <el-button @click="refreshRequests" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total }}</div>
            <div class="stat-label">总申请数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.pending }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.approved }}</div>
            <div class="stat-label">已批准</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.rejected }}</div>
            <div class="stat-label">已拒绝</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <el-card style="margin-bottom: 20px;">
      <div class="filter-section">
        <div class="filter-left">
          <el-select v-model="filters.status" placeholder="申请状态" clearable style="width: 120px; margin-right: 10px;">
            <el-option label="待处理" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名或邮箱"
            style="width: 200px; margin-right: 10px;"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>
    </el-card>

    <!-- 申请列表 -->
    <el-card>
      <el-table :data="filteredRequests" style="width: 100%" v-loading="loading">
        <el-table-column prop="username" label="申请人" min-width="120">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="32" :src="getUserAvatar(row.username)">
                {{ row.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="user-details">
                <div class="username">{{ row.username }}</div>
                <div class="email">{{ row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="申请留言" min-width="300" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="处理时间" width="150">
          <template #default="{ row }">
            {{ row.status === 'pending' ? '-' : formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending'"
              size="small" 
              type="success" 
              @click="handleApprove(row)"
              :loading="processingRequest === row.id"
            >
              批准
            </el-button>
            <el-button 
              v-if="row.status === 'pending'"
              size="small" 
              type="danger" 
              @click="handleReject(row)"
              :loading="processingRequest === row.id"
            >
              拒绝
            </el-button>
            <el-button 
              v-if="row.status !== 'pending'"
              size="small" 
              type="info" 
              @click="viewRequestDetails(row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="totalRequests > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalRequests"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-empty v-if="filteredRequests.length === 0 && !loading" description="暂无加入申请" />

    <!-- 申请详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      title="申请详情"
      width="600px"
    >
      <div v-if="selectedRequest" class="request-details">
        <div class="detail-item">
          <label>申请人：</label>
          <span>{{ selectedRequest.username }}</span>
        </div>
        <div class="detail-item">
          <label>邮箱：</label>
          <span>{{ selectedRequest.email }}</span>
        </div>
        <div class="detail-item">
          <label>申请时间：</label>
          <span>{{ formatDate(selectedRequest.created_at) }}</span>
        </div>
        <div class="detail-item">
          <label>处理时间：</label>
          <span>{{ selectedRequest.status === 'pending' ? '未处理' : formatDate(selectedRequest.updated_at) }}</span>
        </div>
        <div class="detail-item">
          <label>状态：</label>
          <el-tag :type="getStatusType(selectedRequest.status)" size="small">
            {{ getStatusText(selectedRequest.status) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>申请留言：</label>
          <div class="message-content">{{ selectedRequest.message }}</div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDetailsDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, ArrowLeft, Search } from '@element-plus/icons-vue'
import { teamApi, type TeamJoinRequest } from '@/api/team'
import { formatDate } from '@/utils/date'

const router = useRouter()
const route = useRoute()

// 获取团队ID
const teamId = parseInt(route.params.teamId as string)
const teamName = ref('团队')

// 数据定义
const requests = ref<TeamJoinRequest[]>([])
const loading = ref(false)
const refreshing = ref(false)
const processingRequest = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalRequests = ref(0)
const searchKeyword = ref('')

// 筛选条件
const filters = ref({
  status: null
})

// 统计信息
const statistics = computed(() => {
  const total = requests.value.length
  const pending = requests.value.filter(r => r.status === 'pending').length
  const approved = requests.value.filter(r => r.status === 'approved').length
  const rejected = requests.value.filter(r => r.status === 'rejected').length
  
  return { total, pending, approved, rejected }
})

// 对话框相关
const showDetailsDialog = ref(false)
const selectedRequest = ref<TeamJoinRequest | null>(null)

// 计算属性
const filteredRequests = computed(() => {
  let result = requests.value

  // 状态过滤
  if (filters.value.status) {
    result = result.filter(request => request.status === filters.value.status)
  }

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(request => 
      request.username.toLowerCase().includes(keyword) ||
      request.email.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 生命周期
onMounted(async () => {
  await fetchRequests()
  await fetchTeamInfo()
})

// 获取团队信息
const fetchTeamInfo = async () => {
  try {
    // 这里应该调用获取团队详情的API
    // 暂时使用路由参数
    teamName.value = `团队 ${teamId}`
  } catch (error) {
    console.error('获取团队信息失败:', error)
  }
}

// 获取加入申请列表
const fetchRequests = async () => {
  try {
    loading.value = true
    const response = await teamApi.getTeamJoinRequests(teamId)
    requests.value = response || []
    totalRequests.value = requests.value.length
  } catch (error: any) {
    ElMessage.error('获取加入申请失败: ' + (error.response?.data?.detail || error.message))
    requests.value = []
    totalRequests.value = 0
  } finally {
    loading.value = false
  }
}

// 刷新申请列表
const refreshRequests = async () => {
  refreshing.value = true
  await fetchRequests()
  refreshing.value = false
}

// 批准申请
const handleApprove = async (request: TeamJoinRequest) => {
  try {
    await ElMessageBox.confirm(
      `确定要批准用户 "${request.username}" 的加入申请吗？`,
      '确认批准',
      { type: 'warning' }
    )
    
    processingRequest.value = request.id
    await teamApi.approveJoinRequest(teamId, request.id)
    
    ElMessage.success('申请已批准，用户已加入团队')
    await fetchRequests() // 刷新列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批准申请失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    processingRequest.value = null
  }
}

// 拒绝申请
const handleReject = async (request: TeamJoinRequest) => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝用户 "${request.username}" 的加入申请吗？`,
      '确认拒绝',
      { type: 'warning' }
    )
    
    processingRequest.value = request.id
    await teamApi.rejectJoinRequest(teamId, request.id)
    
    ElMessage.success('申请已拒绝')
    await fetchRequests() // 刷新列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('拒绝申请失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    processingRequest.value = null
  }
}

// 查看申请详情
const viewRequestDetails = (request: TeamJoinRequest) => {
  selectedRequest.value = request
  showDetailsDialog.value = true
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    status: null
  }
  searchKeyword.value = ''
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 工具函数
const getStatusType = (status: string) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待处理'
    case 'approved': return '已批准'
    case 'rejected': return '已拒绝'
    default: return '未知'
  }
}

const getUserAvatar = (username: string) => {
  // 这里可以根据用户名生成头像或使用默认头像
  return ''
}
</script>

<style scoped>
.team-join-requests-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-left {
  display: flex;
  align-items: center;
}

.filter-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-weight: 500;
  color: #303133;
}

.email {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.request-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.detail-item label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.detail-item span {
  color: #303133;
}

.message-content {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  color: #606266;
  line-height: 1.5;
  white-space: pre-wrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

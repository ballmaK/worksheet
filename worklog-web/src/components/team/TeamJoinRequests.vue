<template>
  <el-card class="team-join-requests">
    <div class="card-header">
      <span>加入申请 ({{ joinRequests.length }})</span>
      <div class="header-actions">
        <el-button @click="refreshRequests" :loading="refreshing" size="small">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 申请列表 -->
    <div v-if="joinRequests.length === 0" style="text-align: center; color: #999; padding: 20px;">
      暂无加入申请
    </div>
    <el-table v-else :data="joinRequests" v-loading="loading">
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
      <el-table-column label="操作" width="200">
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
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { teamApi, type TeamJoinRequest } from '@/api/team'
import { formatDate } from '@/utils/date'

// Props
interface Props {
  teamId: number
}

const props = defineProps<Props>()

// 数据定义
const joinRequests = ref<TeamJoinRequest[]>([])
const loading = ref(false)
const refreshing = ref(false)
const processingRequest = ref<number | null>(null)

// 对话框相关
const showDetailsDialog = ref(false)
const selectedRequest = ref<TeamJoinRequest | null>(null)

// 生命周期
onMounted(async () => {
  await fetchRequests()
})

// 获取加入申请列表
const fetchRequests = async () => {
  try {
    loading.value = true
    const response = await teamApi.getTeamJoinRequests(props.teamId)
    joinRequests.value = response || []
  } catch (error: any) {
    ElMessage.error('获取加入申请失败: ' + (error.response?.data?.detail || error.message))
    joinRequests.value = []
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
    await teamApi.approveJoinRequest(props.teamId, request.id)
    
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
    await teamApi.rejectJoinRequest(props.teamId, request.id)
    
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
.team-join-requests {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header span {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
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

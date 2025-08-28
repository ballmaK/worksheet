<template>
  <div class="team-work-logs">
    <el-card class="filter-card">
      <div class="filter-header">
        <h3>工作日志筛选</h3>
      </div>
      
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="成员">
          <el-select v-model="filterForm.memberId" placeholder="选择成员" clearable>
            <el-option
              v-for="member in teamMembers"
              :key="member.id"
              :label="member.username"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="项目">
          <el-select v-model="filterForm.projectId" placeholder="选择项目" clearable>
            <el-option
              v-for="project in teamProjects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :shortcuts="dateShortcuts"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="exportWorkLogs">导出</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="work-logs-card">
      <template #header>
        <div class="card-header">
          <h3>团队工作日志</h3>
          <div class="header-actions">
            <el-button type="primary" @click="refreshWorkLogs">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="workLogs"
        style="width: 100%"
        border
      >
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="username" label="成员" width="120" />
        
        <el-table-column prop="project_name" label="项目" width="150" />
        
        <el-table-column prop="content" label="工作内容" min-width="300">
          <template #default="{ row }">
            <div class="work-content">
              <p>{{ row.content }}</p>
              <div v-if="row.comments" class="comments">
                <div v-for="comment in row.comments" :key="comment.id" class="comment">
                  <span class="comment-user">{{ comment.username }}:</span>
                  <span class="comment-content">{{ comment.content }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="hours" label="工时" width="100" />
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="handleComment(row)"
            >
              评论
            </el-button>
            <el-button
              type="success"
              link
              @click="handleApprove(row)"
              v-if="row.status === 'pending'"
            >
              审核
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 评论对话框 -->
    <el-dialog
      v-model="showCommentDialog"
      title="添加评论"
      width="500px"
    >
      <el-form :model="commentForm" label-width="80px">
        <el-form-item label="评论内容">
          <el-input
            v-model="commentContent"
            type="textarea"
            :rows="4"
            placeholder="请输入评论内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCommentDialog = false">取消</el-button>
          <el-button type="primary" @click="submitComment">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { workLogApi } from '@/api/workLog'
import { teamMemberApi, type TeamMember } from '@/api/team-member'
import { projectApi } from '@/api/project'
import type { Project } from '@/types/project'
import type { WorkLog } from '@/types/worklog'
import { formatDate } from '@/utils/date'

const route = useRoute()
const teamId = ref(Number(route.params.teamId))
const teamMembers = ref<TeamMember[]>([])
const projects = ref<Project[]>([])
const workLogs = ref<WorkLog[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const showCommentDialog = ref(false)
const commentContent = ref('')
const currentWorkLog = ref<WorkLog | null>(null)

// 筛选表单
const filterForm = reactive({
  memberId: null,
  projectId: null,
  dateRange: []
})

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  }
]

// 加载团队成员
const loadTeamMembers = async () => {
  try {
    const response = await teamMemberApi.getTeamMembers(teamId.value)
    teamMembers.value = response.data
  } catch (error) {
    ElMessage.error('加载团队成员失败')
  }
}

// 加载团队项目
const loadTeamProjects = async () => {
  try {
    const response = await projectApi.getProjects(teamId.value)
    projects.value = response.data
  } catch (error) {
    ElMessage.error('加载团队项目失败')
  }
}

// 加载工作日志
const loadWorkLogs = async () => {
  try {
    const params = {
      team_id: teamId.value,
      page: currentPage.value,
      page_size: pageSize.value,
      member_id: filterForm.memberId,
      project_id: filterForm.projectId,
      start_date: filterForm.dateRange[0] ? new Date(filterForm.dateRange[0]).toISOString() : undefined,
      end_date: filterForm.dateRange[1] ? new Date(filterForm.dateRange[1]).toISOString() : undefined
    }
    
    const response = await workLogApi.getTeamWorkLogs(params)
    workLogs.value = response.data.items
    total.value = response.data.total
  } catch (error: any) {
    console.error('加载工作日志失败:', error)
    ElMessage.error(error.response?.data?.message || '加载工作日志失败，请检查网络连接')
  }
}

// 处理筛选
const handleFilter = () => {
  currentPage.value = 1
  loadWorkLogs()
}

// 重置筛选
const resetFilter = () => {
  filterForm.memberId = null
  filterForm.projectId = null
  filterForm.dateRange = []
  handleFilter()
}

// 处理分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadWorkLogs()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadWorkLogs()
}

// 刷新工作日志
const refreshWorkLogs = () => {
  loadWorkLogs()
}

// 处理评论
const handleComment = (row: WorkLog) => {
  currentWorkLog.value = row
  showCommentDialog.value = true
}

// 提交评论
const submitComment = async () => {
  if (!currentWorkLog.value) return
  
  try {
    await workLogApi.addComment(currentWorkLog.value.id, {
      content: commentContent.value
    })
    ElMessage.success('评论成功')
    showCommentDialog.value = false
    commentContent.value = ''
    await loadWorkLogs()
  } catch (error) {
    ElMessage.error('评论失败')
  }
}

// 处理审批
const handleApprove = async (row: WorkLog) => {
  try {
    await workLogApi.approveWorkLog(row.id)
    ElMessage.success('审批成功')
    await loadWorkLogs()
  } catch (error) {
    ElMessage.error('审批失败')
  }
}

// 导出工作日志
const exportWorkLogs = async () => {
  try {
    const params = {
      team_id: teamId.value,
      member_id: filterForm.memberId,
      project_id: filterForm.projectId,
      start_date: filterForm.dateRange[0],
      end_date: filterForm.dateRange[1]
    }
    
    const response = await workLogApi.exportTeamWorkLogs(params)
    const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `团队工作日志_${formatDate(new Date())}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadTeamMembers()
  loadTeamProjects()
  loadWorkLogs()
})
</script>

<style scoped>
.team-work-logs {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-header {
  margin-bottom: 20px;
}

.filter-header h3 {
  margin: 0;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.work-content {
  white-space: pre-wrap;
}

.comments {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.comment {
  margin-bottom: 5px;
}

.comment-user {
  font-weight: bold;
  margin-right: 5px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 
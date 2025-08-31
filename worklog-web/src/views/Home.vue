<template>
  <div class="home-container">
    <!-- 移除工作模式切换按钮，改为使用专门的工作模式卡片 -->

    <!-- 核心功能区 - 最重要的内容 -->
    <el-row :gutter="20" class="core-section">
      <!-- 任务管理 - 最重要的功能，占用最大空间 -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="task-management-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">📋 任务管理</span>
              <el-button type="primary" @click="$router.push('/tasks')">
                管理任务
              </el-button>
            </div>
          </template>
          <div class="task-stats">
            <div class="main-stat">
              <div class="stat-number">{{ stats.totalTasks }}</div>
              <div class="stat-text">总任务数</div>
            </div>
            <div class="task-breakdown">
              <div class="breakdown-item pending">
                <span class="count">{{ stats.pendingTasks }}</span>
                <span class="label">待处理</span>
              </div>
              <div class="breakdown-item in-progress">
                <span class="count">{{ stats.inProgressTasks }}</span>
                <span class="label">进行中</span>
              </div>
              <div class="breakdown-item completed">
                <span class="count">{{ stats.completedTasks }}</span>
                <span class="label">已完成</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 工作模式 - 重要功能，中等空间 -->
      <el-col :xs="24" :lg="12">
        <WorkModeCard />
      </el-col>
    </el-row>

    <!-- 次要功能区 -->
    <el-row :gutter="20" class="secondary-section">
      <!-- 项目统计 - 重要但次于任务 -->
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>📁 项目统计</span>
              <el-button type="primary" link @click="$router.push('/projects')">
                查看全部
              </el-button>
            </div>
          </template>
          <div class="stat-value">{{ stats.totalProjects }}</div>
          <div class="stat-label">
            <div>总项目数</div>
            <div class="sub-stats">
              <span class="active">进行中: {{ stats.activeProjects }}</span>
              <span class="completed">已完成: {{ stats.completedProjects }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 工作日志 - 重要但次于项目 -->
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>📝 本周工作日志</span>
              <el-button type="primary" link @click="$router.push('/worklogs')">
                查看全部
              </el-button>
            </div>
          </template>
          <div class="stat-value">{{ stats.weeklyWorkLogs }}</div>
          <div class="stat-label">条记录</div>
        </el-card>
      </el-col>
      
      <!-- 团队统计 - 相对次要 -->
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>👥 我的团队</span>
              <el-button type="primary" link @click="$router.push('/teams')">
                查看全部
              </el-button>
            </div>
          </template>
          <div class="stat-value">{{ stats.totalTeams }}</div>
          <div class="stat-label">个团队</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作区 -->
    <el-row :gutter="20" class="quick-actions-section">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="quick-action-card" @click="$router.push('/tasks')">
          <div class="action-content">
            <el-icon class="action-icon"><Setting /></el-icon>
            <div class="action-text">
              <div class="action-title">快速创建任务</div>
              <div class="action-desc">开始新的工作任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="quick-action-card" @click="$router.push('/worklogs')">
          <div class="action-content">
            <el-icon class="action-icon"><Timer /></el-icon>
            <div class="action-text">
              <div class="action-title">记录工作日志</div>
              <div class="action-desc">记录今日工作内容</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="quick-action-card" @click="$router.push('/download')">
          <div class="action-content">
            <el-icon class="action-icon"><Download /></el-icon>
            <div class="action-text">
              <div class="action-title">下载桌面客户端</div>
              <div class="action-desc">享受更好的工作体验</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="quick-action-card" @click="$router.push('/calendar')">
          <div class="action-content">
            <el-icon class="action-icon"><Calendar /></el-icon>
            <div class="action-text">
              <div class="action-title">查看日历</div>
              <div class="action-desc">查看日程安排</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 团队和项目列表 -->
    <el-row :gutter="20" class="content-section">
      <el-col :xs="24" :lg="12">
        <el-card class="team-list">
          <template #header>
            <div class="card-header">
              <span>我的团队</span>
              <el-button type="primary" @click="$router.push('/teams')">
                管理
              </el-button>
            </div>
          </template>
          <el-empty v-if="teams.length === 0" description="暂无团队" />
          <el-scrollbar v-else height="400px">
            <div v-for="team in teams" :key="team.id" class="team-item">
              <div class="team-info">
                <h3>{{ team.name }}</h3>
                <p>{{ team.description }}</p>
                <div class="team-meta">
                  <span class="meta-item"><el-icon><User /></el-icon> {{ team.members?.length || 0 }} 名成员</span>
                  <span class="meta-item"><el-icon><Folder /></el-icon> {{ team.projects?.length || 0 }} 个项目</span>
                </div>
              </div>
              <div class="team-actions">
                <el-button type="primary" link @click="$router.push(`/teams/${team.id}/manage`)">
                  管理
                </el-button>
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="project-list">
          <template #header>
            <div class="card-header">
              <span>我的项目</span>
              <el-button type="primary" @click="$router.push('/projects')">
                管理
              </el-button>
            </div>
          </template>
          <el-empty v-if="myProjects.length === 0" description="暂无项目" />
          <el-scrollbar v-else height="400px">
            <div v-for="project in myProjects" :key="project.id" class="project-item">
              <div class="project-info">
                <h3>{{ project.name }}</h3>
                <p>{{ project.description }}</p>
                <div class="project-meta">
                  <el-tag size="small" :type="project.status === 'in_progress' ? 'success' : (project.status === 'completed' ? 'info' : 'default')">
                    {{ project.status === 'in_progress' ? '进行中' : (project.status === 'completed' ? '已完成' : project.status) }}
                  </el-tag>
                  <span><el-icon><Calendar /></el-icon> {{ formatDate(project.start_date) }}</span>
                </div>
              </div>
              <div class="project-actions">
                <el-button type="primary" link @click="$router.push(`/projects/${project.id}`)">
                  查看
                </el-button>
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Folder, Calendar, Refresh, Timer, Setting, Download } from '@element-plus/icons-vue'
import WorkModeCard from '@/components/WorkModeCard.vue'
import { teamApi } from '@/api/team'
import { projectApi } from '@/api/project'
import { useUserStore } from '@/stores/user'
import { workLogApi } from '@/api/workLog'
import { teamMemberApi } from '@/api/teamMember'
import { taskApi } from '@/api/task'
import { formatDate } from '@/utils/date'
import request from '@/utils/request'

const userStore = useUserStore()
const teams = ref([])
const myProjects = ref([])
const weeklyWorkLogs = ref([])
const todos = ref([])
const stats = ref({
  totalTeams: 0,
  activeProjects: 0,
  completedProjects: 0,
  totalProjects: 0,
  weeklyWorkLogs: 0,
  totalTasks: 0,
  pendingTasks: 0,
  inProgressTasks: 0,
  completedTasks: 0
})

const refreshStats = async () => {
  await fetchData()
  ElMessage.success('统计数据已刷新')
}

const fetchData = async () => {
  try {
    // 获取当前用户
    const currentUser = await request.get('/users/me')
    
    // 获取团队列表
    const teamsResponse = await teamApi.getTeams()
    let teamsData: any[] = []
    
    if (teamsResponse && typeof teamsResponse === 'object') {
      const responseData = teamsResponse as any
      if (responseData.data) {
        if (responseData.data.items && Array.isArray(responseData.data.items)) {
          teamsData = responseData.data.items
        } else if (Array.isArray(responseData.data)) {
          teamsData = responseData.data
        }
      } else if (responseData.items && Array.isArray(responseData.items)) {
        teamsData = responseData.items
      } else if (Array.isArray(responseData)) {
        teamsData = responseData
      }
    }
    
    // 获取每个团队的成员信息和项目信息
    const teamsWithDetails = await Promise.all(
      teamsData.map(async (team: any) => {
        const [membersResponse, projectsResponse] = await Promise.all([
          teamMemberApi.getTeamMembers(team.id),
          projectApi.getProjects(team.id)  // 这里传入team.id来获取该团队的项目
        ])
        
        // 处理成员响应
        let members: any[] = []
        if (membersResponse && typeof membersResponse === 'object') {
          const membersData = membersResponse as any
          if (membersData.data) {
            members = Array.isArray(membersData.data) ? membersData.data : []
          } else if (Array.isArray(membersData)) {
            members = membersData
          }
        }
        
        // 处理项目响应
        let projects: any[] = []
        if (projectsResponse && typeof projectsResponse === 'object') {
          const projectsData = projectsResponse as any
          if (projectsData.data) {
            projects = Array.isArray(projectsData.data) ? projectsData.data : []
          } else if (Array.isArray(projectsData)) {
            projects = projectsData
          }
        }
        
        return {
          ...team,
          members,
          projects
        }
      })
    )
    
    teams.value = teamsWithDetails

    // 获取我的项目
    if (currentUser?.id) {
      const myProjectsResponse = await projectApi.getProjects(undefined, currentUser.id)
      let myProjectsData: any[] = []
      
      if (myProjectsResponse && typeof myProjectsResponse === 'object') {
        const responseData = myProjectsResponse as any
        if (responseData.data) {
          if (responseData.data.items && Array.isArray(responseData.data.items)) {
            myProjectsData = responseData.data.items
          } else if (Array.isArray(responseData.data)) {
            myProjectsData = responseData.data
          }
        } else if (responseData.items && Array.isArray(responseData.items)) {
          myProjectsData = responseData.items
        } else if (Array.isArray(responseData)) {
          myProjectsData = responseData
        }
      }
      
      myProjects.value = myProjectsData
    } else {
      myProjects.value = []
    }

    // 统计所有团队的项目
    const allProjects = teamsWithDetails.flatMap((team: any) => team.projects)
    console.log('【Home】所有项目:', allProjects)
    console.log('【Home】项目数量:', allProjects.length)
    
    // 按状态分类项目
    const activeProjects = allProjects.filter((p: any) => p.status === 'in_progress')
    const completedProjects = allProjects.filter((p: any) => p.status === 'completed')
    const totalProjects = allProjects.length
    
    console.log('【Home】进行中项目:', activeProjects)
    console.log('【Home】已完成项目:', completedProjects)
    console.log('【Home】项目统计:', {
      total: totalProjects,
      active: activeProjects.length,
      completed: completedProjects.length
    })

    // 获取本周工作日志
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 7)
    const workLogsResponse = await workLogApi.getWorkLogs({
      page: 1,
      page_size: 100,
      start_date: startDate.toISOString(),
      end_date: new Date().toISOString()
    })
    
    // 处理工作日志响应格式
    let workLogsData: any[] = []
    if (workLogsResponse && typeof workLogsResponse === 'object') {
      const responseData = workLogsResponse as any
      if (responseData.data) {
        if (responseData.data.items && Array.isArray(responseData.data.items)) {
          workLogsData = responseData.data.items
        } else if (Array.isArray(responseData.data)) {
          workLogsData = responseData.data
        }
      } else if (responseData.items && Array.isArray(responseData.items)) {
        workLogsData = responseData.items
      } else if (Array.isArray(responseData)) {
        workLogsData = responseData
      }
    }
    
    weeklyWorkLogs.value = workLogsData

    // 获取任务统计
    let totalTasks = 0
    let pendingTasks = 0
    let inProgressTasks = 0
    let completedTasks = 0
    
    try {
      const tasksResponse = await taskApi.getTasks({
        page: 1,
        page_size: 100
      })
      
      // 处理任务响应格式
      let tasksData: any[] = []
      if (tasksResponse && typeof tasksResponse === 'object') {
        const responseData = tasksResponse as any
        if (responseData.data) {
          if (responseData.data.items && Array.isArray(responseData.data.items)) {
            tasksData = responseData.data.items
          } else if (Array.isArray(responseData.data)) {
            tasksData = responseData.data
          }
        } else if (responseData.items && Array.isArray(responseData.items)) {
          tasksData = responseData.items
        } else if (Array.isArray(responseData)) {
          tasksData = responseData
        }
      }
      
      totalTasks = tasksData.length
      
      // 按状态统计任务
      pendingTasks = tasksData.filter(task => task.status === 'pending').length
      inProgressTasks = tasksData.filter(task => task.status === 'in_progress').length
      completedTasks = tasksData.filter(task => task.status === 'completed').length
    } catch (error) {
      console.warn('获取任务数据失败:', error)
    }

    // 更新统计信息
    stats.value = {
      totalTeams: teamsData.length,
      activeProjects: activeProjects.length,
      completedProjects: completedProjects.length,
      totalProjects,
      weeklyWorkLogs: workLogsData.length,
      totalTasks,
      pendingTasks,
      inProgressTasks,
      completedTasks
    }

    // TODO: 获取待办事项
    todos.value = []
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home-container {
  padding: 12px;
  min-height: 100vh;
  overflow: visible;
}

/* 核心功能区样式 */
.core-section {
  margin-bottom: 20px;
}

.task-management-card {
  min-height: 200px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border: 2px solid #e9ecef;
}

.task-management-card .card-header {
  border-bottom: 1px solid #ebeef5;
  padding: 16px 20px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.task-stats {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-stat {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  border-radius: 12px;
  color: white;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-text {
  font-size: 16px;
  opacity: 0.9;
}

.task-breakdown {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.breakdown-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
}

.breakdown-item.pending {
  border-left: 4px solid #fa8c16;
}

.breakdown-item.in-progress {
  border-left: 4px solid #409eff;
}

.breakdown-item.completed {
  border-left: 4px solid #67c23a;
}

.breakdown-item .count {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.breakdown-item .label {
  font-size: 12px;
  color: #606266;
}

/* 次要功能区样式 */
.secondary-section {
  margin-bottom: 20px;
}

.stat-cards {
  margin-bottom: 16px;
}

.stat-card {
  min-height: 120px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 8px 0;
}

.stat-label {
  color: #909399;
  font-size: 13px;
}

.sub-stats {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
}

.sub-stats span {
  padding: 2px 6px;
  border-radius: 3px;
}

.sub-stats .active {
  background-color: #e6f7ff;
  color: #1890ff;
}

.sub-stats .completed {
  background-color: #f6ffed;
  color: #52c41a;
}

.sub-stats .pending {
  background-color: #fff7e6;
  color: #fa8c16;
}

.sub-stats .in-progress {
  background-color: #e6f7ff;
  color: #1890ff;
}

/* 快速操作区样式 */
.quick-actions-section {
  margin-bottom: 20px;
}

.quick-action-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

.quick-action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.action-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.action-icon {
  font-size: 24px;
  color: #409eff;
  background: rgba(64, 158, 255, 0.1);
  padding: 12px;
  border-radius: 8px;
}

.action-text {
  flex: 1;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 13px;
  color: #606266;
}

/* 移除旧的紧凑布局样式 */

.content-section {
  margin-top: 20px;
}

.quick-stats {
  height: 100%;
}

.quick-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  border-radius: 8px;
  color: white;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-content .stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.stat-content .stat-label {
  font-size: 12px;
  color: #606266;
  margin: 0;
}

.team-list,
.project-list {
  height: 100%;
}

.team-item,
.project-item {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.team-item:last-child,
.project-item:last-child {
  border-bottom: none;
}

.team-info,
.project-info {
  flex: 1;
}

.team-info h3,
.project-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.team-info p,
.project-info p {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
}

.team-meta,
.project-meta {
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.team-actions,
.project-actions {
  margin-left: 16px;
}

/* 自定义滚动条样式 */
:deep(.el-scrollbar__bar.is-vertical) {
  width: 8px;
}

:deep(.el-scrollbar__thumb) {
  background-color: #c0c4cc;
  border-radius: 4px;
}

:deep(.el-scrollbar__thumb:hover) {
  background-color: #909399;
}

@media (max-width: 768px) {
  .home-container {
    padding: 10px;
  }
  
  .stat-cards {
    margin-bottom: 10px;
  }
  
  .content-section {
    margin-top: 10px;
    height: calc(100% - 160px);
  }
  
  .team-item,
  .project-item {
    padding: 12px;
  }
}
</style> 
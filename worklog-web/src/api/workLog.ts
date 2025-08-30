
import requestApi from '@/utils/request'

export interface WorkLog {
  id: number
  title?: string
  work_type: string
  content: string
  start_time: string
  end_time: string
  team_id: number
  team_name: string
  project_id?: number
  project_name?: string
  task_id?: number  // 关联的任务ID
  task_title?: string  // 关联的任务标题
  created_at: string
  updated_at: string
  status: 'pending' | 'approved' | 'rejected'
  progress_percentage?: number  // 任务完成度
  issues_encountered?: string  // 遇到的问题
  solutions_applied?: string   // 解决方案
  blockers?: string           // 阻碍因素
  comments?: WorkLogComment[]
  user_id?: number
  user_name?: string
  duration?: number
  hours_spent?: number
  work_status?: string
  description?: string
  details?: string
  date?: string
}

export interface WorkLogComment {
  id: number
  content: string
  user_id: number
  user_name: string
  created_at: string
}

export interface WorkLogCreate {
  title: string
  work_type: string
  content: string
  start_time: string
  end_time?: string
  team_id?: number
  project_id?: number
  task_id?: number
}

export interface WorkLogUpdate extends WorkLogCreate {}

export interface WorkLogListResponse {
  items: WorkLog[]
  total: number
  page: number
  size: number
  pages: number
}

export interface TaskWorkSummary {
  task_id: number
  task_title: string
  total_hours: number
  work_log_count: number
  estimated_hours: number
  actual_hours: number
  work_type_stats: Array<{
    work_type: string
    count: number
    hours: number
  }>
  user_stats: Array<{
    user_id: number
    count: number
    hours: number
  }>
}

export const workLogApi = {
  // 获取工作日志列表
  getWorkLogs(params: {
    page: number
    page_size: number
    start_date?: string
    end_date?: string
    work_type?: string
    tags?: string
    task_id?: number  // 按任务ID筛选
    project_id?: number  // 按项目ID筛选
    team_id?: number  // 按团队ID筛选
  }) {
    return requestApi<WorkLogListResponse>({
      url: '/work-logs',
      method: 'get',
      params
    })
  },

  // 获取团队工作日志列表
  getTeamWorkLogs(params: {
    team_id: number
    page: number
    page_size: number
    member_id?: number
    project_id?: number
    start_date?: string
    end_date?: string
  }) {
    return requestApi<WorkLogListResponse>({
      url: '/work-logs/team',
      method: 'get',
      params
    })
  },

  // 获取单个工作日志
  getWorkLog(id: number) {
    return requestApi<WorkLog>({
      url: `/work-logs/${id}`,
      method: 'get'
    })
  },

  // 创建工作日志
  createWorkLog(data: {
    project_id?: number
    task_id?: number  // 关联的任务ID
    team_id?: number
    work_type: string
    content: string
    start_time: string
    end_time?: string
    progress_percentage?: number
    issues_encountered?: string
    solutions_applied?: string
    blockers?: string
    remark?: string
    tags?: string
  }) {
    return requestApi<WorkLog>({
      url: '/work-logs',
      method: 'post',
      data
    })
  },

  // 更新工作日志
  updateWorkLog(id: number, data: Partial<WorkLog>) {
    return requestApi<WorkLog>({
      url: `/work-logs/${id}`,
      method: 'put',
      data
    })
  },

  // 删除工作日志
  deleteWorkLog(id: number) {
    return requestApi({
      url: `/work-logs/${id}`,
      method: 'delete'
    })
  },

  // 获取任务相关的工作日志
  getTaskWorkLogs(taskId: number, params?: {
    page?: number
    page_size?: number
  }) {
    return requestApi<WorkLog[]>({
      url: `/work-logs/task/${taskId}`,
      method: 'get',
      params
    })
  },

  // 获取任务工作汇总
  getTaskWorkSummary(taskId: number) {
    return requestApi<TaskWorkSummary>({
      url: `/work-logs/task/${taskId}/summary`,
      method: 'get'
    })
  },

  // 更新任务的最新工作日志
  updateLatestTaskWorkLog(taskId: number, data: Partial<WorkLog>) {
    return requestApi<WorkLog>({
      url: `/work-logs/task/${taskId}/update-latest`,
      method: 'put',
      data
    })
  },

  // 添加工作日志评论
  addWorkLogComment(workLogId: number, content: string) {
    return requestApi<WorkLogComment>({
      url: `/work-logs/${workLogId}/comments`,
      method: 'post',
      data: { content }
    })
  },

  // 审核工作日志
  approveWorkLog(workLogId: number) {
    return requestApi<WorkLog>({
      url: `/work-logs/${workLogId}/approve`,
      method: 'post'
    })
  },

  // 导出团队工作日志
  exportTeamWorkLogs(params: {
    team_id: number
    member_id?: number
    project_id?: number
    start_date?: string
    end_date?: string
  }) {
    return requestApi({
      url: '/work-logs/team/export',
      method: 'get',
      params,
      responseType: 'blob'
    })
  }
} 
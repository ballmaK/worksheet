import requestApi from '@/utils/request'

export interface Task {
  id: number
  title: string
  description?: string
  team_id: number
  project_id?: number
  task_level: 'project' | 'subtask'  // 任务层级
  parent_task_id?: number  // 父任务ID
  assignee_id?: number
  creator_id: number
  
  // 工作流相关字段
  claimed_by?: number      // 认领人ID
  claimed_at?: string      // 认领时间
  started_at?: string      // 开始工作时间
  completed_at?: string    // 完成时间
  
  status: 'pending' | 'assigned' | 'in_progress' | 'review' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  due_date?: string
  estimated_hours?: number
  actual_hours: number
  task_type: 'feature' | 'bug' | 'improvement' | 'documentation' | 'other'
  tags?: string
  created_at: string
  updated_at: string
  is_deleted: boolean
  
  // 关联信息
  creator?: UserInfo
  assignee?: UserInfo
  project?: ProjectInfo  // 项目信息
  claimed_user?: UserInfo  // 认领人信息
  parent_task?: Task  // 父任务
  subtasks?: Task[]   // 子任务
  comments?: TaskComment[]
  
  // 统计信息
  subtask_count?: number
  completed_subtask_count?: number
  comment_count?: number
}

export interface TaskComment {
  id: number
  task_id: number
  user_id: number
  content: string
  created_at: string
  updated_at: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  username: string
  email: string
}

export interface TaskListResponse {
  items: Task[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TaskStatistics {
  total: number
  pending: number
  in_progress: number
  completed: number
  review: number
  cancelled: number
  overdue: number
  total_estimated_hours: number
  completed_hours: number
  completion_rate: number
}

export interface CreateTaskData {
  title: string
  description?: string
  team_id: number
  project_id?: number
  task_level?: 'project' | 'subtask'  // 任务层级
  parent_task_id?: number  // 父任务ID
  assignee_id?: number
  status?: 'pending' | 'in_progress' | 'review' | 'completed' | 'cancelled'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  due_date?: string
  estimated_hours?: number
  task_type?: 'feature' | 'bug' | 'improvement' | 'documentation' | 'other'
  tags?: string
}

export interface UpdateTaskData {
  title?: string
  description?: string
  assignee_id?: number
  status?: 'pending' | 'in_progress' | 'review' | 'completed' | 'cancelled'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  due_date?: string
  estimated_hours?: number
  actual_hours?: number
  task_type?: 'feature' | 'bug' | 'improvement' | 'documentation' | 'other'
  tags?: string
}

export interface CreateCommentData {
  content: string
}

export interface TaskLog {
  id: number
  task_id: number
  user_id: number
  user_name?: string
  action_type: string
  description?: string
  old_value?: any
  new_value?: any
  extra_data?: any
  created_at: string
}

export interface TaskStatusChange {
  id: number
  task_id: number
  user_id: number
  user_name?: string
  old_status: string
  new_status: string
  reason?: string
  comment?: string
  created_at: string
}

export interface TaskActivityLog extends TaskLog {
  log_type: 'operation' | 'status_change'
}

export interface ProjectInfo {
  id: number
  name: string
  description?: string
}

export const taskApi = {
  // 获取任务列表
  getTasks(params: {
    team_id?: number
    project_id?: number
    status?: string
    priority?: string
    assignee_id?: number | string
    search?: string
    page?: number
    page_size?: number
  }) {
    return requestApi<TaskListResponse>({
      url: '/tasks',
      method: 'get',
      params
    })
  },

  // 获取任务详情
  getTask(id: number) {
    return requestApi<Task>({
      url: `/tasks/${id}`,
      method: 'get'
    })
  },

  // 创建任务
  createTask(data: CreateTaskData) {
    return requestApi<Task>({
      url: '/tasks',
      method: 'post',
      data
    })
  },

  // 更新任务
  updateTask(id: number, data: UpdateTaskData) {
    return requestApi<Task>({
      url: `/tasks/${id}`,
      method: 'put',
      data
    })
  },

  // 删除任务
  deleteTask(id: number) {
    return requestApi({
      url: `/tasks/${id}`,
      method: 'delete'
    })
  },

  // 获取子任务列表
  getSubTasks(taskId: number) {
    return requestApi<Task[]>({
      url: `/tasks/${taskId}/subtasks`,
      method: 'get'
    })
  },

  // 创建子任务
  createSubTask(taskId: number, data: CreateTaskData) {
    return requestApi<Task>({
      url: `/tasks/${taskId}/subtasks`,
      method: 'post',
      data
    })
  },

  // 获取任务评论
  getTaskComments(taskId: number) {
    return requestApi<TaskComment[]>({
      url: `/tasks/${taskId}/comments`,
      method: 'get'
    })
  },

  // 创建任务评论
  createTaskComment(taskId: number, data: CreateCommentData) {
    return requestApi<TaskComment>({
      url: `/tasks/${taskId}/comments`,
      method: 'post',
      data
    })
  },

  // 获取通用任务统计
  getTaskStatistics(params?: {
    team_id?: number
    project_id?: number
    assignee_id?: number
  }) {
    return requestApi<TaskStatistics>({
      url: '/tasks/statistics',
      method: 'get',
      params
    })
  },

  // 获取团队任务统计
  getTeamTaskStatistics(teamId: number) {
    return requestApi<TaskStatistics>({
      url: `/tasks/statistics/team/${teamId}`,
      method: 'get'
    })
  },

  // 获取项目任务统计
  getProjectTaskStatistics(projectId: number) {
    return requestApi<TaskStatistics>({
      url: `/tasks/statistics/project/${projectId}`,
      method: 'get'
    })
  },

  // 获取任务日志
  getTaskLogs(taskId: number, params?: { limit?: number; offset?: number }) {
    return requestApi<TaskLog[]>({
      url: `/tasks/${taskId}/logs`,
      method: 'get',
      params
    })
  },

  // 获取任务状态变化记录
  getTaskStatusChanges(taskId: number, params?: { limit?: number; offset?: number }) {
    return requestApi<TaskStatusChange[]>({
      url: `/tasks/${taskId}/status-changes`,
      method: 'get',
      params
    })
  },

  // 获取任务活动日志
  getTaskActivityLogs(taskId: number, params?: { limit?: number; offset?: number }) {
    return requestApi<TaskActivityLog[]>({
      url: `/tasks/${taskId}/activity`,
      method: 'get',
      params
    })
  },

  // 认领任务
  claimTask(taskId: number) {
    return requestApi({
      url: `/tasks/${taskId}/claim`,
      method: 'post'
    })
  },

  // 开始工作
  startTaskWork(taskId: number) {
    return requestApi({
      url: `/tasks/${taskId}/start`,
      method: 'post'
    })
  },

  // 完成任务
  completeTask(taskId: number) {
    return requestApi({
      url: `/tasks/${taskId}/complete`,
      method: 'post'
    })
  },

  // 提交审核
  submitTaskForReview(taskId: number) {
    return requestApi({
      url: `/tasks/${taskId}/submit-review`,
      method: 'post'
    })
  },

  // 审核通过
  approveTask(taskId: number) {
    return requestApi({
      url: `/tasks/${taskId}/approve`,
      method: 'post'
    })
  },

  // 审核拒绝
  rejectTask(taskId: number, reason: string) {
    return requestApi({
      url: `/tasks/${taskId}/reject`,
      method: 'post',
      data: { reason }
    })
  },

  // 快速创建任务
  createTaskQuick(data: { title: string; team_id?: number }) {
    return requestApi<Task>({
      url: '/tasks/quick',
      method: 'post',
      data
    })
  },

  // 分配任务
  assignTask(taskId: number, assigneeId: number) {
    return requestApi<Task>({
      url: `/tasks/${taskId}/assign`,
      method: 'post',
      data: { assignee_id: assigneeId }
    })
  }
} 
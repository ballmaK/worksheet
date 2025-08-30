import requestApi from '@/utils/request'

export interface ProjectOverview {
  project: {
    id: number
    name: string
    description: string
    status: string
    progress: number
    start_date: string
    end_date: string
    created_at: string
  }
  statistics: {
    total_tasks: number
    completed_tasks: number
    in_progress_tasks: number
    pending_tasks: number
    completion_rate: number
    total_estimated_hours: number
    total_actual_hours: number
  }
  recent_activities: Array<{
    id: number
    type: string
    title: string
    content: string
    created_at: string
    user: {
      id: number
      username: string
    }
  }>
  team_members: Array<{
    id: number
    username: string
    role: string
    joined_at: string
  }>
}

export interface ProjectTask {
  id: number
  title: string
  description: string
  status: string
  priority: string
  task_type: string
  assignee_id: number
  assignee: {
    id: number
    username: string
  }
  due_date: string
  estimated_hours: number
  actual_hours: number
  created_at: string
  updated_at: string
}

export interface ProjectActivity {
  id: string
  type: string
  title: string
  content: string
  created_at: string
  user: {
    id: number
    username: string
  }
  metadata: any
}

export interface TaskCreateData {
  title: string
  description?: string
  task_type: string
  priority: string
  assignee_id?: number
  due_date?: string
  estimated_hours?: number
}

export interface TaskFilters {
  status?: string
  priority?: string
  keyword?: string
  skip?: number
  limit?: number
}

// 获取项目概览
export function getProjectOverview(projectId: number) {
  return requestApi<ProjectOverview>({
    url: `/project-management/${projectId}/overview`,
    method: 'GET'
  })
}

// 获取项目任务列表
export function getProjectTasks(projectId: number, params?: TaskFilters) {
  return requestApi<ProjectTask[]>({
    url: `/project-management/${projectId}/tasks`,
    method: 'GET',
    params
  })
}

// 创建项目任务
export function createProjectTask(projectId: number, data: TaskCreateData) {
  return requestApi<ProjectTask>({
    url: `/project-management/${projectId}/tasks`,
    method: 'POST',
    data
  })
}

// 获取项目活动流
export function getProjectActivities(projectId: number, params?: { skip?: number; limit?: number }) {
  return requestApi<{
    activities: ProjectActivity[]
    total: number
    page: number
    page_size: number
  }>({
    url: `/project-management/${projectId}/activities`,
    method: 'GET',
    params
  })
}

export const projectManagementApi = {
  getProjectOverview,
  getProjectTasks,
  createProjectTask,
  getProjectActivities
}

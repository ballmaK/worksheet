import request from '@/utils/request'

export interface Project {
  id: number
  name: string
  description: string
  team_id: number
  team_name?: string
  creator_id: number
  creator_name?: string
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold' | 'cancelled'
  start_date?: string
  end_date?: string
  progress: number
  task_count?: number
  member_count?: number
  worklog_count?: number
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  name: string
  description?: string
  team_id: number
  status?: 'not_started' | 'in_progress' | 'completed' | 'on_hold' | 'cancelled'
  start_date?: string
  end_date?: string
  progress?: number
}

export interface ProjectUpdate {
  name?: string
  description?: string
  team_id?: number
  status?: 'not_started' | 'in_progress' | 'completed' | 'on_hold' | 'cancelled'
  start_date?: string
  end_date?: string
  progress?: number
}

export const projectApi = {
  // 获取项目列表
  getProjects: (teamId?: number, memberId?: number) => {
    return request.get<Project[]>('/projects', {
      params: { 
        team_id: teamId,
        member_id: memberId
      }
    })
  },

  // 获取项目详情
  getProject: (id: number) => {
    return request.get<Project>(`/projects/${id}`)
  },

  // 创建项目
  createProject: (data: ProjectCreate) => {
    return request.post<Project>('/projects', data)
  },

  // 更新项目
  updateProject: (id: number, data: ProjectUpdate) => {
    return request.put<Project>(`/projects/${id}`, data)
  },

  // 删除项目
  deleteProject: (id: number) => {
    return request.delete(`/projects/${id}`)
  }
} 
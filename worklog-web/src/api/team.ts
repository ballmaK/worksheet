import requestApi from '@/utils/request'

export interface TeamMember {
  id: number
  team_id: number
  user_id: number
  role: string
  username: string
  email: string
  joined_at: string
}

export interface Team {
  id: number
  name: string
  description: string
  created_at: string
  updated_at: string
  members?: TeamMember[]
  projects?: any[]
}

export interface CreateTeamData {
  name: string
  description: string
}

export interface UpdateTeamData extends CreateTeamData {
  id: number
}

export interface TeamActivity {
  id: number
  team_id: number
  user_id: number
  activity_type: string
  title: string
  content?: string
  metadata?: any
  created_at: string
}

export interface TeamProject {
  id: number
  name: string
  description: string
  status: string
  progress: number
  creator_name: string
  start_date?: string
  end_date?: string
  created_at: string
}

export interface TeamStatistics {
  member_count: number
  project_count: number
  worklog_count: number
  task_count: number
}

export const teamApi = {
  // 获取团队列表
  getTeams() {
    return requestApi<Team[]>({
      url: '/teams',
      method: 'get'
    })
  },

  // 获取团队详情
  getTeam(id: number) {
    return requestApi<Team>({
      url: `/teams/${id}`,
      method: 'get'
    })
  },

  // 获取团队成员
  getTeamMembers(teamId: number) {
    return requestApi<TeamMember[]>({
      url: `/teams/${teamId}/members`,
      method: 'get'
    })
  },

  // 移除团队成员
  removeTeamMember(teamId: number, userId: number) {
    return requestApi({
      url: `/teams/${teamId}/members/${userId}`,
      method: 'delete'
    })
  },

  // 创建团队
  createTeam(data: { name: string; description: string }) {
    return requestApi<Team>({
      url: '/teams',
      method: 'post',
      data
    })
  },

  // 更新团队
  updateTeam(id: number, data: { name: string; description: string }) {
    return requestApi<Team>({
      url: `/teams/${id}`,
      method: 'put',
      data
    })
  },

  // 删除团队
  deleteTeam(id: number) {
    return requestApi({
      url: `/teams/${id}`,
      method: 'delete'
    })
  },

  // 获取团队动态
  getTeamActivities(
    teamId: number,
    params?: {
      skip?: number
      limit?: number
      activity_type?: string
      start_date?: string
      end_date?: string
    }
  ) {
    return requestApi<TeamActivity[]>({
      url: `/teams/${teamId}/activities`,
      method: 'get',
      params
    })
  },

  // 获取团队项目列表
  getTeamProjects(
    teamId: number,
    params?: {
      skip?: number
      limit?: number
      status?: string
      keyword?: string
    }
  ) {
    return requestApi<TeamProject[]>({
      url: `/teams/${teamId}/projects`,
      method: 'get',
      params
    })
  },

  // 关联项目到团队
  associateProject(teamId: number, projectId: number) {
    return requestApi({
      url: `/teams/${teamId}/projects/${projectId}/associate`,
      method: 'post'
    })
  },

  // 解除项目与团队的关联
  disassociateProject(teamId: number, projectId: number) {
    return requestApi({
      url: `/teams/${teamId}/projects/${projectId}/disassociate`,
      method: 'delete'
    })
  },

  // 获取团队统计信息
  getTeamStatistics(teamId: number) {
    return requestApi<TeamStatistics>({
      url: `/teams/${teamId}/statistics`,
      method: 'get'
    })
  }
} 
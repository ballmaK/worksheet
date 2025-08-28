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
  }
} 
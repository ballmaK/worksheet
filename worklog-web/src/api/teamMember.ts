import { api } from '@/api'

export interface TeamMember {
  id: number
  team_id: number
  user_id: number
  role: string
  created_at: string
  updated_at: string
  user: {
    id: number
    username: string
    email: string
    role: string
  }
}

export const teamMemberApi = {
  // 获取团队成员列表
  getTeamMembers(teamId: number) {
    return api.get<TeamMember[]>(`/teams/${teamId}/members`)
  },

  // 添加团队成员
  addTeamMember(teamId: number, data: { user_id: number; role: string }) {
    return api.post<TeamMember>(`/teams/${teamId}/members`, data)
  },

  // 更新团队成员角色
  updateTeamMember(teamId: number, memberId: number, data: { role: string }) {
    return api.put<TeamMember>(`/teams/${teamId}/members/${memberId}`, data)
  },

  // 删除团队成员
  deleteTeamMember(teamId: number, memberId: number) {
    return api.delete(`/teams/${teamId}/members/${memberId}`)
  }
} 
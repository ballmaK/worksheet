import requestApi from '@/utils/request'

export interface TeamMember {
  id: number
  team_id: number
  user_id: number
  username: string
  email: string
  role: 'team_member' | 'team_admin'
  joined_at: string
}

export interface InviteMemberData {
  email: string
  role: 'team_member' | 'team_admin'
}

export const teamMemberApi = {
  // 获取团队成员列表
  getTeamMembers: (teamId: number) => {
    return requestApi<TeamMember[]>({
      url: `/teams/${teamId}/members`,
      method: 'get'
    })
  },

  // 邀请新成员
  inviteMember: (teamId: number, data: InviteMemberData) => {
    return requestApi({
      url: `/teams/${teamId}/invite`,
      method: 'post',
      data
    })
  },

  // 更新成员角色
  updateMemberRole: (teamId: number, memberId: number, data: { role: 'team_member' | 'team_admin' }) => {
    return requestApi<TeamMember>({
      url: `/teams/${teamId}/members/${memberId}`,
      method: 'put',
      data
    })
  },

  // 移除成员
  removeMember: (teamId: number, memberId: number) => {
    return requestApi({
      url: `/teams/${teamId}/members/${memberId}`,
      method: 'delete'
    })
  }
} 
import requestApi from '@/utils/request'

export interface TeamInvite {
  id: number
  team_id: number
  inviter_id: number
  email: string
  role: string
  status: string
  created_at: string
  updated_at: string
  inviter_name: string
  team_name: string
}

export interface VerifyInvitationData {
  email: string
  verification_code: string
  username?: string
  password?: string
}

export interface VerifyInvitationResponse {
  message: string
  user_created: boolean
  team_member_id?: number
}

export const teamInviteApi = {
  // 获取团队邀请列表
  getInvites: (teamId: number) => 
    requestApi<TeamInvite[]>({
      url: `/teams/${teamId}/invites`,
      method: 'get'
    }),
  
  // 创建邀请
  createInvite: (teamId: number, data: { email: string; role: string }) => 
    requestApi<TeamInvite>({
      url: `/teams/${teamId}/invite`,
      method: 'post',
      data
    }),
  
  // 验证邀请码
  verifyInvitation: (data: VerifyInvitationData) => 
    requestApi<VerifyInvitationResponse>({
      url: '/teams/invite/verify',
      method: 'post',
      data
    }),
  
  // 重新发送邀请
  resendInvite: (inviteId: number) => 
    requestApi({
      url: `/teams/invite/${inviteId}/resend`,
      method: 'post'
    }),
  
  // 删除邀请
  deleteInvite: (inviteId: number) => 
    requestApi({
      url: `/teams/invite/${inviteId}`,
      method: 'delete'
    })
} 
export interface TeamMember {
  id: number
  team_id: number
  user_id: number
  username: string
  email: string
  role: 'team_admin' | 'team_member'
  joined_at: string
}

export interface Team {
  id: number
  name: string
  description: string
  created_at: string
  members: TeamMember[]
} 
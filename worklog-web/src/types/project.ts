export interface Project {
  id: number
  name: string
  description: string
  team_id: number
  team_name: string
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold'
  start_date: string
  end_date: string
  progress: number
  creator_id: number
  creator_name: string
  created_at: string
  updated_at: string
  is_my_project?: boolean
  task_count?: number
  member_count?: number
  worklog_count?: number
}

export interface ProjectCreate {
  name: string
  description: string
  team_id: number
  status: string
  start_date: string
  end_date: string
  progress: number
}

export interface ProjectUpdate extends Partial<ProjectCreate> {}

export interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  size: number
  pages: number
}

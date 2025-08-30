export interface WorkLog {
  id: number
  title?: string
  work_type: string
  content: string
  start_time: string
  end_time: string
  team_id: number
  team_name: string
  project_id?: number
  project_name?: string
  task_id?: number
  task_title?: string
  created_at: string
  updated_at: string
  status: 'pending' | 'approved' | 'rejected'
  progress_percentage?: number
  issues_encountered?: string
  solutions_applied?: string
  blockers?: string
  comments?: WorkLogComment[]
  user_id?: number
  user_name?: string
  duration?: number
  hours_spent?: number
  work_status?: string
  description?: string
  details?: string
  date?: string
}

export interface WorkLogComment {
  id: number
  content: string
  user_id: number
  user_name: string
  created_at: string
}

export interface WorkLogCreate {
  title: string
  work_type: string
  content: string
  start_time: string
  end_time?: string
  team_id?: number
  project_id?: number
  task_id?: number
}

export interface WorkLogUpdate extends WorkLogCreate {}

export interface WorkLogListResponse {
  items: WorkLog[]
  total: number
  page: number
  size: number
  pages: number
}

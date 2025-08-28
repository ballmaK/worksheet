export interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
  reminder_interval: number
  work_hours_start: string
  work_hours_end: string
  reminder_enabled: boolean
  notification_method: string
  last_reminder_at?: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface UserUpdate {
  username?: string
  email?: string
  password?: string
  role?: string
  is_active?: boolean
  reminder_interval?: number
  work_hours_start?: string
  work_hours_end?: string
  reminder_enabled?: boolean
  notification_method?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
} 
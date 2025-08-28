import api from './request'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData extends LoginData {
  email: string
  invite_token?: string
}

export const authApi = {
  login: (data: LoginData | FormData) => {
    return api.post('/users/token', data)
  },
  
  register: (data: RegisterData) => {
    return api.post('/users/register', data)
  },
  
  logout: () => {
    return api.post('/users/logout')
  }
} 
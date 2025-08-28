import requestApi from '@/utils/request'

export interface User {
  id: number
  username: string
  email: string
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  invite_token?: string
}

export const userApi = {
  // 用户注册
  register(data: RegisterRequest) {
    return requestApi<User>({
      url: '/users/register',
      method: 'post',
      data
    })
  },

  // 用户登录
  login(data: { username: string; password: string }) {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)
    
    return requestApi<LoginResponse>({
      url: '/users/token',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  // 获取当前用户信息
  getCurrentUser() {
    return requestApi<User>({
      url: '/users/me',
      method: 'get'
    })
  },

  // 获取用户列表
  getUsers() {
    return requestApi<User[]>({
      url: '/users',
      method: 'get'
    })
  },

  // 获取用户详情
  getUser(id: number) {
    return requestApi<User>({
      url: `/users/${id}`,
      method: 'get'
    })
  },

  // 创建用户
  createUser(data: { username: string; email: string; password: string }) {
    return requestApi<User>({
      url: '/users',
      method: 'post',
      data
    })
  },

  // 更新用户
  updateUser(id: number, data: Partial<User>) {
    return requestApi<User>({
      url: `/users/${id}`,
      method: 'put',
      data
    })
  },

  // 删除用户
  deleteUser(id: number) {
    return requestApi({
      url: `/users/${id}`,
      method: 'delete'
    })
  }
} 
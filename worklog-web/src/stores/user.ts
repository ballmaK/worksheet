import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'

// 检查是否在Electron环境中
const isElectron = () => {
  return typeof window !== 'undefined' && window.electronAPI
}

// 安全地调用Electron API
const callElectronAPI = (method: string, ...args: any[]) => {
  if (isElectron() && (window as any).electronAPI && (window as any).electronAPI[method]) {
    return (window as any).electronAPI[method](...args)
  }
}

export interface UserState {
  userId: number | null
  username: string | null
  email: string | null
  role: string | null
  token: string | null
}

export const useUserStore = defineStore('user', () => {
  const userId = ref<number | null>(null)
  const username = ref<string | null>(null)
  const email = ref<string | null>(null)
  const role = ref<string | null>(null)
  const token = ref<string | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    
    // 在Electron环境中，同步token到主进程
    callElectronAPI('updateToken', newToken)
  }

  const setUser = (user: Partial<UserState>) => {
    if (user.userId) {
      userId.value = user.userId
      localStorage.setItem('userId', user.userId.toString())
    }
    if (user.username) {
      username.value = user.username
      localStorage.setItem('username', user.username)
    }
    if (user.email) {
      email.value = user.email
      localStorage.setItem('email', user.email)
    }
    if (user.role) {
      role.value = user.role
      localStorage.setItem('role', user.role)
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const response = await api.post('/users/token', {
        username,
        password
      })
      const { access_token, user } = response.data
      setToken(access_token)
      setUser({
        userId: user.id,
        username: user.username,
        email: user.email,
        role: user.role
      })
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  const logout = () => {
    userId.value = null
    username.value = null
    email.value = null
    role.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    localStorage.removeItem('email')
    localStorage.removeItem('role')
    
    // 在Electron环境中，清除主进程token
    if (window.electronAPI && window.electronAPI.updateToken) {
      window.electronAPI.updateToken('')
    }
  }

  const initFromStorage = () => {
    const storedToken = localStorage.getItem('token')
    const storedUserId = localStorage.getItem('userId')
    const storedUsername = localStorage.getItem('username')
    const storedEmail = localStorage.getItem('email')
    const storedRole = localStorage.getItem('role')
    
    if (storedToken) {
      token.value = storedToken
      // 在Electron环境中，同步token到主进程
      if (window.electronAPI && window.electronAPI.updateToken) {
        window.electronAPI.updateToken(storedToken)
      }
    }
    if (storedUserId) {
      userId.value = parseInt(storedUserId)
    }
    if (storedUsername) {
      username.value = storedUsername
    }
    if (storedEmail) {
      email.value = storedEmail
    }
    if (storedRole) {
      role.value = storedRole
    }
  }

  return {
    userId,
    username,
    email,
    role,
    token,
    isLoggedIn,
    setToken,
    setUser,
    login,
    logout,
    initFromStorage
  }
}) 
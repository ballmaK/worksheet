import { userApi } from '@/api/user'
import { User } from '@/types/user'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'current_user'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function getCurrentUser(): User | null {
  const userStr = localStorage.getItem(USER_KEY)
  return userStr ? JSON.parse(userStr) : null
}

export function setCurrentUser(user: User): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeCurrentUser(): void {
  localStorage.removeItem(USER_KEY)
}

export async function refreshUserInfo(): Promise<User | null> {
  try {
    const response = await userApi.getCurrentUser()
    const user = response.data
    setCurrentUser(user)
    return user
  } catch (error) {
    console.error('Failed to refresh user info:', error)
    return null
  }
}

export function clearAuth(): void {
  removeToken()
  removeCurrentUser()
} 
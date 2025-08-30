import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 根据环境设置API基础URL
const getBaseURL = () => {
  // 生产环境使用相对路径，由Nginx代理
  if (import.meta.env.PROD) {
    return '/api/v1'
  }
  // 开发环境使用本地地址
  return 'http://localhost:8000/api/v1'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 如果响应数据中包含 data 字段，直接返回 data
    if (response.data && 'data' in response.data) {
      return response.data
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    }
    return Promise.reject(error)
  }
)

export default api 
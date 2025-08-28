import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export interface NotificationData {
  title: string
  content: string
  type: 'task' | 'team' | 'system' | 'worklog' | 'project' | 'general'
  data?: any
  priority?: 'urgent' | 'important' | 'normal' | 'low'
}

class NotificationManager {
  private toastRef: any = null
  private isElectron = typeof window !== 'undefined' && (window.electron !== undefined || window.electronAPI !== undefined)

  // 设置Toast组件引用
  setToastRef(ref: any) {
    this.toastRef = ref
  }

  // 显示通知
  show(notification: NotificationData) {
    // 1. 显示Toast通知
    this.showToast(notification)
    
    // 2. 显示系统通知（Electron环境）
    if (this.isElectron) {
      this.showSystemNotification(notification)
    }
    
    // 3. 显示Element Plus消息（作为备用）
    this.showElementMessage(notification)
  }

  // 显示Toast通知
  private showToast(notification: NotificationData) {
    if (this.toastRef) {
      this.toastRef.addNotification({
        ...notification,
        timestamp: Date.now()
      })
    }
  }

  // 显示系统通知
  private showSystemNotification(notification: NotificationData) {
    // 优先使用electronAPI，兼容electron
    const electronAPI = window.electronAPI || window.electron
    if (this.isElectron && electronAPI?.showNotification) {
      try {
        electronAPI.showNotification({
          title: notification.title,
          body: notification.content,
          icon: this.getNotificationIcon(notification.type),
          silent: false
        })
      } catch (error) {
        console.error('Electron通知发送失败:', error)
      }
    }
  }

  // 显示Element Plus消息
  private showElementMessage(notification: NotificationData) {
    const type = this.getElMessageType(notification.type)
    ElMessage({
      message: `${notification.title}: ${notification.content}`,
      type,
      duration: 3000,
      showClose: true
    })
  }

  // 获取通知图标
  private getNotificationIcon(type: string): string {
    const icons = {
      task: '🎯',
      team: '👥',
      system: '⚙️',
      worklog: '📝',
      project: '📁',
      general: '🔔'
    }
    return icons[type as keyof typeof icons] || icons.general
  }

  // 获取Element Plus消息类型
  private getElMessageType(type: string): 'success' | 'warning' | 'info' | 'error' {
    const types = {
      task: 'success',
      team: 'info',
      system: 'warning',
      worklog: 'info',
      project: 'info',
      general: 'info'
    }
    return (types[type as keyof typeof types] || 'info') as any
  }

  // 请求通知权限
  async requestPermission(): Promise<boolean> {
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        return true
      } else if (Notification.permission === 'default') {
        const permission = await Notification.requestPermission()
        return permission === 'granted'
      }
    }
    return false
  }

  // 检查通知权限
  hasPermission(): boolean {
    return 'Notification' in window && Notification.permission === 'granted'
  }
}

// 创建全局通知管理器实例
export const notificationManager = new NotificationManager()

// Vue Composable
export function useNotification() {
  const toastRef = ref<any>(null)

  // 设置Toast引用
  const setToastRef = (ref: any) => {
    toastRef.value = ref
    notificationManager.setToastRef(ref)
  }

  // 显示通知
  const showNotification = (notification: NotificationData) => {
    notificationManager.show(notification)
  }

  // 显示任务通知
  const showTaskNotification = (title: string, content: string, data?: any) => {
    showNotification({
      title,
      content,
      type: 'task',
      data
    })
  }

  // 显示团队通知
  const showTeamNotification = (title: string, content: string, data?: any) => {
    showNotification({
      title,
      content,
      type: 'team',
      data
    })
  }

  // 显示系统通知
  const showSystemNotification = (title: string, content: string, data?: any) => {
    showNotification({
      title,
      content,
      type: 'system',
      data
    })
  }

  // 显示工作日志通知
  const showWorklogNotification = (title: string, content: string, data?: any) => {
    showNotification({
      title,
      content,
      type: 'worklog',
      data
    })
  }

  // 显示项目通知
  const showProjectNotification = (title: string, content: string, data?: any) => {
    showNotification({
      title,
      content,
      type: 'project',
      data
    })
  }

  // 请求通知权限
  const requestPermission = () => {
    return notificationManager.requestPermission()
  }

  // 检查通知权限
  const hasPermission = () => {
    return notificationManager.hasPermission()
  }

  return {
    toastRef,
    setToastRef,
    showNotification,
    showTaskNotification,
    showTeamNotification,
    showSystemNotification,
    showWorklogNotification,
    showProjectNotification,
    requestPermission,
    hasPermission
  }
} 
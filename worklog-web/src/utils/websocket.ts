import { useUserStore } from '@/stores/user'

export interface WebSocketMessage {
  type: string
  data?: any
  timestamp?: number
  message?: string
  status?: string
}

export interface MessageNotification {
  id: number
  title: string
  content: string
  message_type: string
  priority: string
  created_at: string
  sender?: {
    id: number
    username: string
  }
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000 // 3秒
  private heartbeatInterval: number | null = null
  private isConnecting = false
  private messageHandlers: Map<string, (data: any) => void> = new Map()

  // 事件回调
  private onConnectCallback: (() => void) | null = null
  private onDisconnectCallback: (() => void) | null = null
  private onErrorCallback: ((error: Event) => void) | null = null

  constructor() {
    // 页面卸载时清理连接
    window.addEventListener('beforeunload', () => {
      this.disconnect()
    })
  }

  /**
   * 连接到WebSocket服务器
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return
    }

    this.isConnecting = true
    const userStore = useUserStore()
    const token = userStore.token

    if (!token) {
      console.error('WebSocket连接失败: 未找到用户token')
      this.isConnecting = false
      return
    }

    try {
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/api/v1/ws/messages/?token=${token}`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket连接已建立')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.startHeartbeat()
        this.onConnectCallback?.()
      }

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data)
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket连接已关闭:', event.code, event.reason)
        this.isConnecting = false
        this.stopHeartbeat()
        this.onDisconnectCallback?.()
        
        // 如果不是主动断开，尝试重连
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket连接错误:', error)
        this.isConnecting = false
        this.onErrorCallback?.(error)
      }

    } catch (error) {
      console.error('WebSocket连接失败:', error)
      this.isConnecting = false
      this.scheduleReconnect()
    }
  }

  /**
   * 断开WebSocket连接
   */
  disconnect(): void {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close(1000, '主动断开连接')
      this.ws = null
    }
  }

  /**
   * 发送消息
   */
  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }

  /**
   * 发送心跳
   */
  private sendHeartbeat(): void {
    this.send({
      type: 'heartbeat',
      timestamp: Date.now()
    })
  }

  /**
   * 开始心跳
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.sendHeartbeat()
    }, 30000) // 30秒发送一次心跳
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data)
      console.log('收到WebSocket消息:', message)

      // 处理心跳响应
      if (message.type === 'heartbeat' || message.type === 'pong') {
        return
      }

      // 处理新消息通知
      if (message.type === 'new_message') {
        this.handleNewMessage(message.data)
        return
      }

      // 处理任务状态更新
      if (message.type === 'task_update') {
        this.handleTaskUpdate(message.data)
        return
      }

      // 处理团队通知
      if (message.type === 'team_notification') {
        this.handleTeamNotification(message.data)
        return
      }

      // 处理任务通知（后端发送的实际消息类型）
      if (message.type === 'task_notification') {
        this.handleTaskNotification(message)
        return
      }

      // 处理项目通知
      if (message.type === 'project_notification') {
        this.handleProjectNotification(message)
        return
      }

      // 处理系统通知
      if (message.type === 'system_notification') {
        this.handleSystemNotification(message)
        return
      }

      // 调用注册的消息处理器
      const handler = this.messageHandlers.get(message.type)
      if (handler) {
        handler(message.data)
      }

    } catch (error) {
      console.error('解析WebSocket消息失败:', error)
    }
  }

  /**
   * 处理新消息通知
   */
  private handleNewMessage(data: MessageNotification): void {
    // 显示浏览器通知
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(data.title, {
        body: data.content,
        icon: '/favicon.ico',
        tag: `message_${data.id}`
      })
    }

    // 触发消息更新事件
    window.dispatchEvent(new CustomEvent('new-message', { detail: data }))
  }

  /**
   * 处理任务状态更新
   */
  private handleTaskUpdate(data: any): void {
    window.dispatchEvent(new CustomEvent('task-update', { detail: data }))
  }

  /**
   * 处理团队通知
   */
  private handleTeamNotification(data: any): void {
    window.dispatchEvent(new CustomEvent('team-notification', { detail: data }))
  }

  /**
   * 处理任务通知
   */
  private handleTaskNotification(message: any): void {
    console.log('处理任务通知:', message)
    
    // 构建通知数据
    const notificationData = {
      title: `任务通知: ${message.task_title || '未知任务'}`,
      content: this.buildTaskNotificationContent(message),
      type: 'task' as const,
      data: message
    }

    // 触发任务通知事件
    window.dispatchEvent(new CustomEvent('task-notification', { detail: notificationData }))
    
    // 同时触发新消息事件，用于更新消息列表
    window.dispatchEvent(new CustomEvent('new-message', { detail: notificationData }))
  }

  /**
   * 处理项目通知
   */
  private handleProjectNotification(message: any): void {
    console.log('处理项目通知:', message)
    
    const notificationData = {
      title: `项目通知: ${message.project_name || '未知项目'}`,
      content: this.buildProjectNotificationContent(message),
      type: 'project' as const,
      data: message
    }

    window.dispatchEvent(new CustomEvent('project-notification', { detail: notificationData }))
    window.dispatchEvent(new CustomEvent('new-message', { detail: notificationData }))
  }

  /**
   * 处理系统通知
   */
  private handleSystemNotification(message: any): void {
    console.log('处理系统通知:', message)
    
    const notificationData = {
      title: message.title || '系统通知',
      content: message.content || '收到系统通知',
      type: 'system' as const,
      data: message
    }

    window.dispatchEvent(new CustomEvent('system-notification', { detail: notificationData }))
    window.dispatchEvent(new CustomEvent('new-message', { detail: notificationData }))
  }

  /**
   * 构建任务通知内容
   */
  private buildTaskNotificationContent(message: any): string {
    const { notification_type, task_title, task_status, creator_name, assignee_name, extra_data } = message
    
    switch (notification_type) {
      case 'task_assigned':
        return `任务"${task_title}"已分配给${assignee_name || '您'}`
      case 'task_status_changed':
        const oldStatus = extra_data?.old_status || '未知'
        const newStatus = extra_data?.new_status || task_status || '未知'
        return `任务"${task_title}"状态从${oldStatus}变更为${newStatus}`
      case 'task_created':
        return `新任务"${task_title}"已创建，创建者：${creator_name}`
      default:
        return `任务"${task_title}"有新的更新`
    }
  }

  /**
   * 构建项目通知内容
   */
  private buildProjectNotificationContent(message: any): string {
    const { notification_type, project_name, creator_name } = message
    
    switch (notification_type) {
      case 'project_created':
        return `新项目"${project_name}"已创建，创建者：${creator_name}`
      default:
        return `项目"${project_name}"有新的更新`
    }
  }

  /**
   * 安排重连
   */
  private scheduleReconnect(): void {
    this.reconnectAttempts++
    const delay = this.reconnectInterval * this.reconnectAttempts
    
    console.log(`${delay}ms后尝试重连WebSocket (第${this.reconnectAttempts}次)`)
    
    setTimeout(() => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.connect()
      } else {
        console.error('WebSocket重连失败，已达到最大重试次数')
      }
    }, delay)
  }

  /**
   * 注册消息处理器
   */
  on(type: string, handler: (data: any) => void): void {
    this.messageHandlers.set(type, handler)
  }

  /**
   * 移除消息处理器
   */
  off(type: string): void {
    this.messageHandlers.delete(type)
  }

  /**
   * 设置连接回调
   */
  onConnect(callback: () => void): void {
    this.onConnectCallback = callback
  }

  /**
   * 设置断开连接回调
   */
  onDisconnect(callback: () => void): void {
    this.onDisconnectCallback = callback
  }

  /**
   * 设置错误回调
   */
  onError(callback: (error: Event) => void): void {
    this.onErrorCallback = callback
  }

  /**
   * 检查连接状态
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  /**
   * 获取连接状态
   */
  getConnectionState(): number {
    return this.ws?.readyState || WebSocket.CLOSED
  }
}

// 创建单例实例
export const wsService = new WebSocketService()

// 导出连接状态常量
export const WS_STATE = {
  CONNECTING: WebSocket.CONNECTING,
  OPEN: WebSocket.OPEN,
  CLOSING: WebSocket.CLOSING,
  CLOSED: WebSocket.CLOSED
} 
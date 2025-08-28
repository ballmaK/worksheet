import { ref, onMounted, onUnmounted, watch } from 'vue'
import { wsService, WS_STATE, type WebSocketMessage, type MessageNotification } from '@/utils/websocket'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useNotification } from './useNotification'

export function useWebSocket() {
  const isConnected = ref(false)
  const connectionState = ref<number>(WS_STATE.CLOSED)
  const unreadCount = ref(0)
  const userStore = useUserStore()
  const { showTaskNotification, showTeamNotification, showSystemNotification, showWorklogNotification, showProjectNotification } = useNotification()

  // 连接状态更新
  const updateConnectionState = () => {
    isConnected.value = wsService.isConnected()
    connectionState.value = wsService.getConnectionState()
  }

  // 连接成功回调
  const handleConnect = () => {
    updateConnectionState()
    console.log('WebSocket连接成功')
  }

  // 断开连接回调
  const handleDisconnect = () => {
    updateConnectionState()
    console.log('WebSocket连接断开')
  }

  // 错误处理回调
  const handleError = (error: Event) => {
    updateConnectionState()
    console.error('WebSocket连接错误:', error)
    ElMessage.error('WebSocket连接错误，请检查网络连接')
  }

  // 处理新消息
  const handleNewMessage = (data: MessageNotification) => {
    unreadCount.value++
    
    // 根据消息类型显示不同的通知
    switch (data.message_type) {
      case 'task':
        showTaskNotification(data.title, data.content, data)
        break
      case 'team':
        showTeamNotification(data.title, data.content, data)
        break
      case 'system':
        showSystemNotification(data.title, data.content, data)
        break
      case 'worklog':
        showWorklogNotification(data.title, data.content, data)
        break
      case 'project':
        showProjectNotification(data.title, data.content, data)
        break
      default:
        showTaskNotification(data.title, data.content, data)
    }

    // 触发消息更新事件
    window.dispatchEvent(new CustomEvent('message-count-updated', { 
      detail: { count: unreadCount.value } 
    }))
  }

  // 处理任务更新
  const handleTaskUpdate = (data: any) => {
    console.log('任务状态更新:', data)
    showTaskNotification('任务更新', `任务"${data.title || '未知任务'}"状态已更新`, data)
    // 可以在这里触发任务列表刷新
    window.dispatchEvent(new CustomEvent('task-list-refresh'))
  }

  // 处理团队通知
  const handleTeamNotification = (data: any) => {
    console.log('团队通知:', data)
    showTeamNotification(data.title || '团队通知', data.message || data.content || '收到新的团队通知', data)
  }

  // 处理任务通知
  const handleTaskNotification = (data: any) => {
    console.log('任务通知:', data)
    unreadCount.value++
    
    showTaskNotification(data.title, data.content, data)
    
    // 触发消息更新事件
    window.dispatchEvent(new CustomEvent('message-count-updated', { 
      detail: { count: unreadCount.value } 
    }))
    
    // 触发任务列表刷新
    window.dispatchEvent(new CustomEvent('task-list-refresh'))
  }

  // 处理项目通知
  const handleProjectNotification = (data: any) => {
    console.log('项目通知:', data)
    unreadCount.value++
    
    showProjectNotification(data.title, data.content, data)
    
    // 触发消息更新事件
    window.dispatchEvent(new CustomEvent('message-count-updated', { 
      detail: { count: unreadCount.value } 
    }))
  }

  // 处理系统通知
  const handleSystemNotification = (data: any) => {
    console.log('系统通知:', data)
    unreadCount.value++
    
    showSystemNotification(data.title, data.content, data)
    
    // 触发消息更新事件
    window.dispatchEvent(new CustomEvent('message-count-updated', { 
      detail: { count: unreadCount.value } 
    }))
  }

  // 事件处理函数
  const handleNewMessageEvent = (event: Event) => {
    const customEvent = event as CustomEvent
    handleNewMessage(customEvent.detail)
  }

  const handleTaskUpdateEvent = (event: Event) => {
    const customEvent = event as CustomEvent
    handleTaskUpdate(customEvent.detail)
  }

  const handleTeamNotificationEvent = (event: Event) => {
    const customEvent = event as CustomEvent
    handleTeamNotification(customEvent.detail)
  }

  const handleTaskNotificationEvent = (event: Event) => {
    const customEvent = event as CustomEvent
    handleTaskNotification(customEvent.detail)
  }

  const handleProjectNotificationEvent = (event: Event) => {
    const customEvent = event as CustomEvent
    handleProjectNotification(customEvent.detail)
  }

  const handleSystemNotificationEvent = (event: Event) => {
    const customEvent = event as CustomEvent
    handleSystemNotification(customEvent.detail)
  }

  // 初始化WebSocket
  const initWebSocket = async () => {
    // 检查用户是否已登录
    if (!userStore.isLoggedIn) {
      console.log('用户未登录，跳过WebSocket连接')
      return
    }

    // 设置事件回调
    wsService.onConnect(handleConnect)
    wsService.onDisconnect(handleDisconnect)
    wsService.onError(handleError)

    // 注册消息处理器
    wsService.on('new_message', handleNewMessage)
    wsService.on('task_update', handleTaskUpdate)
    wsService.on('team_notification', handleTeamNotification)

    // 监听自定义事件
    window.addEventListener('new-message', handleNewMessageEvent)
    window.addEventListener('task-update', handleTaskUpdateEvent)
    window.addEventListener('team-notification', handleTeamNotificationEvent)
    window.addEventListener('task-notification', handleTaskNotificationEvent)
    window.addEventListener('project-notification', handleProjectNotificationEvent)
    window.addEventListener('system-notification', handleSystemNotificationEvent)

    // 请求通知权限
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }

    // 连接WebSocket
    await wsService.connect()
    updateConnectionState()
  }

  // 监听用户登录状态变化
  watch(() => userStore.isLoggedIn, (isLoggedIn) => {
    if (isLoggedIn) {
      console.log('用户已登录，建立WebSocket连接')
      initWebSocket()
    } else {
      console.log('用户已登出，断开WebSocket连接')
      wsService.disconnect()
      updateConnectionState()
      unreadCount.value = 0
    }
  })

  // 发送消息
  const sendMessage = (message: WebSocketMessage) => {
    wsService.send(message)
  }

  // 手动连接
  const connect = async () => {
    if (!userStore.isLoggedIn) {
      console.warn('用户未登录，无法建立WebSocket连接')
      return
    }
    await wsService.connect()
    updateConnectionState()
  }

  // 手动断开
  const disconnect = () => {
    wsService.disconnect()
    updateConnectionState()
  }

  // 重置未读消息计数
  const resetUnreadCount = () => {
    unreadCount.value = 0
  }

  // 组件挂载时初始化
  onMounted(() => {
    // 如果用户已经登录，立即初始化WebSocket
    if (userStore.isLoggedIn) {
      initWebSocket()
    }
  })

  // 组件卸载时清理
  onUnmounted(() => {
    // 移除事件监听器
    window.removeEventListener('new-message', handleNewMessageEvent)
    window.removeEventListener('task-update', handleTaskUpdateEvent)
    window.removeEventListener('team-notification', handleTeamNotificationEvent)
    window.removeEventListener('task-notification', handleTaskNotificationEvent)
    window.removeEventListener('project-notification', handleProjectNotificationEvent)
    window.removeEventListener('system-notification', handleSystemNotificationEvent)
    
    // 清理WebSocket连接
    wsService.disconnect()
  })

  return {
    isConnected,
    connectionState,
    unreadCount,
    sendMessage,
    connect,
    disconnect,
    resetUnreadCount
  }
} 
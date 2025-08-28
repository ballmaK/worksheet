import request from './request'

export interface Message {
  id: number
  title: string
  content: string
  message_type: 'task' | 'team' | 'system' | 'worklog' | 'project' | 'user'
  priority: 'urgent' | 'important' | 'normal' | 'low'
  sender_id?: number
  sender_name?: string
  recipients: number[]
  is_read: boolean
  is_deleted: boolean
  read_at?: string
  created_at: string
  updated_at: string
  message_data?: any
}

export interface MessageStats {
  total_count: number
  unread_count: number
  today_count: number
  week_count: number
  by_type: {
    task: number
    team: number
    system: number
    worklog: number
    project: number
    user: number
  }
}

export interface MessageCreate {
  title: string
  content: string
  message_type: string
  priority?: string
  recipients: number[]
  message_data?: any
}

export interface MessageTemplate {
  id: number
  name: string
  title_template: string
  content_template: string
  message_type: string
  priority: string
  variables: any
  send_via_email: boolean
  send_via_websocket: boolean
  send_via_desktop: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

// 获取消息列表
export const getMessages = async (params?: {
  skip?: number
  limit?: number
  unread_only?: boolean
  message_type?: string
}): Promise<Message[]> => {
  const response = await request.get('/messages/', { params })
  return response.data
}

// 获取消息统计
export const getMessageStats = async (): Promise<MessageStats> => {
  const response = await request.get('/messages/stats')
  return response.data
}

// 获取未读消息数量
export const getUnreadCount = async (): Promise<{ unread_count: number }> => {
  const response = await request.get('/messages/unread-count')
  return response.data
}

// 获取指定消息
export const getMessage = async (messageId: number): Promise<Message> => {
  const response = await request.get(`/messages/${messageId}`)
  return response.data
}

// 标记消息为已读
export const markMessageAsRead = async (messageId: number): Promise<Message> => {
  const response = await request.put(`/messages/${messageId}/read`)
  return response.data
}

// 标记所有消息为已读
export const markAllMessagesAsRead = async (messageType?: string): Promise<{ marked_count: number }> => {
  const response = await request.put('/messages/mark-all-read', {
    params: { message_type: messageType }
  })
  return response.data
}

// 删除消息
export const deleteMessage = async (messageId: number): Promise<Message> => {
  const response = await request.delete(`/messages/${messageId}`)
  return response.data
}

// 获取消息模板列表
export const getMessageTemplates = async (messageType?: string): Promise<MessageTemplate[]> => {
  const response = await request.get('/messages/templates/', {
    params: { message_type: messageType }
  })
  return response.data
}

// 获取指定消息模板
export const getMessageTemplate = async (templateId: number): Promise<MessageTemplate> => {
  const response = await request.get(`/messages/templates/${templateId}`)
  return response.data
}

// 创建消息模板
export const createMessageTemplate = async (template: Partial<MessageTemplate>): Promise<MessageTemplate> => {
  const response = await request.post('/messages/templates/', template)
  return response.data
}

// 更新消息模板
export const updateMessageTemplate = async (templateId: number, template: Partial<MessageTemplate>): Promise<MessageTemplate> => {
  const response = await request.put(`/messages/templates/${templateId}`, template)
  return response.data
}

// 删除消息模板
export const deleteMessageTemplate = async (templateId: number): Promise<MessageTemplate> => {
  const response = await request.delete(`/messages/templates/${templateId}`)
  return response.data
}

// 获取连接状态
export const getConnectionStatus = async (): Promise<{ connected_users: number[] }> => {
  const response = await request.get('/messages/connection-status')
  return response.data
}

// 发送测试通知
export const sendTestNotification = async (): Promise<{ success: boolean; message: string }> => {
  const response = await request.post('/messages/test-notification')
  return response.data
}

// 消息API对象
export const messageApi = {
  getMessages,
  getMessageStats,
  getUnreadCount,
  getMessage,
  markMessageAsRead,
  markAllMessagesAsRead,
  deleteMessage,
  getMessageTemplates,
  getMessageTemplate,
  createMessageTemplate,
  updateMessageTemplate,
  deleteMessageTemplate,
  getConnectionStatus,
  sendTestNotification
} 
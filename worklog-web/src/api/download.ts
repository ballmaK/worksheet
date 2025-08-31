import request from '@/utils/request'

export interface DownloadInfo {
  name: string
  version: string
  filename: string
  size: string
  size_bytes: number
  url: string
  checksum: string
  requirements: string
  features: string[]
  updated_at: string
}

export interface DownloadsResponse {
  status: string
  data: {
    windows: DownloadInfo
    macos: DownloadInfo
    linux: DownloadInfo
  }
  timestamp: string
}

export interface DownloadStats {
  total_downloads: number
  platform_stats: {
    windows: number
    macos: number
    linux: number
  }
  recent_downloads: any[]
  timestamp: string
}

export interface UpdateInfo {
  latest_version: string
  update_available: boolean
  update_url: string | null
  changelog: string[]
  timestamp: string
}

/**
 * 获取所有下载版本信息
 */
export const getDownloads = () => {
  return request<DownloadsResponse>({
    url: '/api/v1/downloads',
    method: 'GET'
  })
}

/**
 * 获取特定平台的下载信息
 */
export const getDownloadInfo = (platform: string) => {
  return request<{ status: string; data: DownloadInfo; timestamp: string }>({
    url: `/api/v1/downloads/${platform}`,
    method: 'GET'
  })
}

/**
 * 下载客户端文件
 */
export const downloadClient = (platform: string) => {
  return request({
    url: `/api/v1/downloads/${platform}/download`,
    method: 'GET',
    responseType: 'blob'
  })
}

/**
 * 检查客户端更新
 */
export const checkUpdates = () => {
  return request<{ status: string; data: UpdateInfo; timestamp: string }>({
    url: '/api/v1/downloads/check-updates',
    method: 'GET'
  })
}

/**
 * 获取下载统计信息
 */
export const getDownloadStats = () => {
  return request<{ status: string; data: DownloadStats; timestamp: string }>({
    url: '/api/v1/downloads/stats',
    method: 'GET'
  })
}

const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 工作模式相关
  toggleWorkMode: () => ipcRenderer.invoke('toggle-work-mode'),
  getWorkMode: () => ipcRenderer.invoke('get-work-mode'),
  
  // 窗口控制
  resizeWindow: (width, height) => ipcRenderer.invoke('resize-window', width, height),
  moveWindowTo: (x, y) => ipcRenderer.invoke('move-window-to', x, y),
  getWindowPosition: () => ipcRenderer.invoke('get-window-position'),
  showMainWindow: () => ipcRenderer.invoke('show-main-window'),
  showTaskBar: () => ipcRenderer.invoke('show-task-bar'),
  hideTaskBar: () => ipcRenderer.invoke('hide-task-bar'),
  
  // 外部链接
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  openAdminPanel: () => ipcRenderer.invoke('open-external', 'http://localhost:8000/docs'),
  
  // 系统通知
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),
  
  // Token管理
  updateToken: (token) => ipcRenderer.send('update-token', token)
})

// 为了兼容性，也暴露electron对象
contextBridge.exposeInMainWorld('electron', {
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),
  toggleWorkMode: () => ipcRenderer.invoke('toggle-work-mode'),
  getWorkMode: () => ipcRenderer.invoke('get-work-mode')
}) 
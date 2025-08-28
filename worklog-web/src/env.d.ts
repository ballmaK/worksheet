/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 扩展window对象类型
declare global {
  interface Window {
    electronAPI?: {
      // 工作模式相关
      toggleWorkMode: () => Promise<boolean>
      getWorkMode: () => Promise<boolean>
      
      // 窗口控制
      resizeWindow: (width: number, height: number) => Promise<void>
      moveWindowTo: (x: number, y: number) => Promise<void>
      getWindowPosition: () => Promise<[number, number]>
      showMainWindow: () => Promise<void>
      showTaskBar: () => Promise<void>
      hideTaskBar: () => Promise<void>
      
      // 外部链接
      openExternal: (url: string) => Promise<void>
      openAdminPanel: () => Promise<void>
      
      // 系统通知
      showNotification: (options: any) => Promise<void>
      
      // Token管理
      updateToken: (token: string) => void
    }
    electron?: {
      showNotification: (options: any) => Promise<void>
      toggleWorkMode: () => Promise<boolean>
      getWorkMode: () => Promise<boolean>
    }
  }
} 
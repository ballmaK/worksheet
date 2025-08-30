// 全局类型声明
declare global {
  interface Window {
    electronAPI?: {
      minimize: () => void;
      close: () => void;
      openCalendar: () => void;
      openMainWindow: () => void;
      toggleMinimize: () => void;
      getTaskTotalDuration: () => Promise<number>;
      // 添加其他electron API方法
    };
    electron?: any;
  }
}

// 扩展AxiosResponse类型
declare module 'axios' {
  interface AxiosResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: any;
    config: any;
    request?: any;
  }
}

// 声明缺失的模块
declare module '@/api/workLog' {
  export const workLogApi: any;
  export const createWorkLog: any;
  export const updateWorkLog: any;
  export const deleteWorkLog: any;
  export const getWorkLogs: any;
}

declare module '@/types/project' {
  export interface Project {
    id: number;
    name: string;
    description: string;
    team_id: number | null;
    status: string;
    start_date: string;
    end_date: string;
    progress: number;
    creator_id: number;
    created_at: string;
    updated_at: string;
  }
  
  export interface ProjectCreate {
    name: string;
    description: string;
    team_id: number | null;
    status: string;
    start_date: string;
    end_date: string;
    progress: number;
  }
}

declare module '@/types/worklog' {
  export interface WorkLog {
    id: number;
    user_id: number;
    task_id: number;
    project_id: number;
    description: string;
    start_time: string;
    end_time: string;
    duration: number;
    status: string;
    created_at: string;
    updated_at: string;
  }
}

export {};

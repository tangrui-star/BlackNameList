/**
 * 筛查相关API
 */
import request from './request'

export interface ScreeningTask {
  id: number
  task_name: string
  file_name: string
  file_path: string
  total_records: number
  processed_records: number
  matched_records: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  created_by: number
  created_at: string
  completed_at?: string
}

export interface ScreeningResult {
  id: number
  task_id: number
  blacklist_id: number
  order_data: any
  match_type: 'phone' | 'name' | 'ktt_name' | 'address'
  match_score: number
  match_details: string
  risk_level: 'low' | 'medium' | 'high'
  created_at: string
}

export interface ScreeningTaskCreate {
  task_name?: string
}

export const screeningApi = {
  // 上传筛查文件
  uploadFile: (file: File, taskName?: string): Promise<ScreeningTask> => {
    const formData = new FormData()
    formData.append('file', file)
    if (taskName) {
      formData.append('task_name', taskName)
    }
    return request.post('/screening/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取筛查任务列表
  getTasks: (params?: {
    skip?: number
    limit?: number
    status?: string
  }): Promise<ScreeningTask[]> => {
    return request.get('/screening/tasks', { params })
  },

  // 获取筛查任务详情
  getTask: (taskId: number): Promise<ScreeningTask> => {
    return request.get(`/screening/tasks/${taskId}`)
  },

  // 开始筛查任务
  startTask: (taskId: number): Promise<{ message: string; task_id: number }> => {
    return request.post(`/screening/tasks/${taskId}/start`)
  },

  // 获取筛查结果
  getResults: (taskId: number, params?: {
    skip?: number
    limit?: number
    risk_level?: string
  }): Promise<ScreeningResult[]> => {
    return request.get(`/screening/tasks/${taskId}/results`, { params })
  },

  // 导出筛查结果
  exportResults: (taskId: number, format: string = 'excel'): Promise<any> => {
    return request.post(`/screening/tasks/${taskId}/export`, null, {
      params: { format },
      responseType: 'blob'
    })
  }
}

import request from './request'

export const adminApi = {
  // 获取系统统计
  getStats: () => {
    return request.get('/admin/stats')
  },

  // 获取系统配置
  getConfig: () => {
    return request.get('/admin/config')
  },

  // 更新系统配置
  updateConfig: (data: any) => {
    return request.put('/admin/config', data)
  },

  // 创建数据备份
  createBackup: () => {
    return request.post('/admin/backup')
  },

  // 获取系统日志
  getLogs: (params: any) => {
    return request.get('/admin/logs', { params })
  }
}

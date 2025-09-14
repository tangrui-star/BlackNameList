import request from './request'

export const blacklistApi = {
  // 获取黑名单列表
  getBlacklistList: (params: any) => {
    return request.post('/blacklist/list', params).then(response => {
      console.log('黑名单API原始响应:', response)
      // 返回完整的分页响应对象
      if (response && typeof response === 'object') {
        return response
      } else {
        console.error('API返回格式错误:', response)
        return { data: [], total: 0, page: 1, size: 20, pages: 0 }
      }
    })
  },

  // 获取黑名单详情
  getBlacklistDetail: (id: number) => {
    return request.post('/blacklist/detail', { blacklist_id: id }).then(response => {
      console.log('黑名单详情API响应:', response)
      return response
    })
  },

  // 创建黑名单
  createBlacklist: (data: any) => {
    return request.post('/blacklist', data)
  },

  // 更新黑名单
  updateBlacklist: (id: number, data: any) => {
    return request.put(`/blacklist/${id}`, data)
  },

  // 删除黑名单
  deleteBlacklist: (id: number) => {
    return request.delete(`/blacklist/${id}`)
  },

  // 批量删除黑名单
  batchDeleteBlacklist: (ids: number[]) => {
    return request.post('/blacklist/batch-delete', { ids })
  },

  // 导入Excel文件
  importBlacklist: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/blacklist/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出黑名单
  exportBlacklist: (params: any) => {
    return request.get('/blacklist/export', { 
      params,
      responseType: 'blob'
    })
  },

  // 获取黑名单变更历史
  getBlacklistHistory: (id: number) => {
    return request.get(`/blacklist/${id}/history`)
  }
}

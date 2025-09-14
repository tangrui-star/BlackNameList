import request from './request'
import type { Group, GroupListResponse, GroupSearchParams, GroupCreate, GroupUpdate, GroupBatchCheckResponse } from '@/types/group'

export const groupApi = {
  // 获取分组列表
  getGroupList: (params: GroupSearchParams): Promise<GroupListResponse> => {
    return request.post('/groups/list', params)
  },

  // 获取分组详情
  getGroup: (id: number): Promise<Group> => {
    return request.post('/groups/detail', { group_id: id })
  },

  // 创建分组
  createGroup: (data: GroupCreate): Promise<Group> => {
    return request.post('/groups/create', data)
  },

  // 更新分组
  updateGroup: (id: number, data: GroupUpdate): Promise<Group> => {
    return request.post('/groups/update', { group_id: id, ...data })
  },

  // 删除分组
  deleteGroup: (id: number): Promise<any> => {
    return request.post('/groups/delete', { group_id: id })
  },

  // 批量检测黑名单
  batchCheckBlacklist: (groupId: number, forceRecheck: boolean = false): Promise<GroupBatchCheckResponse> => {
    return request.post('/groups/batch-check', { 
      group_id: groupId, 
      force_recheck: forceRecheck 
    })
  },

  // 上传Excel文件到分组
  uploadExcelToGroup: (groupId: number, file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(`/groups/upload-excel?group_id=${groupId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

import request from './request'

export const userApi = {
  // 获取用户列表
  getUserList: (params: any) => {
    return request.post('/users/list', params)
  },

  // 获取用户详情
  getUserDetail: (id: number) => {
    return request.get(`/users/${id}`)
  },

  // 创建用户
  createUser: (data: any) => {
    return request.post('/users', data)
  },

  // 更新用户
  updateUser: (id: number, data: any) => {
    return request.put(`/users/${id}`, data)
  },

  // 删除用户
  deleteUser: (id: number) => {
    return request.delete(`/users/${id}`)
  },

  // 获取角色列表
  getRoleList: () => {
    return request.post('/roles/list', {})
  }
}

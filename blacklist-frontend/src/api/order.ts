/**
 * 订单相关API
 */
import request from './request'

export interface OrderSearchParams {
  group_tour_number?: string
  orderer?: string
  contact_phone?: string
  order_status?: string
  is_blacklist_checked?: string
  payment_time_start?: string
  payment_time_end?: string
  skip?: number
  limit?: number
}

export interface OrderCreateData {
  group_tour_number?: string
  orderer?: string
  member_remarks?: string
  payment_time?: string
  group_leader_remarks?: string
  product?: string
  category?: string
  quantity?: number
  order_amount?: number
  refund_amount?: number
  order_status?: string
  pickup_point?: string
  consignee?: string
  contact_phone?: string
  detailed_address?: string
}

export interface OrderUpdateData extends OrderCreateData {}

export interface OrderListResponse {
  data: any[]
  total: number
  page: number
  size: number
}

export interface ExcelUploadResponse {
  success: boolean
  message: string
  imported_count: number
  failed_count: number
  errors: string[]
}

export interface BlacklistCheckResponse {
  is_blacklist: boolean
  risk_level?: string
  match_info?: string
  matched_blacklist_ids: number[]
}

export const orderApi = {
  // 获取订单列表
  getOrderList: (params: OrderSearchParams): Promise<OrderListResponse> => {
    return request.post('/orders/list', params)
  },

  // 获取单个订单
  getOrder: (id: number): Promise<any> => {
    return request.post('/orders/detail', { order_id: id })
  },

  // 创建订单
  createOrder: (data: OrderCreateData): Promise<any> => {
    return request.post('/orders/create', data)
  },

  // 更新订单
  updateOrder: (id: number, data: OrderUpdateData): Promise<any> => {
    return request.post('/orders/update', { order_id: id, ...data })
  },

  // 删除订单
  deleteOrder: (id: number): Promise<any> => {
    return request.post('/orders/delete', { order_id: id })
  },

  // 批量删除订单
  batchDeleteOrders: (ids: number[]): Promise<any> => {
    return request.post('/orders/batch-delete', { ids })
  },

  // 上传Excel文件
  uploadExcel: (file: File): Promise<ExcelUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/orders/upload-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 检测黑名单
  checkBlacklist: (id: number): Promise<BlacklistCheckResponse> => {
    return request.post(`/orders/${id}/check-blacklist`)
  },

  // 批量检测黑名单
  batchCheckBlacklist: (ids: number[]): Promise<{ results: any[] }> => {
    return request.post('/orders/batch-check-blacklist', { order_ids: ids })
  },

  // 导出订单
  exportOrders: (params: any): Promise<any> => {
    return request.post('/orders/export', params, {
      responseType: 'blob'
    })
  }
}

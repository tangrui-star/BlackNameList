/**
 * 黑名单检测相关API
 */
import request from './request'

export interface BlacklistMatch {
  is_match: boolean
  match_type: string
  match_score: number
  match_details: string
  risk_level: string
  blacklist_id: number
  blacklist_reason: string
}

export interface BlacklistCheckResult {
  is_blacklist: boolean
  risk_level: string
  matches: BlacklistMatch[]
  match_count?: number
}

export interface OrderBlacklistInfo {
  order_id: number
  group_tour_number: string
  orderer: string
  contact_phone: string
  detailed_address: string
  order_amount: number
  order_status: string
  risk_level: string
  match_info: string
  match_details: string
  payment_time: string
}

export interface BlacklistStatistics {
  total_orders: number
  checked_orders: number
  blacklist_matches: number
  match_rate: number
  risk_level_distribution: Record<string, number>
}

export const blacklistCheckApi = {
  // 检查单个订单
  checkSingleOrder: (orderId: number): Promise<{
    order_id: number
    order_info: any
    blacklist_check: BlacklistCheckResult
  }> => {
    return request.get(`/blacklist-check/check-order/${orderId}`)
  },

  // 批量检查订单
  checkOrders: (params?: {
    skip?: number
    limit?: number
    risk_level?: string
  }): Promise<{
    total_checked: number
    blacklist_matches: number
    results: Array<{
      order_id: number
      group_tour_number: string
      orderer: string
      contact_phone: string
      blacklist_check: BlacklistCheckResult
    }>
  }> => {
    return request.get('/blacklist-check/check-orders', { params })
  },

  // 获取黑名单匹配的订单列表
  getBlacklistMatches: (params?: {
    skip?: number
    limit?: number
    risk_level?: string
  }): Promise<{
    total_matches: number
    results: OrderBlacklistInfo[]
  }> => {
    return request.get('/blacklist-check/blacklist-matches', { params })
  },

  // 获取统计信息
  getStatistics: (): Promise<BlacklistStatistics> => {
    return request.get('/blacklist-check/statistics')
  }
}

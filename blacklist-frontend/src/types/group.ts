// 分组相关类型定义

export enum GroupStatus {
  ACTIVE = 'active',
  ARCHIVED = 'archived',
  DELETED = 'deleted'
}

export interface GroupBase {
  name: string
  description?: string
  file_name?: string
  file_path?: string
  status: GroupStatus
}

export interface GroupCreate extends GroupBase {}

export interface GroupUpdate {
  name?: string
  description?: string
  status?: GroupStatus
}

export interface GroupInDB extends GroupBase {
  id: number
  total_orders: number
  checked_orders: number
  blacklist_matches: number
  created_by?: number
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface Group extends GroupInDB {}

export interface GroupListResponse {
  data: GroupInDB[]
  total: number
  page: number
  size: number
  pages: number
}

export interface GroupSearchParams {
  skip?: number
  limit?: number
  status?: string
  search?: string
}

export interface GroupBatchCheckResponse {
  group_id: number
  group_name: string
  total_orders: number
  checked_orders: number
  blacklist_matches: number
  new_matches: number
  check_time: string
  status: string
  message: string
}

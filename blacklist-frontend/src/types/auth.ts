// 认证相关类型定义

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  phone?: string
  role_id?: number
  role?: Role
  is_active: boolean
  last_login?: string
  created_at: string
  updated_at: string
}

export interface Role {
  id: number
  name: string
  description?: string
  permissions?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
  phone?: string
}

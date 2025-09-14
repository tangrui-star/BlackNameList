import request from './request'
import type { LoginRequest, LoginResponse, RefreshTokenRequest, User, RegisterRequest } from '@/types/auth'

export const authApi = {
  // 用户登录
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    console.log('发送登录请求到:', '/auth/login', data)
    const response = await request.post('/auth/login', data)
    console.log('登录API原始响应:', response)
    console.log('登录API响应数据:', response)
    return response
  },

  // 刷新token
  refreshToken: async (data: RefreshTokenRequest): Promise<LoginResponse> => {
    const response = await request.post('/auth/refresh', data)
    return response
  },

  // 获取当前用户信息
  getCurrentUser: async (): Promise<User> => {
    const response = await request.get('/auth/me')
    return response
  },

  // 用户登出
  logout: async (): Promise<void> => {
    await request.post('/auth/logout')
  },

  // 用户注册
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await request.post('/auth/register', data)
    return response
  }
}

// 导出单独的注册函数
export const register = authApi.register

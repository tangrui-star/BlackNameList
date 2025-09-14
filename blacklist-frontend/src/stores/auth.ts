import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import type { User, LoginRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role?.name || '')

  // 登录
  const login = async (loginData: LoginRequest): Promise<boolean> => {
    try {
      loading.value = true
      console.log('发送登录请求:', loginData)
      const response = await authApi.login(loginData)
      console.log('登录API响应:', response)
      
      // 检查响应结构
      if (!response || !response.access_token || !response.user) {
        console.error('登录响应格式错误:', response)
        ElMessage.error('登录响应格式错误')
        return false
      }
      
      // 保存token和用户信息
      token.value = response.access_token
      refreshToken.value = response.refresh_token
      user.value = response.user
      
      console.log('保存到store:', {
        token: token.value,
        user: user.value,
        isAuthenticated: isAuthenticated.value
      })
      
      // 保存到localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      console.error('登录错误详情:', error)
      const errorMessage = error.response?.data?.detail || error.message || '登录失败'
      ElMessage.error(errorMessage)
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async (): Promise<void> => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 清除本地存储
      token.value = null
      refreshToken.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      
      console.log('已清除所有认证信息')
      ElMessage.success('已退出登录')
    }
  }

  // 强制清除认证信息
  const clearAuth = (): void => {
    console.log('强制清除认证信息')
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // 刷新token
  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken.value) return false
    
    try {
      const response = await authApi.refreshToken({ refresh_token: refreshToken.value })
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)
      return true
    } catch (error) {
      console.error('刷新token失败:', error)
      await logout()
      return false
    }
  }

  // 获取当前用户信息
  const getCurrentUser = async (): Promise<void> => {
    if (!token.value) {
      console.log('没有token，跳过获取用户信息')
      return
    }
    
    try {
      console.log('开始获取当前用户信息...')
      const response = await authApi.getCurrentUser()
      console.log('获取用户信息响应:', response)
      user.value = response
      localStorage.setItem('user', JSON.stringify(response))
      console.log('用户信息已更新:', user.value)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果token无效，尝试刷新
      if (await refreshAccessToken()) {
        console.log('token刷新成功，重新获取用户信息')
        await getCurrentUser()
      } else {
        console.log('token刷新失败，清除认证信息')
        await logout()
      }
    }
  }

  // 初始化认证状态
  const initializeAuth = async (): Promise<void> => {
    try {
      const savedUser = localStorage.getItem('user')
      const savedToken = localStorage.getItem('access_token')
      
      console.log('初始化认证状态:', {
        hasToken: !!savedToken,
        hasUser: !!savedUser,
        tokenValue: savedToken ? savedToken.substring(0, 50) + '...' : '无'
      })
      
      if (savedUser && savedToken) {
        console.log('从localStorage恢复用户信息')
        // 先恢复本地状态
        token.value = savedToken
        refreshToken.value = localStorage.getItem('refresh_token')
        user.value = JSON.parse(savedUser)
        
        console.log('恢复的认证状态:', {
          token: !!token.value,
          user: !!user.value,
          isAuthenticated: isAuthenticated.value
        })
        
        // 验证token是否有效（不强制获取最新用户信息，避免重复API调用）
        try {
          await getCurrentUser()
          console.log('Token验证成功，用户信息已更新')
        } catch (error) {
          console.warn('Token验证失败，但保持本地状态:', error)
          // 不立即清除认证信息，让用户尝试使用
        }
      } else {
        console.log('没有保存的认证信息，需要重新登录')
        // 确保状态为未认证
        token.value = null
        refreshToken.value = null
        user.value = null
      }
    } catch (error) {
      console.error('初始化认证状态失败:', error)
      // 清除无效的认证信息
      clearAuth()
    }
  }

  // 检查权限
  const hasPermission = (permission: string): boolean => {
    if (!user.value?.role?.permissions) return false
    return user.value.role.permissions.includes(permission)
  }

  // 检查角色
  const hasRole = (role: string): boolean => {
    return userRole.value === role
  }

  // 检查多个角色中的任意一个
  const hasAnyRole = (roles: string[]): boolean => {
    return roles.includes(userRole.value)
  }

  return {
    // 状态
    token,
    refreshToken,
    user,
    loading,
    
    // 计算属性
    isAuthenticated,
    userRole,
    
    // 方法
    login,
    logout,
    clearAuth,
    refreshAccessToken,
    getCurrentUser,
    initializeAuth,
    hasPermission,
    hasRole,
    hasAnyRole
  }
})

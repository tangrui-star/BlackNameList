import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: any) => {
    const authStore = useAuthStore()
    
    console.log('=== 请求拦截器调试信息 ===')
    console.log('请求URL:', config.url)
    console.log('请求方法:', config.method)
    console.log('Token存在:', !!authStore.token)
    console.log('Token值:', authStore.token || '无')
    console.log('Token长度:', authStore.token ? authStore.token.length : 0)
    console.log('用户存在:', !!authStore.user)
    console.log('用户信息:', authStore.user)
    console.log('认证状态:', authStore.isAuthenticated)
    
    // 添加token到请求头
    if (authStore.token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${authStore.token}`
      }
      console.log('✅ 已添加Authorization头')
    } else {
      console.warn('❌ 没有找到token，请求可能失败')
      console.log('localStorage中的token:', localStorage.getItem('access_token'))
    }
    
    console.log('最终请求头:', {
      ...config.headers,
      Authorization: config.headers?.Authorization ? config.headers.Authorization.substring(0, 50) + '...' : '无'
    })
    console.log('=== 请求拦截器调试信息结束 ===')
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  async (error) => {
    const { response } = error
    
    if (response) {
      const { status, data } = response
      
      switch (status) {
        case 401:
          // 未授权，尝试刷新token
          const authStore = useAuthStore()
          if (await authStore.refreshAccessToken()) {
            // 刷新成功，重试原请求
            try {
              const retryResponse = await request(error.config)
              return retryResponse
            } catch (retryError) {
              console.error('重试请求失败:', retryError)
              return Promise.reject(retryError)
            }
          } else {
            // 刷新失败，跳转到登录页
            await authStore.logout()
            router.push('/login')
          }
          break
          
        case 403:
          // 403可能是token过期，尝试刷新token
          const authStore403 = useAuthStore()
          console.warn('收到403错误，尝试刷新token')
          if (await authStore403.refreshAccessToken()) {
            // 刷新成功，重试原请求
            console.log('token刷新成功，重试原请求')
            try {
              const retryResponse = await request(error.config)
              return retryResponse
            } catch (retryError) {
              console.error('重试请求失败:', retryError)
              return Promise.reject(retryError)
            }
          } else {
            // 刷新失败，清除认证信息并跳转到登录页
            console.warn('token刷新失败，清除认证信息并跳转到登录页')
            authStore403.clearAuth()
            router.push('/login')
          }
          break
          
        case 404:
          ElMessage.error('请求的资源不存在')
          break
          
        case 422:
          // 表单验证错误
          if (data.detail && Array.isArray(data.detail)) {
            const errors = data.detail.map((err: any) => err.msg).join(', ')
            ElMessage.error(errors)
          } else {
            ElMessage.error(data.detail || '请求参数错误')
          }
          break
          
        case 500:
          ElMessage.error('服务器内部错误')
          break
          
        default:
          ElMessage.error(data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    
    return Promise.reject(error)
  }
)

export default request

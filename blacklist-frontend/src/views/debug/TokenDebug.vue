<template>
  <div class="token-debug">
    <h2>Token调试页面</h2>
    
    <div class="debug-section">
      <h3>Store状态</h3>
      <p><strong>Token存在:</strong> {{ !!authStore.token }}</p>
      <p><strong>Token值:</strong> {{ authStore.token ? authStore.token.substring(0, 50) + '...' : '无' }}</p>
      <p><strong>用户存在:</strong> {{ !!authStore.user }}</p>
      <p><strong>用户信息:</strong> {{ authStore.user ? JSON.stringify(authStore.user, null, 2) : '无' }}</p>
      <p><strong>认证状态:</strong> {{ authStore.isAuthenticated ? '是' : '否' }}</p>
    </div>
    
    <div class="debug-section">
      <h3>LocalStorage</h3>
      <p><strong>access_token:</strong> {{ localStorage.getItem('access_token') ? localStorage.getItem('access_token')?.substring(0, 50) + '...' : '无' }}</p>
      <p><strong>refresh_token:</strong> {{ localStorage.getItem('refresh_token') ? '有' : '无' }}</p>
      <p><strong>user:</strong> {{ localStorage.getItem('user') || '无' }}</p>
    </div>
    
    <div class="debug-section">
      <h3>操作</h3>
      <button @click="testLogin" :disabled="loading">测试登录</button>
      <button @click="testAPI" :disabled="loading">测试API</button>
      <button @click="clearAll" :disabled="loading">清除所有</button>
      <button @click="refreshPage" :disabled="loading">刷新页面</button>
    </div>
    
    <div class="debug-section" v-if="apiResults.length > 0">
      <h3>API测试结果</h3>
      <div v-for="(result, index) in apiResults" :key="index" class="result-item">
        <strong>{{ result.name }}:</strong> 
        <span :class="result.success ? 'success' : 'error'">
          {{ result.success ? '成功' : '失败' }}
        </span>
        <pre>{{ result.response }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { userApi } from '@/api/user'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const loading = ref(false)
const apiResults = ref<Array<{name: string, success: boolean, response: string}>>([])

const testLogin = async () => {
  loading.value = true
  try {
    const result = await authApi.login({
      username: 'admin',
      password: 'admin123'
    })
    
    apiResults.value.push({
      name: '登录测试',
      success: true,
      response: JSON.stringify(result, null, 2)
    })
    
    ElMessage.success('登录测试成功')
  } catch (error: any) {
    apiResults.value.push({
      name: '登录测试',
      success: false,
      response: error.response?.data || error.message
    })
    ElMessage.error('登录测试失败')
  } finally {
    loading.value = false
  }
}

const testAPI = async () => {
  loading.value = true
  try {
    const result = await userApi.getUserList({ skip: 0, limit: 10 })
    
    apiResults.value.push({
      name: '用户列表API测试',
      success: true,
      response: JSON.stringify(result, null, 2)
    })
    
    ElMessage.success('API测试成功')
  } catch (error: any) {
    apiResults.value.push({
      name: '用户列表API测试',
      success: false,
      response: error.response?.data || error.message
    })
    ElMessage.error('API测试失败')
  } finally {
    loading.value = false
  }
}

const clearAll = () => {
  authStore.clearAuth()
  apiResults.value = []
  ElMessage.success('已清除所有数据')
}

const refreshPage = () => {
  window.location.reload()
}

onMounted(() => {
  console.log('Token调试页面已加载')
  console.log('Store状态:', {
    token: authStore.token,
    user: authStore.user,
    isAuthenticated: authStore.isAuthenticated
  })
  console.log('LocalStorage:', {
    access_token: localStorage.getItem('access_token'),
    refresh_token: localStorage.getItem('refresh_token'),
    user: localStorage.getItem('user')
  })
})
</script>

<style scoped>
.token-debug {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.debug-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
}

.debug-section h3 {
  margin-top: 0;
  color: #333;
}

.result-item {
  margin-bottom: 15px;
  padding: 10px;
  background: white;
  border-radius: 4px;
}

.success {
  color: green;
  font-weight: bold;
}

.error {
  color: red;
  font-weight: bold;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin-top: 5px;
}

button {
  margin-right: 10px;
  margin-bottom: 10px;
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: #337ecc;
}
</style>

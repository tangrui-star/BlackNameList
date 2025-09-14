<template>
  <div class="auth-debug">
    <h2>身份验证调试页面</h2>
    
    <div class="debug-section">
      <h3>认证状态</h3>
      <p><strong>Token:</strong> {{ authStore.token ? authStore.token.substring(0, 50) + '...' : '无' }}</p>
      <p><strong>用户信息:</strong> {{ authStore.user ? JSON.stringify(authStore.user, null, 2) : '无' }}</p>
      <p><strong>是否已认证:</strong> {{ authStore.isAuthenticated ? '是' : '否' }}</p>
      <p><strong>用户角色:</strong> {{ authStore.userRole || '无' }}</p>
    </div>
    
    <div class="debug-section">
      <h3>LocalStorage</h3>
      <p><strong>access_token:</strong> {{ localStorage.getItem('access_token') ? localStorage.getItem('access_token')?.substring(0, 50) + '...' : '无' }}</p>
      <p><strong>refresh_token:</strong> {{ localStorage.getItem('refresh_token') ? '有' : '无' }}</p>
      <p><strong>user:</strong> {{ localStorage.getItem('user') || '无' }}</p>
    </div>
    
    <div class="debug-section">
      <h3>测试API</h3>
      <button @click="testLogin" :disabled="loading">测试登录</button>
      <button @click="testUserList" :disabled="loading">测试用户列表</button>
      <button @click="testRoleList" :disabled="loading">测试角色列表</button>
      <button @click="logout" :disabled="loading">登出</button>
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

const testUserList = async () => {
  loading.value = true
  try {
    const result = await userApi.getUserList({ skip: 0, limit: 10 })
    
    apiResults.value.push({
      name: '用户列表测试',
      success: true,
      response: JSON.stringify(result, null, 2)
    })
    
    ElMessage.success('用户列表测试成功')
  } catch (error: any) {
    apiResults.value.push({
      name: '用户列表测试',
      success: false,
      response: error.response?.data || error.message
    })
    ElMessage.error('用户列表测试失败')
  } finally {
    loading.value = false
  }
}

const testRoleList = async () => {
  loading.value = true
  try {
    const result = await userApi.getRoleList()
    
    apiResults.value.push({
      name: '角色列表测试',
      success: true,
      response: JSON.stringify(result, null, 2)
    })
    
    ElMessage.success('角色列表测试成功')
  } catch (error: any) {
    apiResults.value.push({
      name: '角色列表测试',
      success: false,
      response: error.response?.data || error.message
    })
    ElMessage.error('角色列表测试失败')
  } finally {
    loading.value = false
  }
}

const logout = async () => {
  loading.value = true
  try {
    await authStore.logout()
    ElMessage.success('已登出')
  } catch (error: any) {
    ElMessage.error('登出失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  console.log('认证调试页面已加载')
})
</script>

<style scoped>
.auth-debug {
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

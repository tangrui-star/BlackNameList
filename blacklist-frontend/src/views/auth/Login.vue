<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1 class="login-title">黑名单管理系统</h1>
        <p class="login-subtitle">Blacklist Management System</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名或邮箱"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p class="login-tip">
          默认管理员账户：admin / admin123
        </p>
        <p class="register-link">
          还没有账户？
          <el-button type="text" @click="goToRegister" class="register-button">
            立即注册
          </el-button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { LoginRequest } from '@/types/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const loginFormRef = ref<FormInstance>()

// 表单数据
const loginForm = reactive<LoginRequest>({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 加载状态
const loading = ref(false)

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    console.log('开始登录流程...')
    
    const success = await authStore.login(loginForm)
    
    if (success) {
      console.log('登录成功，准备跳转...')
      console.log('认证状态:', authStore.isAuthenticated)
      console.log('用户信息:', authStore.user)
      console.log('Token:', authStore.token)
      console.log('用户角色:', authStore.user?.role)
      
      // 等待一下确保状态更新完成
      await new Promise(resolve => setTimeout(resolve, 500))
      
      try {
        await router.push('/')
        console.log('路由跳转成功')
      } catch (error) {
        console.error('路由跳转失败:', error)
        // 如果跳转失败，尝试刷新页面
        window.location.href = '/'
      }
    } else {
      console.log('登录失败')
    }
  } catch (error) {
    console.error('登录异常:', error)
  } finally {
    loading.value = false
  }
}

// 跳转到注册页面
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
}

.login-footer {
  text-align: center;
}

.login-tip {
  font-size: 12px;
  color: #95a5a6;
  margin: 0 0 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.register-link {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.register-button {
  color: #409eff;
  font-weight: 500;
  padding: 0;
  margin-left: 5px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-box {
    padding: 30px 20px;
  }
  
  .login-title {
    font-size: 24px;
  }
}
</style>

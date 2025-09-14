<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2>用户注册</h2>
        <p>创建新账户</p>
      </div>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="fullName">
          <el-input
            v-model="registerForm.fullName"
            placeholder="请输入真实姓名（可选）"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="电话" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入电话号码（可选）"
            prefix-icon="Phone"
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleRegister"
            class="register-button"
          >
            注册
          </el-button>
          <el-button @click="goToLogin" class="login-button">
            已有账户？去登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { register as registerApi } from '@/api/auth'

const router = useRouter()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  fullName: '',
  phone: ''
})

// 表单验证规则
const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  fullName: [
    { max: 50, message: '姓名长度不能超过 50 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    const { confirmPassword, ...registerData } = registerForm
    await registerApi(registerData)
    
    ElMessage.success('注册成功！请登录')
    router.push('/login')
  } catch (error: any) {
    console.error('注册失败:', error)
    ElMessage.error(error.response?.data?.detail || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-box {
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.register-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.register-form {
  margin-top: 20px;
}

.register-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  margin-bottom: 15px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 14px;
  color: #666;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}
</style>

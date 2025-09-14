<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被删除
      </div>
      <el-button type="primary" @click="goHome">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.not-found-content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 20px;
  line-height: 1;
}

.error-message {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.error-description {
  font-size: 16px;
  color: #909399;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-message {
    font-size: 24px;
  }
  
  .error-description {
    font-size: 14px;
  }
}
</style>

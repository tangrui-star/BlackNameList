<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  // 应用挂载完成，认证状态由路由守卫处理
  console.log('应用已挂载')
})
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
}
</style>

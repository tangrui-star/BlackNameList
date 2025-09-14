<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="sidebar-header">
        <h2 class="logo">黑名单系统</h2>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        
        <el-menu-item index="/blacklist">
          <el-icon><UserFilled /></el-icon>
          <span>黑名单管理</span>
        </el-menu-item>
        
        <el-menu-item index="/orders">
          <el-icon><Document /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        
        <el-menu-item index="/screening">
          <el-icon><Search /></el-icon>
          <span>订单筛查</span>
        </el-menu-item>
        
        <el-menu-item 
          v-if="hasAnyRole(['超级管理员', '管理员', 'admin'])"
          index="/users"
        >
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item 
          v-if="hasAnyRole(['超级管理员', '管理员', 'admin'])"
          index="/admin"
        >
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-button
            type="text"
            @click="toggleSidebar"
            class="sidebar-toggle"
          >
            <el-icon size="20">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </el-button>
          
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="user-name">{{ user?.full_name || user?.username }}</span>
              <el-icon class="el-icon--right">
                <ArrowDown />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 页面内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  House,
  UserFilled,
  Document,
  Search,
  User,
  Setting,
  Fold,
  Expand,
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏状态
const isCollapse = ref(false)
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '200px')

// 当前用户
const user = computed(() => authStore.user)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta?.title
  }))
})

// 切换侧边栏
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 处理用户下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await authStore.logout()
        router.push('/login')
      } catch (error) {
        // 用户取消
      }
      break
  }
}

// 权限检查
const hasAnyRole = (roles: string[]) => {
  try {
    const userRole = authStore.userRole
    const hasRole = authStore.hasAnyRole(roles)
    console.log('权限检查:', {
      userRole,
      requiredRoles: roles,
      hasRole,
      user: authStore.user
    })
    return hasRole
  } catch (error) {
    console.error('权限检查错误:', error)
    return false
  }
}

// 监听路由变化，自动收起侧边栏（移动端）
watch(route, () => {
  if (window.innerWidth < 768) {
    isCollapse.value = true
  }
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
}

.sidebar {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2b3a4b;
  border-bottom: 1px solid #434a50;
}

.logo {
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.sidebar-menu {
  border: none;
  background: #304156;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
  height: 50px;
  line-height: 50px;
}

.sidebar-menu .el-menu-item:hover {
  background: #263445;
  color: white;
}

.sidebar-menu .el-menu-item.is-active {
  background: #409eff;
  color: white;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.sidebar-toggle {
  font-size: 18px;
  color: #606266;
}

.breadcrumb {
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: #409eff;
  color: white;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .sidebar:not(.el-aside--collapsed) {
    transform: translateX(0);
  }
  
  .main-container {
    margin-left: 0;
  }
  
  .header-left {
    gap: 10px;
  }
  
  .breadcrumb {
    display: none;
  }
  
  .user-name {
    display: none;
  }
}
</style>

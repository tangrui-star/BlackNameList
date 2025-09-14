// @ts-ignore
import { createRouter, createWebHistory } from 'vue-router'
// @ts-ignore
import { useAuthStore } from '@/stores/auth'
// @ts-ignore
import NProgress from 'nprogress'
// @ts-ignore
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({ showSpinner: false })

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { 
      title: '登录',
      requiresAuth: false 
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { 
      title: '注册',
      requiresAuth: false 
    }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue'),
        meta: { 
          title: '仪表板',
          icon: 'House'
        }
      },
      {
        path: '/blacklist',
        name: 'Blacklist',
        component: () => import('@/views/blacklist/BlacklistList.vue'),
        meta: { 
          title: '黑名单管理',
          icon: 'UserFilled'
        }
      },
      {
        path: '/orders',
        name: 'Orders',
        component: () => import('@/views/orders/OrderList.vue'),
        meta: { 
          title: '订单管理',
          icon: 'Document'
        }
      },
      {
        path: '/blacklist/create',
        name: 'BlacklistCreate',
        component: () => import('@/views/blacklist/BlacklistForm.vue'),
        meta: { 
          title: '添加黑名单',
          icon: 'Plus'
        }
      },
      {
        path: '/blacklist/:id/edit',
        name: 'BlacklistEdit',
        component: () => import('@/views/blacklist/BlacklistForm.vue'),
        meta: { 
          title: '编辑黑名单',
          icon: 'Edit'
        }
      },
      {
        path: '/screening',
        name: 'Screening',
        component: () => import('@/views/screening/ScreeningList.vue'),
        meta: { 
          title: '订单筛查',
          icon: 'Search'
        }
      },
      {
        path: '/screening/upload',
        name: 'ScreeningUpload',
        component: () => import('@/views/screening/ScreeningUpload.vue'),
        meta: { 
          title: '上传筛查文件',
          icon: 'Upload'
        }
      },
      {
        path: '/screening/:taskId/results',
        name: 'ScreeningResults',
        component: () => import('@/views/screening/ScreeningResults.vue'),
        meta: { 
          title: '筛查结果',
          icon: 'Document'
        }
      },
      {
        path: '/blacklist-check',
        name: 'BlacklistCheckResults',
        component: () => import('@/views/blacklist/BlacklistCheckResults.vue'),
        meta: { 
          title: '黑名单检测结果',
          icon: 'Warning'
        }
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/admin/UserList.vue'),
        meta: { 
          title: '用户管理',
          icon: 'User',
          roles: ['超级管理员', '管理员']
        }
      },
      {
        path: '/admin',
        name: 'Admin',
        component: () => import('@/views/admin/AdminPanel.vue'),
        meta: { 
          title: '系统管理',
          icon: 'Setting',
          roles: ['超级管理员', '管理员']
        }
      },
      {
        path: '/debug/auth',
        name: 'AuthDebug',
        component: () => import('@/views/debug/AuthDebug.vue'),
        meta: { 
          title: '认证调试',
          icon: 'Tools'
        }
      },
      {
        path: '/debug/token',
        name: 'TokenDebug',
        component: () => import('@/views/debug/TokenDebug.vue'),
        meta: { 
          title: 'Token调试',
          icon: 'Tools'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
    meta: { 
      title: '页面不存在',
      requiresAuth: false 
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 认证状态初始化标志
let authInitialized = false

// 路由守卫
router.beforeEach(async (to: any, _from: any, next: any) => {
  NProgress.start()
  
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 黑名单管理系统` : '黑名单管理系统'
  
  // 如果认证状态还没有初始化，先初始化
  if (!authInitialized) {
    console.log('初始化认证状态...')
    try {
      await authStore.initializeAuth()
      authInitialized = true
      console.log('认证状态初始化完成')
    } catch (error) {
      console.error('认证状态初始化失败:', error)
      // 如果初始化失败，清除可能存在的无效认证信息
      authStore.clearAuth()
    }
  }
  
  // 如果已登录且访问登录页，重定向到首页
  if (to.path === '/login' && authStore.isAuthenticated) {
    console.log('已登录用户访问登录页，重定向到首页')
    next('/')
    return
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    // 如果token存在但用户信息不存在，尝试获取用户信息
    if (authStore.token && !authStore.user) {
      console.log('Token存在但用户信息缺失，尝试获取用户信息')
      try {
        await authStore.getCurrentUser()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 如果获取失败，清除认证状态
        await authStore.logout()
        next('/login')
        return
      }
    }
    
    console.log('检查认证状态:', {
      token: !!authStore.token,
      user: !!authStore.user,
      isAuthenticated: authStore.isAuthenticated,
      path: to.path
    })
    
    // 确保认证状态是最新的
    if (!authStore.token || !authStore.user) {
      console.log('认证失败，重定向到登录页')
      next('/login')
      return
    }
    
    // 检查角色权限
    if (to.meta.roles && authStore.user?.role?.name && !to.meta.roles.includes(authStore.user.role.name)) {
      next('/')
      return
    }
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router

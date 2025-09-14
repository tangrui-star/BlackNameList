/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'nprogress' {
  interface NProgress {
    configure(options: any): void
    start(): void
    done(): void
  }
  const NProgress: NProgress
  export default NProgress
}

declare module 'nprogress/nprogress.css' {
  const content: string
  export default content
}

declare module '@/views/auth/Login.vue' {
  const component: any
  export default component
}

declare module '@/views/auth/Register.vue' {
  const component: any
  export default component
}

declare module '@/components/layout/AppLayout.vue' {
  const component: any
  export default component
}

declare module '@/views/dashboard/Dashboard.vue' {
  const component: any
  export default component
}

declare module '@/views/blacklist/BlacklistList.vue' {
  const component: any
  export default component
}

declare module '@/views/blacklist/BlacklistForm.vue' {
  const component: any
  export default component
}

declare module '@/views/screening/ScreeningList.vue' {
  const component: any
  export default component
}

declare module '@/views/screening/ScreeningUpload.vue' {
  const component: any
  export default component
}

declare module '@/views/screening/ScreeningResults.vue' {
  const component: any
  export default component
}

declare module '@/views/admin/UserList.vue' {
  const component: any
  export default component
}

declare module '@/views/admin/AdminPanel.vue' {
  const component: any
  export default component
}

declare module '@/views/debug/AuthDebug.vue' {
  const component: any
  export default component
}

declare module '@/views/debug/TokenDebug.vue' {
  const component: any
  export default component
}

declare module '@/views/error/NotFound.vue' {
  const component: any
  export default component
}

declare module '@/views/orders/OrderList.vue' {
  const component: any
  export default component
}

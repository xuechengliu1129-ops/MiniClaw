import { createRouter, createWebHistory } from 'vue-router'
import Chat from '@/pages/Chat.vue'
import Dashboard from '@/pages/Dashboard.vue'
import Skills from '@/pages/Skills.vue'
import Models from '@/pages/Models.vue'
import Memory from '@/pages/Memory.vue'
import Feishu from '@/pages/Feishu.vue'
import Gateway from '@/pages/Gateway.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: Chat,
    meta: { title: '智能对话' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '系统概览' },
  },
  {
    path: '/skills',
    name: 'Skills',
    component: Skills,
    meta: { title: '技能管理' },
  },
  {
    path: '/models',
    name: 'Models',
    component: Models,
    meta: { title: '模型配置' },
  },
  {
    path: '/memory',
    name: 'Memory',
    component: Memory,
    meta: { title: '记忆管理' },
  },
  {
    path: '/feishu',
    name: 'Feishu',
    component: Feishu,
    meta: { title: '飞书集成' },
  },
  {
    path: '/gateway',
    name: 'Gateway',
    component: Gateway,
    meta: { title: '网关监控' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局路由守卫（本地模式，无需认证）
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - MiniClaw`
  next()
})

export default router
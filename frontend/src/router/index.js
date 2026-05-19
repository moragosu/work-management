import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Progress from '../views/Progress.vue'
import Admin from '../views/Admin.vue'
import Help from '../views/Help.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard, meta: { title: '대시보드' } },
  { path: '/progress', component: Progress, meta: { title: '주간 진행 현황' } },
  { path: '/staff', redirect: '/admin' },
  { path: '/admin', component: Admin, meta: { title: '관리 도구' } },
  { path: '/help', component: Help, meta: { title: '도움말' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})

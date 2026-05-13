import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Progress from '../views/Progress.vue'
import Staff from '../views/Staff.vue'
import Admin from '../views/Admin.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard, meta: { title: '대시보드' } },
  { path: '/progress', component: Progress, meta: { title: '진행도 관리' } },
  { path: '/staff', component: Staff, meta: { title: '인력 관리' } },
  { path: '/admin', component: Admin, meta: { title: '관리 도구' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})

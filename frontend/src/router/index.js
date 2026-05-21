import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Progress from '../views/Progress.vue'
import Admin from '../views/Admin.vue'
import Help from '../views/Help.vue'
import GoRedirect from '../views/GoRedirect.vue'
import Feedback from '../views/Feedback.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard, meta: { title: '대시보드' } },
  { path: '/progress', component: Progress, meta: { title: '주간 진행 현황' } },
  { path: '/staff', redirect: '/admin' },
  { path: '/admin', component: Admin, meta: { title: '관리 도구' } },
  { path: '/feedback', component: Feedback, meta: { title: '피드백' } },
  { path: '/help', component: Help, meta: { title: '도움말' } },
  { path: '/go/:id', component: GoRedirect, meta: { title: '이동 중...' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})

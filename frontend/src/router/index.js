import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Progress from '../views/Progress.vue'
import Admin from '../views/Admin.vue'
import Help from '../views/Help.vue'
import GoRedirect from '../views/GoRedirect.vue'
import Feedback from '../views/Feedback.vue'
import Login from '../views/Login.vue'
import Signup from '../views/Signup.vue'
import Notifications from '../views/Notifications.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: Login, meta: { public: true, title: '로그인' } },
  { path: '/signup', component: Signup, meta: { public: true, title: '회원가입' } },
  { path: '/dashboard', component: Dashboard, meta: { title: '대시보드' } },
  { path: '/progress', component: Progress, meta: { title: '주간 진행 현황' } },
  { path: '/staff', redirect: '/admin' },
  { path: '/admin', component: Admin, meta: { title: '관리 도구' } },
  { path: '/feedback', component: Feedback, meta: { title: '피드백' } },
  { path: '/notifications', component: Notifications, meta: { title: '알림' } },
  { path: '/help', component: Help, meta: { title: '도움말' } },
  { path: '/go/:id', component: GoRedirect, meta: { title: '이동 중...' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  if (to.meta.public) return next()
  const token = localStorage.getItem('token')
  if (!token) return next({ path: '/login', query: { redirect: to.fullPath } })
  next()
})

export default router

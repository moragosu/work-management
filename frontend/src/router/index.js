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
import ChangePassword from '../views/ChangePassword.vue'
import TaskHistory from '../views/TaskHistory.vue'
import IssueHistory from '../views/IssueHistory.vue'
import AnswerHistory from '../views/AnswerHistory.vue'
import ExportReport from '../views/ExportReport.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: Login, meta: { public: true, title: '로그인' } },
  { path: '/signup', component: Signup, meta: { public: true, title: '회원가입' } },
  { path: '/change-password', component: ChangePassword, meta: { title: '비밀번호 변경' } },
  { path: '/dashboard', component: Dashboard, meta: { title: '대시보드' } },
  { path: '/progress', component: Progress, meta: { title: '주간 진행 현황' } },
  { path: '/staff', redirect: '/admin' },
  { path: '/admin', component: Admin, meta: { title: '관리 도구' } },
  { path: '/feedback', component: Feedback, meta: { title: '피드백' } },
  { path: '/notifications', component: Notifications, meta: { title: '알림' } },
  { path: '/help', component: Help, meta: { title: '도움말' } },
  { path: '/tasks/:id/history', component: TaskHistory, meta: { title: '과제 이력' } },
  { path: '/issue-history', component: IssueHistory, meta: { title: '삭제된 이슈 히스토리' } },
  { path: '/answer-history', component: AnswerHistory, meta: { title: '답변 현황 히스토리' } },
  { path: '/export', component: ExportReport, meta: { title: '보고서 내보내기', requiresLeader: true } },
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
  // 임시 비밀번호 사용 중이면 비밀번호 변경 페이지로 강제 이동
  const user = JSON.parse(localStorage.getItem('authUser') || 'null')
  if (user?.force_password_change && to.path !== '/change-password') {
    return next('/change-password')
  }
  if (to.meta.requiresLeader) {
    const isLeader = user?.is_admin || user?.role === 'group_leader' || user?.role === 'part_leader'
    if (!isLeader) return next('/dashboard')
  }
  next()
})

export default router

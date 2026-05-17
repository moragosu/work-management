<template>
  <div>
    <div class="page-header">
      <div>
        <h2>대시보드</h2>
        <div class="subtitle">{{ currentWeek }} · {{ today }}</div>
      </div>
      <button class="btn btn-ghost btn-sm" @click="refresh">🔄 새로고침</button>
    </div>

    <div class="page-body">
      <!-- ① 목표 요약 카드 -->
      <div class="grid-4" style="margin-bottom:24px">
        <div class="card stat-accent stat-accent-blue">
          <div class="card-body stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-value">{{ objectives.length }}</div>
            <div class="stat-label">전체 목표</div>
          </div>
        </div>
        <div class="card stat-accent stat-accent-primary">
          <div class="card-body stat-card">
            <div class="stat-icon">🔄</div>
            <div class="stat-value" style="color:var(--primary)">{{ inProgressCount }}</div>
            <div class="stat-label">진행중</div>
          </div>
        </div>
        <div class="card stat-accent stat-accent-green">
          <div class="card-body stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value" style="color:var(--success)">{{ completedCount }}</div>
            <div class="stat-label">완료</div>
          </div>
        </div>
        <div class="card stat-accent stat-accent-red">
          <div class="card-body stat-card">
            <div class="stat-icon">⚠️</div>
            <div class="stat-value" style="color:var(--danger)">{{ dangerCount }}</div>
            <div class="stat-label">위험</div>
          </div>
        </div>
      </div>

      <!-- ② 액션 패널 3종 -->
      <div class="grid-3" style="margin-bottom:24px;align-items:start">

        <!-- 미답변 질문 -->
        <div class="card action-panel">
          <div class="card-header">
            <div class="panel-title">
              <span class="panel-icon" style="background:#fff7ed;color:var(--orange)">💬</span>
              미답변 질문
            </div>
            <span class="badge" :class="unansweredQuestions.length ? 'badge-orange' : 'badge-gray'">
              {{ unansweredQuestions.length }}건
            </span>
          </div>
          <div class="card-body panel-body">
            <div v-if="actionLoading" class="loading-center" style="padding:24px"><div class="spinner"></div></div>
            <div v-else-if="unansweredQuestions.length === 0" class="panel-empty">
              이번 주 미답변 질문이 없습니다 👍
            </div>
            <ul v-else class="panel-list">
              <li v-for="q in unansweredQuestions" :key="q.id" class="panel-item panel-item-link" @click="goToQuestion(q)">
                <div class="panel-item-main">{{ q.question }}</div>
                <div class="panel-item-sub">
                  <span class="badge badge-blue">{{ getTaskName(q.task_id) }}</span>
                  <span class="panel-goto">바로가기 →</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- 이슈 -->
        <div class="card action-panel">
          <div class="card-header">
            <div class="panel-title">
              <span class="panel-icon" style="background:#fff7ed;color:var(--warning)">🚧</span>
              이슈
            </div>
            <span class="badge" :class="weekIssues.length ? 'badge-yellow' : 'badge-gray'">
              {{ weekIssues.length }}건
            </span>
          </div>
          <div class="card-body panel-body">
            <div v-if="actionLoading" class="loading-center" style="padding:24px"><div class="spinner"></div></div>
            <div v-else-if="weekIssues.length === 0" class="panel-empty">
              이번 주 등록된 이슈가 없습니다 👍
            </div>
            <ul v-else class="panel-list">
              <li v-for="p in weekIssues" :key="p.id" class="panel-item panel-item-link" @click="goToIssue(p)">
                <div class="issue-text">{{ p.issue }}</div>
                <div class="panel-item-sub">
                  <span class="badge badge-blue">{{ getTaskName(p.task_id) }}</span>
                  <span v-if="p.assignee" class="badge badge-gray">{{ p.assignee }}</span>
                  <span class="panel-goto">바로가기 →</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- 미배정 과제 -->
        <div class="card action-panel">
          <div class="card-header">
            <div class="panel-title">
              <span class="panel-icon" style="background:#f0f4ff;color:var(--primary)">👤</span>
              미배정 과제
            </div>
            <span class="badge" :class="unassignedTasks.length ? 'badge-red' : 'badge-gray'">
              {{ unassignedTasks.length }}건
            </span>
          </div>
          <div class="card-body panel-body">
            <div v-if="actionLoading" class="loading-center" style="padding:24px"><div class="spinner"></div></div>
            <div v-else-if="unassignedTasks.length === 0" class="panel-empty">
              모든 과제에 담당자가 배정되어 있습니다 👍
            </div>
            <ul v-else class="panel-list">
              <li v-for="t in unassignedTasks" :key="t.id" class="panel-item panel-item-link" @click="goToTask(t)">
                <div class="panel-item-main">{{ t.name }}</div>
                <div class="panel-item-sub">
                  <span class="badge badge-blue">{{ t.id }}</span>
                  <span class="badge badge-gray">{{ getObjectiveName(t.objective_id) }}</span>
                  <span class="panel-goto">바로가기 →</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- ③ 목표 카드 목록 -->
      <div class="section-header" style="margin-bottom:12px">
        <span class="section-header-title">목표 현황</span>
      </div>
      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="objectives.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>등록된 목표가 없습니다. 관리 도구에서 목표를 추가하세요.</p>
      </div>
      <div v-else class="grid-2" style="gap:16px">
        <div v-for="obj in objectives" :key="obj.id" class="card obj-card">
          <div class="card-header">
            <div class="flex-center gap-8" style="min-width:0;flex:1">
              <span class="obj-id-badge">{{ obj.id }}</span>
              <span class="obj-name">{{ obj.name }}</span>
            </div>
            <span :class="statusBadgeClass(obj.status)" style="flex-shrink:0">{{ obj.status }}</span>
          </div>
          <div class="card-body" style="padding:12px 16px">
            <div v-if="obj.key_results && obj.key_results.length > 0">
              <div class="section-title">Key Results <span class="text-muted">({{ obj.key_results.length }})</span></div>
              <div class="kr-list">
                <div v-for="kr in obj.key_results" :key="kr.id" class="kr-item">
                  <span class="badge badge-blue" style="width:36px;justify-content:center">{{ kr.id }}</span>
                  <span class="text-sm">{{ kr.name }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-sm text-muted">Key Results 없음</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import axios from 'axios'
import { parseIds } from '../utils/parseIds.js'

const router = useRouter()

const objectives = ref([])
const tasks      = ref([])
const staffList  = ref([])
const questions  = ref([])
const progressList = ref([])

const loading = ref(false)
const actionLoading = ref(false)

const today = new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

function getCurrentWeekNumber() {
  const d = new Date()
  const start = new Date(d.getFullYear(), 0, 1)
  return Math.ceil(((d - start) / 86400000 + start.getDay() + 1) / 7)
}
const currentWeek = `W${getCurrentWeekNumber()}`

// ── 목표 통계 ──
const inProgressCount = computed(() => objectives.value.filter(o => o.status === '진행중').length)
const completedCount  = computed(() => objectives.value.filter(o => o.status === '완료').length)
const dangerCount     = computed(() => objectives.value.filter(o => o.status === '위험').length)

// ── 액션 패널 데이터 ──
const unansweredQuestions = computed(() =>
  questions.value.filter(q => !q.answers || q.answers.length === 0)
)

const weekIssues = computed(() =>
  progressList.value.filter(p => p.issue && p.issue.trim())
)

const assignedTaskIds = computed(() => {
  const ids = new Set()
  staffList.value.forEach(s => {
    parseIds(s.selected_tasks).forEach(id => ids.add(id))
  })
  return ids
})

const unassignedTasks = computed(() =>
  tasks.value.filter(t => !assignedTaskIds.value.has(t.id))
)

// ── 헬퍼 ──
function getTaskName(taskId) {
  return tasks.value.find(t => t.id === taskId)?.name || taskId
}
function getObjectiveName(objectiveId) {
  return objectives.value.find(o => o.id === objectiveId)?.name || objectiveId
}
function statusBadgeClass(status) {
  return { '진행중': 'badge badge-blue', '완료': 'badge badge-green', '위험': 'badge badge-red' }[status] || 'badge badge-gray'
}

// ── 바로가기 네비게이션 ──
function goToQuestion(q) {
  router.push({ path: '/progress', query: { week: currentWeek, focusQuestion: q.id } })
}
function goToIssue(p) {
  router.push({ path: '/progress', query: { week: currentWeek, focusIssue: p.task_id } })
}
function goToTask(t) {
  router.push({ path: '/admin', query: { tab: 'task', focusTask: t.id } })
}

// ── 데이터 로드 ──
async function refresh() {
  loading.value = true
  actionLoading.value = true
  try {
    const [oRes, tRes, sRes] = await Promise.all([
      axios.get('/api/okrs'),
      axios.get('/api/tasks'),
      axios.get('/api/staff'),
    ])
    objectives.value = oRes.data
    tasks.value      = tRes.data
    staffList.value  = sRes.data

    const [qRes, pRes] = await Promise.all([
      axios.get('/api/qna/questions', { params: { week: currentWeek } }),
      axios.get('/api/progress',      { params: { week: currentWeek } }),
    ])
    questions.value    = qRes.data
    progressList.value = pRes.data
  } finally {
    loading.value = false
    actionLoading.value = false
  }
}

onMounted(refresh)
</script>

<style scoped>
/* ── 통계 카드 ── */
.stat-accent { border-top: 3px solid var(--outline); }
.stat-accent-blue    { border-top-color: var(--primary); }
.stat-accent-primary { border-top-color: #6366f1; }
.stat-accent-green   { border-top-color: var(--success); }
.stat-accent-red     { border-top-color: var(--danger); }
.stat-icon { font-size: 20px; margin-bottom: 6px; line-height: 1; }

/* ── 액션 패널 ── */
.action-panel { display: flex; flex-direction: column; }

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.panel-icon {
  width: 28px; height: 28px;
  border-radius: var(--radius-sm);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}

.panel-body {
  padding: 12px 16px !important;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-empty {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 16px 0;
}

.panel-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding: 0;
  max-height: 220px;
  overflow-y: auto;
}

.panel-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 10px;
  background: var(--gray-50);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--outline);
}

.panel-item-main {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
  word-break: keep-all;
}

.issue-text {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
  word-break: keep-all;
  white-space: pre-wrap;
}

.panel-item-sub {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.panel-item-link {
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.panel-item-link:hover {
  background: var(--primary-light);
  border-left-color: var(--primary);
}

.panel-goto {
  font-size: 11px;
  color: var(--primary);
  margin-left: auto;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}
.panel-item-link:hover .panel-goto { opacity: 1; }

/* ── 섹션 헤더 ── */
.section-header { display: flex; align-items: center; gap: 8px; }
.section-header-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ── 목표 카드 ── */
.obj-card { transition: box-shadow .2s, transform .15s; }
.obj-card:hover { box-shadow: var(--shadow-l2); transform: translateY(-1px); }

.obj-id-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px;
  background: var(--primary-light); color: var(--primary);
  border-radius: var(--radius-md);
  font-weight: 700; font-size: 13px;
  flex-shrink: 0;
}
.obj-name {
  font-weight: 600; font-size: 14px;
  color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* ── KR ── */
.section-title {
  font-size: 11px; font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.04em;
  margin-bottom: 8px;
}
.kr-list { display: flex; flex-direction: column; gap: 4px; }
.kr-item {
  display: flex; align-items: center; gap: 8px;
  background: var(--gray-50);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
}
</style>

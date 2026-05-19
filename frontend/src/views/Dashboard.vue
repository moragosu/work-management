<template>
  <div>
    <div class="page-header">
      <div>
        <h2>대시보드</h2>
        <div class="subtitle">{{ currentWeek }} · {{ today }}</div>
      </div>
      <button class="btn btn-ghost btn-sm" @click="refresh" data-tooltip="데이터를 최신 상태로 갱신">
        <span class="material-symbols-outlined" style="font-size:16px;width:16px;height:16px">refresh</span>
        새로고침
      </button>
    </div>

    <div class="page-body">
      <!-- ① 이번 주 실용 지표 -->
      <div class="grid-4" style="margin-bottom:24px">
        <div class="card stat-accent" :class="unansweredQuestions.length ? 'stat-accent-orange' : 'stat-accent-green'" data-tooltip="전체 기간 중 아직 답변이 달리지 않은 질문 수" data-tooltip-pos="bottom">
          <div class="card-body stat-card">
            <span class="material-symbols-outlined stat-icon" :class="unansweredQuestions.length ? 'stat-icon-orange' : 'stat-icon-green'">quiz</span>
            <div class="stat-value" :style="unansweredQuestions.length ? 'color:var(--orange,#f97316)' : 'color:var(--success)'">{{ unansweredQuestions.length }}</div>
            <div class="stat-label">미답변 Q&A</div>
          </div>
        </div>
        <div class="card stat-accent" :class="weekIssues.length ? 'stat-accent-yellow' : 'stat-accent-green'" data-tooltip="이번 주 등록된 이슈 수" data-tooltip-pos="bottom">
          <div class="card-body stat-card">
            <span class="material-symbols-outlined stat-icon" :class="weekIssues.length ? 'stat-icon-yellow' : 'stat-icon-green'">warning</span>
            <div class="stat-value" :style="weekIssues.length ? 'color:var(--warning)' : 'color:var(--success)'">{{ weekIssues.length }}</div>
            <div class="stat-label">이번 주 이슈</div>
          </div>
        </div>
        <div class="card stat-accent" :class="unassignedTasks.length ? 'stat-accent-red' : 'stat-accent-green'" data-tooltip="담당자가 지정되지 않은 과제 수" data-tooltip-pos="bottom">
          <div class="card-body stat-card">
            <span class="material-symbols-outlined stat-icon" :class="unassignedTasks.length ? 'stat-icon-red' : 'stat-icon-green'">person_off</span>
            <div class="stat-value" :style="unassignedTasks.length ? 'color:var(--danger)' : 'color:var(--success)'">{{ unassignedTasks.length }}</div>
            <div class="stat-label">미배정 과제</div>
          </div>
        </div>
        <div class="card stat-accent stat-accent-blue" data-tooltip="이번 주 컨플루언스 링크 등록 현황" data-tooltip-pos="bottom">
          <div class="card-body stat-card">
            <span class="material-symbols-outlined stat-icon stat-icon-blue">link</span>
            <div class="stat-value" style="color:var(--primary)">{{ confluenceThisWeek }}<span class="stat-denom">/{{ flatTaskRows.length }}</span></div>
            <div class="stat-label">컨플루언스 등록</div>
            <div class="stat-mini-bar">
              <div class="stat-mini-fill" :style="{ width: flatTaskRows.length ? `${Math.round(confluenceThisWeek / flatTaskRows.length * 100)}%` : '0%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- ② 액션 패널 3종 -->
      <div class="grid-3" style="margin-bottom:24px;align-items:start">

        <!-- 미답변 질문 -->
        <div class="card action-panel">
          <div class="card-header">
            <div class="panel-title">
              <span class="panel-icon" style="background:#fff7ed;color:var(--orange)">
                <span class="material-symbols-outlined">forum</span>
              </span>
              미답변 질문
            </div>
            <span class="badge" :class="unansweredQuestions.length ? 'badge-orange' : 'badge-gray'">
              {{ unansweredQuestions.length }}건
            </span>
          </div>
          <div class="card-body panel-body">
            <div v-if="actionLoading" class="loading-center" style="padding:24px"><div class="spinner"></div></div>
            <div v-else-if="unansweredQuestions.length === 0" class="panel-empty">
              미답변 질문이 없습니다 👍
            </div>
            <ul v-else class="panel-list">
              <li v-for="q in unansweredQuestions" :key="q.id" class="panel-item panel-item-link" @click="goToQuestion(q)">
                <div class="panel-item-main">{{ q.question }}</div>
                <div class="panel-item-sub">
                  <span class="badge badge-blue">{{ getTaskName(q.task_id) }}</span>
                  <span class="badge badge-gray">{{ formatWeekLabel(q.week) }}</span>
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
              <span class="panel-icon" style="background:#fff7ed;color:var(--warning)">
                <span class="material-symbols-outlined">construction</span>
              </span>
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
              <span class="panel-icon" style="background:#f0f4ff;color:var(--primary)">
                <span class="material-symbols-outlined">person_off</span>
              </span>
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

      <!-- ③④ 파트원별 활동 현황 + 주간 등록 현황 -->
      <div class="side-panel-grid">

        <!-- 파트원별 활동 현황 -->
        <div class="side-panel-col">
          <div class="section-header section-header-toggle" @click="activityOpen = !activityOpen" data-tooltip="클릭하여 접기 / 펼치기" data-tooltip-pos="bottom">
            <span class="section-header-title">파트원별 활동 현황</span>
            <span class="panel-count-badge">파트원 {{ staffList.length }}명</span>
            <span class="material-symbols-outlined section-chevron" :class="{ open: activityOpen }">expand_more</span>
          </div>
          <div v-if="activityOpen" class="card panel-card">
            <div v-if="staffList.length === 0" class="panel-empty" style="padding:24px">파트원 정보가 없습니다.</div>
            <div v-else class="activity-scroll">
              <table>
                <thead>
                  <tr>
                    <th>파트원</th>
                    <th data-tooltip="배정된 과제 수 (누적)">담당 과제</th>
                    <th data-tooltip="등록한 이슈 수 (누적)">이슈 등록</th>
                    <th data-tooltip="Q&A에 달린 답변 수 (누적)">Q&A 답변</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in staffList" :key="s.id" style="cursor:default">
                    <td style="vertical-align:middle">
                      <div class="member-cell">
                        <span class="member-avatar">{{ s.name[0] }}</span>
                        <div>
                          <div class="member-name">{{ s.name }}</div>
                          <div class="member-role">{{ s.role }}</div>
                        </div>
                      </div>
                    </td>
                    <td style="vertical-align:middle">
                      <div class="stat-bar-row">
                        <span class="stat-num">{{ memberStatsMap[s.name]?.tasks ?? 0 }}</span>
                        <div class="stat-bar"><div class="stat-fill stat-fill-blue" :style="{ width: barWidth(memberStatsMap[s.name]?.tasks, maxStats.tasks) }"></div></div>
                      </div>
                    </td>
                    <td style="vertical-align:middle">
                      <div class="stat-bar-row">
                        <span class="stat-num">{{ memberStatsMap[s.name]?.issues ?? 0 }}</span>
                        <div class="stat-bar"><div class="stat-fill stat-fill-orange" :style="{ width: barWidth(memberStatsMap[s.name]?.issues, maxStats.issues) }"></div></div>
                      </div>
                    </td>
                    <td style="vertical-align:middle">
                      <div class="stat-bar-row">
                        <span class="stat-num">{{ memberStatsMap[s.name]?.answers ?? 0 }}</span>
                        <div class="stat-bar"><div class="stat-fill stat-fill-green" :style="{ width: barWidth(memberStatsMap[s.name]?.answers, maxStats.answers) }"></div></div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 주간 등록 현황 -->
        <div class="side-panel-col">
          <div class="section-header section-header-toggle" @click="matrixOpen = !matrixOpen" data-tooltip="클릭하여 접기 / 펼치기" data-tooltip-pos="bottom">
            <span class="section-header-title">주간 등록 현황</span>
            <span class="panel-count-badge">과제 {{ flatTaskRows.length }}건</span>
            <div class="matrix-legend-inline">
              <span class="material-symbols-outlined matrix-legend-icon matrix-icon-link">link</span><span>컨플루언스</span>
              <span class="material-symbols-outlined matrix-legend-icon matrix-icon-issue">warning</span><span>이슈</span>
              <span class="matrix-count matrix-count-legend">N</span><span>Q&A</span>
            </div>
            <span class="material-symbols-outlined section-chevron" :class="{ open: matrixOpen }">expand_more</span>
          </div>
          <div v-if="matrixOpen" class="card panel-card" style="overflow:hidden">
            <div v-if="flatTaskRows.length === 0" class="panel-empty" style="padding:24px">등록된 과제가 없습니다</div>
            <div v-else class="matrix-wrap">
              <table class="matrix-table">
                <thead>
                  <tr>
                    <th class="matrix-task-th">과제</th>
                    <th v-for="w in allWeeks" :key="w" class="matrix-week-th" :class="{ 'matrix-col-current': w === currentWeek }">{{ w }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in flatTaskRows" :key="row.id">
                    <td class="matrix-task-td">
                      <span v-if="row.parentName" class="matrix-parent">{{ row.parentName }} › </span>{{ row.selfName }}
                    </td>
                    <td v-for="w in allWeeks" :key="w" class="matrix-cell" :class="{ 'matrix-col-current': w === currentWeek }">
                      <div class="matrix-cell-icons">
                        <span v-if="confluenceMap[row.id]?.has(w)" class="material-symbols-outlined matrix-icon matrix-icon-link" title="컨플루언스 등록">link</span>
                        <span v-if="issueMap[row.id]?.has(w)" class="material-symbols-outlined matrix-icon matrix-icon-issue" title="이슈 등록">warning</span>
                        <span v-if="qnaMap[row.id]?.[w]" class="matrix-count matrix-count-sm" :title="`Q&A ${qnaMap[row.id][w]}건`">{{ qnaMap[row.id][w] }}</span>
                        <span v-if="!confluenceMap[row.id]?.has(w) && !issueMap[row.id]?.has(w) && !qnaMap[row.id]?.[w]" class="matrix-dot-no">–</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      <!-- ⑤ 목표 카드 목록 -->
      <div class="section-header" style="margin-top:32px;margin-bottom:12px">
        <span class="section-header-title">목표 현황</span>
      </div>
      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="objectives.length === 0" class="empty-state">
        <span class="material-symbols-outlined empty-icon">assignment</span>
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
import { getCurrentWeek, formatWeekLabel } from '../utils/week.js'
import { statusBadgeClass } from '../utils/status.js'

const router = useRouter()

const objectives = ref([])
const tasks      = ref([])
const staffList  = ref([])
const questions  = ref([])
const progressList = ref([])
const allProgressItems = ref([])
const allQuestions     = ref([])
const allConfluenceLinks = ref([])
const matrixOpen = ref(true)

const loading = ref(false)
const actionLoading = ref(false)
const activityOpen = ref(true)

const today = new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

const currentWeek = getCurrentWeek()

// ── 목표 통계 ──
const inProgressCount = computed(() => objectives.value.filter(o => o.status === '진행중').length)
const completedCount  = computed(() => objectives.value.filter(o => o.status === '완료').length)
const dangerCount     = computed(() => objectives.value.filter(o => o.status === '위험').length)

// ── 액션 패널 데이터 ──
const unansweredQuestions = computed(() =>
  allQuestions.value.filter(q => !q.answers || q.answers.length === 0)
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
  tasks.value.filter(t => {
    if (assignedTaskIds.value.has(t.id)) return false
    if (t.sub_tasks && t.sub_tasks.some(st => assignedTaskIds.value.has(st.id))) return false
    return true
  })
)

// ── 팀원별 활동 통계 ──
const memberStatsMap = computed(() => {
  const map = {}
  staffList.value.forEach(s => {
    map[s.name] = {
      tasks:   parseIds(s.selected_tasks || '').length,
      issues:  allProgressItems.value.filter(p => p.assignee === s.name && p.issue?.trim()).length,
      answers: allQuestions.value.flatMap(q => q.answers || []).filter(a => a.answer_by === s.name).length,
    }
  })
  return map
})

const maxStats = computed(() => {
  const vals = Object.values(memberStatsMap.value)
  if (!vals.length) return { tasks: 1, issues: 1, answers: 1 }
  return {
    tasks:   Math.max(1, ...vals.map(v => v.tasks)),
    issues:  Math.max(1, ...vals.map(v => v.issues)),
    answers: Math.max(1, ...vals.map(v => v.answers)),
  }
})

function barWidth(val, max) {
  if (!val) return '0%'
  return `${Math.max(3, Math.round((val / max) * 100))}%`
}

const latestIssueMap = computed(() => {
  const map = {}
  staffList.value.forEach(s => {
    const items = allProgressItems.value
      .filter(p => p.assignee === s.name && p.issue?.trim())
      .sort((a, b) => {
        const wa = parseInt((a.week || 'W0').slice(1))
        const wb = parseInt((b.week || 'W0').slice(1))
        return wb - wa
      })
    map[s.name] = items[0] ? { week: items[0].week, issue: items[0].issue } : null
  })
  return map
})

// ── 매트릭스 공통 ──
const allWeeks = computed(() => {
  const s = new Set([currentWeek])
  allProgressItems.value.forEach(p => { if (p.week) s.add(p.week) })
  allQuestions.value.forEach(q => { if (q.week) s.add(q.week) })
  allConfluenceLinks.value.forEach(l => { if (l.week) s.add(l.week) })
  return [...s].sort((a, b) => parseInt(a.slice(1)) - parseInt(b.slice(1)))
})

const flatTaskRows = computed(() => {
  const rows = []
  tasks.value.forEach(t => {
    if (t.sub_tasks && t.sub_tasks.length > 0) {
      t.sub_tasks.forEach(st => {
        rows.push({ id: st.id, selfName: st.name || st.id, parentName: t.name })
      })
    } else {
      rows.push({ id: t.id, selfName: t.name, parentName: null })
    }
  })
  return rows
})

const confluenceMap = computed(() => {
  const m = {}
  allConfluenceLinks.value.forEach(l => {
    if (!l.task_id) return
    if (!m[l.task_id]) m[l.task_id] = new Set()
    m[l.task_id].add(l.week)
  })
  return m
})

const issueMap = computed(() => {
  const m = {}
  allProgressItems.value.filter(p => p.issue?.trim()).forEach(p => {
    if (!p.task_id) return
    if (!m[p.task_id]) m[p.task_id] = new Set()
    m[p.task_id].add(p.week)
  })
  return m
})

const qnaMap = computed(() => {
  const m = {}
  allQuestions.value.forEach(q => {
    if (!q.task_id) return
    if (!m[q.task_id]) m[q.task_id] = {}
    m[q.task_id][q.week] = (m[q.task_id][q.week] || 0) + 1
  })
  return m
})

const confluenceThisWeek = computed(() =>
  flatTaskRows.value.filter(r => confluenceMap.value[r.id]?.has(currentWeek)).length
)
const issueThisWeek = computed(() =>
  flatTaskRows.value.filter(r => issueMap.value[r.id]?.has(currentWeek)).length
)
const qnaThisWeek = computed(() =>
  allQuestions.value.filter(q => q.week === currentWeek).length
)

function truncate(text, len) {
  if (!text) return ''
  const first = text.split('\n')[0].trim()
  return first.length > len ? first.slice(0, len) + '…' : first
}

// ── 헬퍼 ──
function getTaskName(taskId) {
  const direct = tasks.value.find(t => t.id === taskId)
  if (direct) return direct.name
  for (const t of tasks.value) {
    const st = (t.sub_tasks || []).find(s => s.id === taskId)
    if (st) return `${t.name} › ${st.name || taskId}`
  }
  return taskId
}
function getObjectiveName(objectiveId) {
  return objectives.value.find(o => o.id === objectiveId)?.name || objectiveId
}
function resolveParentTaskId(taskId) {
  if (tasks.value.find(t => t.id === taskId)) return taskId
  for (const t of tasks.value) {
    if ((t.sub_tasks || []).some(st => st.id === taskId)) return t.id
  }
  return taskId
}
// ── 바로가기 네비게이션 ──
function goToQuestion(q) {
  router.push({ path: '/progress', query: { week: q.week, focusQuestion: q.id } })
}
function goToIssue(p) {
  router.push({ path: '/progress', query: { week: currentWeek, focusIssue: resolveParentTaskId(p.task_id) } })
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

    const [qRes, pRes, allPRes, allQRes, clRes] = await Promise.all([
      axios.get('/api/qna/questions', { params: { week: currentWeek } }),
      axios.get('/api/progress',      { params: { week: currentWeek } }),
      axios.get('/api/progress'),
      axios.get('/api/qna/questions'),
      axios.get('/api/confluence'),
    ])
    questions.value          = qRes.data
    progressList.value       = pRes.data
    allProgressItems.value   = allPRes.data
    allQuestions.value       = allQRes.data
    allConfluenceLinks.value = clRes.data
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
.stat-accent-blue   { border-top-color: var(--primary); }
.stat-accent-green  { border-top-color: var(--success); }
.stat-accent-red    { border-top-color: var(--danger); }
.stat-accent-orange { border-top-color: var(--orange, #f97316); }
.stat-accent-yellow { border-top-color: var(--warning, #f59e0b); }
.stat-icon {
  font-size: 28px;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  width: 32px;
  height: 32px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-icon-blue   { color: var(--primary); }
.stat-icon-green  { color: var(--success); }
.stat-icon-red    { color: var(--danger); }
.stat-icon-orange { color: var(--orange, #f97316); }
.stat-icon-yellow { color: var(--warning, #f59e0b); }
.stat-denom { font-size: 14px; font-weight: 400; color: var(--text-muted); }
.stat-mini-bar { width: 100%; height: 4px; background: var(--gray-100); border-radius: 999px; overflow: hidden; margin-top: 10px; }
.stat-mini-fill { height: 100%; background: var(--primary); border-radius: 999px; transition: width 0.5s ease; }

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
  flex-shrink: 0;
}
.panel-icon .material-symbols-outlined {
  font-size: 16px;
  width: 16px;
  height: 16px;
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
  color: var(--text-muted);
  margin-left: auto;
  flex-shrink: 0;
  transition: color 0.15s;
}
.panel-item-link:hover .panel-goto { color: var(--primary); }

/* ── 사이드 바이 사이드 패널 ── */
.side-panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: flex-start;
  margin-top: 24px;
}
.side-panel-col { display: flex; flex-direction: column; min-width: 0; }
.panel-card {
  margin-top: 12px;
  height: 400px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.activity-scroll { flex: 1; overflow-x: auto; overflow-y: auto; min-height: 0; }
.panel-count-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--gray-100);
  color: var(--text-muted);
}

/* ── 팀원별 활동 현황 ── */
.member-cell { display: flex; align-items: center; gap: 10px; }
.member-avatar {
  width: 32px; height: 32px;
  border-radius: var(--radius-full);
  background: var(--primary-light); color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px; flex-shrink: 0;
}
.member-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.member-role { font-size: 12px; color: var(--text-muted); margin-top: 1px; }

.stat-bar-row { display: flex; align-items: center; gap: 8px; }
.stat-num { font-size: 13px; font-weight: 600; color: var(--text-primary); min-width: 18px; text-align: right; }
.stat-bar { flex: 1; height: 6px; background: var(--gray-100); border-radius: var(--radius-full); overflow: hidden; }
.stat-fill { height: 100%; border-radius: var(--radius-full); transition: width 0.4s ease; }
.stat-fill-blue   { background: var(--primary); }
.stat-fill-orange { background: var(--orange); }
.stat-fill-green  { background: var(--success); }

.latest-issue { display: flex; align-items: center; gap: 8px; min-width: 0; }
.latest-issue-text {
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── 섹션 헤더 ── */
.section-header { display: flex; align-items: center; gap: 8px; }
.section-header-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.section-header-toggle {
  cursor: pointer;
  user-select: none;
}
.section-header-toggle:hover .section-header-title { color: var(--text-primary); }
.section-chevron {
  font-size: 18px; width: 18px; height: 18px;
  color: var(--text-muted);
  transition: transform 0.2s;
  margin-left: auto;
}
.section-chevron.open { transform: rotate(180deg); }

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

/* ── 매트릭스 테이블 ── */
.matrix-legend-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-muted);
  margin-left: 10px;
}
.matrix-legend-icon {
  font-size: 13px;
  width: 13px;
  height: 13px;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.matrix-count-legend {
  min-width: 16px;
  height: 16px;
  font-size: 10px;
  padding: 0 4px;
}
.matrix-cell-icons {
  display: flex;
  gap: 3px;
  align-items: center;
  justify-content: center;
  min-height: 20px;
}
.matrix-icon {
  font-size: 14px;
  width: 14px;
  height: 14px;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  flex-shrink: 0;
}
.matrix-icon-link  { color: var(--primary); }
.matrix-icon-issue { color: #d97706; }
.matrix-count-sm {
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
}

.matrix-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--gray-100);
  color: var(--text-muted);
  margin-left: 6px;
}
.matrix-wrap {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
  min-height: 0;
}
.matrix-table {
  width: max-content;
  min-width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.matrix-task-th {
  text-align: left;
  padding: 8px 14px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: var(--gray-50);
  border-bottom: 1px solid var(--outline);
  white-space: nowrap;
  min-width: 200px;
  position: sticky;
  left: 0;
  z-index: 2;
}
.matrix-week-th {
  text-align: center;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--gray-50);
  border-bottom: 1px solid var(--outline);
  border-left: 1px solid var(--outline);
  white-space: nowrap;
  min-width: 56px;
}
.matrix-col-current {
  background: color-mix(in srgb, var(--primary) 7%, var(--gray-50)) !important;
}
.matrix-task-td {
  padding: 7px 14px;
  font-size: 12px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--outline);
  white-space: nowrap;
  background: var(--surface);
  position: sticky;
  left: 0;
  z-index: 1;
}
.matrix-parent {
  color: var(--text-muted);
  font-size: 11px;
}
.matrix-cell {
  text-align: center;
  padding: 6px 8px;
  border-bottom: 1px solid var(--outline);
  border-left: 1px solid var(--outline);
  vertical-align: middle;
}
.matrix-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: var(--primary);
  font-size: 11px;
  font-weight: 700;
  padding: 0 5px;
}
.matrix-dot-no {
  color: var(--outline);
  font-size: 14px;
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

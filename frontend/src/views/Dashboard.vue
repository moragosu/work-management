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
      <div class="grid-3" style="margin-bottom:24px">
        <div class="card stat-accent" :class="unansweredQuestions.length ? 'stat-accent-orange' : 'stat-accent-green'" data-tooltip="전체 기간 중 아직 답변이 달리지 않은 질문 수" data-tooltip-pos="bottom">
          <div class="card-body stat-card">
            <span class="material-symbols-outlined stat-icon" :class="unansweredQuestions.length ? 'stat-icon-orange' : 'stat-icon-green'">quiz</span>
            <div class="stat-value" :style="unansweredQuestions.length ? 'color:var(--orange,#f97316)' : 'color:var(--success)'">{{ unansweredQuestions.length }}</div>
            <div class="stat-label">미답변 의견/질문 (전체)</div>
          </div>
        </div>
        <div class="card stat-accent" :class="weekIssues.length ? 'stat-accent-yellow' : 'stat-accent-green'" data-tooltip="이번 주 등록된 이슈 수" data-tooltip-pos="bottom">
          <div class="card-body stat-card">
            <span class="material-symbols-outlined stat-icon" :class="weekIssues.length ? 'stat-icon-yellow' : 'stat-icon-green'">warning</span>
            <div class="stat-value" :style="weekIssues.length ? 'color:var(--warning)' : 'color:var(--success)'">{{ weekIssues.length }}</div>
            <div class="stat-label">이번 주 이슈</div>
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

      <!-- ② 파트 공지 -->
      <div v-if="notice || isAdminMode" class="card notice-card" style="margin-bottom:24px">
        <div class="card-header notice-header">
          <div class="panel-title">
            <span class="panel-icon" style="background:#eff6ff;color:var(--primary)">
              <span class="material-symbols-outlined">campaign</span>
            </span>
            파트 공지
          </div>
          <div v-if="isAdminMode && !noticeEditing" style="display:flex;gap:6px;margin-left:auto">
            <button class="btn btn-ghost btn-xs" @click="startEditNotice">수정</button>
          </div>
          <div v-if="noticeEditing" style="display:flex;gap:6px;margin-left:auto">
            <button class="btn btn-ghost btn-sm" @click="cancelEditNotice">취소</button>
            <button class="btn btn-primary btn-sm" :disabled="noticeSaving" @click="saveNotice">저장</button>
          </div>
        </div>
        <div class="card-body" style="padding:16px">
          <div v-if="noticeEditing">
            <TiptapEditor v-model="noticeDraft" height="180px" />
          </div>
          <div v-else-if="notice">
            <TiptapPreview :modelValue="notice" />
          </div>
          <div v-else class="notice-empty">
            공지 내용을 작성하세요. (관리자 모드에서만 표시됩니다)
          </div>
        </div>
      </div>

      <!-- ③ 액션 패널 2종 -->
      <div class="grid-2" style="margin-bottom:24px;align-items:start">

        <!-- 의견/질문 -->
        <div class="card action-panel">
          <div class="card-header panel-header-toggle" @click="panelExpanded.questions = !panelExpanded.questions" data-tooltip="클릭하여 펼치기 / 접기">
            <div class="panel-title">
              <span class="panel-icon" style="background:#fff7ed;color:var(--orange)">
                <span class="material-symbols-outlined">forum</span>
              </span>
              의견/질문
            </div>
            <div class="q-filter-group" @click.stop>
              <button class="q-filter-btn" :class="{ active: qWeekFilter === 'this' }" @click="qWeekFilter = 'this'">이번주</button>
              <button class="q-filter-btn" :class="{ active: qWeekFilter === 'last' }" @click="qWeekFilter = 'last'">지난주</button>
            </div>
            <div class="q-filter-group" @click.stop>
              <button class="q-filter-btn" :class="{ active: questionFilter === 'unanswered' }" @click="questionFilter = 'unanswered'">미답변</button>
              <button class="q-filter-btn" :class="{ active: questionFilter === 'answered' }" @click="questionFilter = 'answered'">답변완료</button>
              <button class="q-filter-btn" :class="{ active: questionFilter === 'all' }" @click="questionFilter = 'all'">전체</button>
            </div>
            <span class="badge" :class="filteredQuestions.length ? (questionFilter === 'answered' ? 'badge-green' : 'badge-orange') : 'badge-gray'">
              {{ filteredQuestions.length }}건
            </span>
            <span class="material-symbols-outlined section-chevron" :class="{ open: panelExpanded.questions }">expand_more</span>
          </div>
          <div class="card-body panel-body">
            <div v-if="actionLoading" class="loading-center" style="padding:24px"><div class="spinner"></div></div>
            <div v-else-if="filteredQuestions.length === 0" class="panel-empty">
              {{ questionFilter === 'answered' ? '답변 완료된 의견/질문이 없습니다' : questionFilter === 'all' ? '등록된 의견/질문이 없습니다' : '미답변 의견/질문이 없습니다 👍' }}
            </div>
            <ul v-else class="panel-list" :class="{ 'panel-list-expanded': panelExpanded.questions }">
              <li v-for="q in filteredQuestions" :key="q.id" class="panel-item panel-item-link" @click="openModal('question', q)">
                <div v-if="q.questioner || (q.targets && q.targets.length)" class="q-targets-row">
                  <span v-if="q.questioner" class="badge badge-purple" style="font-size:11px">{{ q.questioner }}</span>
                  <template v-if="q.targets && q.targets.length">
                    <span class="material-symbols-outlined q-targets-icon">arrow_forward</span>
                    <span v-for="t in q.targets" :key="t" class="q-target-badge">{{ t }}</span>
                  </template>
                </div>
                <div class="panel-item-main">{{ stripMarkdown(q.question) }}</div>
                <div class="panel-item-sub">
                  <span class="badge badge-blue">{{ getTaskName(q.task_id) }}</span>
                  <span class="badge badge-gray">{{ formatWeekLabel(q.week) }}</span>
                  <span class="panel-goto">상세보기 →</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- 이슈 -->
        <div class="card action-panel">
          <div class="card-header panel-header-toggle" @click="panelExpanded.issues = !panelExpanded.issues" data-tooltip="클릭하여 펼치기 / 접기">
            <div class="panel-title">
              <span class="panel-icon" style="background:#fff7ed;color:var(--warning)">
                <span class="material-symbols-outlined">construction</span>
              </span>
              이슈
            </div>
            <div class="q-filter-group" @click.stop>
              <button class="q-filter-btn" :class="{ active: issWeekFilter === 'this' }" @click="issWeekFilter = 'this'">이번주</button>
              <button class="q-filter-btn" :class="{ active: issWeekFilter === 'last' }" @click="issWeekFilter = 'last'">지난주</button>
            </div>
            <span class="badge" :class="filteredIssues.length ? 'badge-yellow' : 'badge-gray'">
              {{ filteredIssues.length }}건
            </span>
            <span class="material-symbols-outlined section-chevron" :class="{ open: panelExpanded.issues }">expand_more</span>
          </div>
          <div class="card-body panel-body">
            <div v-if="actionLoading" class="loading-center" style="padding:24px"><div class="spinner"></div></div>
            <div v-else-if="filteredIssues.length === 0" class="panel-empty">
              등록된 이슈가 없습니다 👍
            </div>
            <ul v-else class="panel-list" :class="{ 'panel-list-expanded': panelExpanded.issues }">
              <li v-for="p in filteredIssues" :key="p.id" class="panel-item panel-item-link" @click="openModal('issue', p)">
                <div class="issue-text">{{ stripMarkdown(p.issue) }}</div>
                <div class="panel-item-sub">
                  <span class="badge badge-blue">{{ getTaskName(p.task_id) }}</span>
                  <span v-if="p.assignee" class="badge badge-gray">{{ p.assignee }}</span>
                  <span class="panel-goto">상세보기 →</span>
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
            <div class="q-filter-group" style="margin-left:8px" @click.stop>
              <button class="q-filter-btn" :class="{ active: activityWeek === 'this' }" @click="activityWeek = 'this'">이번주</button>
              <button class="q-filter-btn" :class="{ active: activityWeek === 'last' }" @click="activityWeek = 'last'">지난주</button>
            </div>
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
                    <th data-tooltip="해당 주 등록한 이슈 수">이슈</th>
                    <th data-tooltip="해당 주 등록한 질문 수">질문</th>
                    <th data-tooltip="해당 주 작성한 답변 수">답변</th>
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
                        <span class="stat-num stat-num-q">{{ memberStatsMap[s.name]?.questions ?? 0 }}</span>
                        <div class="stat-bar"><div class="stat-fill stat-fill-purple" :style="{ width: barWidth(memberStatsMap[s.name]?.questions, maxStats.questions) }"></div></div>
                      </div>
                    </td>
                    <td style="vertical-align:middle">
                      <div class="stat-bar-row">
                        <span class="stat-num stat-num-a">{{ memberStatsMap[s.name]?.answers ?? 0 }}</span>
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
              <span class="matrix-count matrix-count-legend">N</span><span>의견/질문</span>
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
                    <td class="matrix-task-td matrix-task-link" @click="goToProgressTask(row)" data-tooltip="진행현황에서 보기">
                      <span v-if="row.parentName" class="matrix-parent">{{ row.parentName }} › </span>{{ row.selfName }}
                    </td>
                    <td v-for="w in allWeeks" :key="w" class="matrix-cell" :class="{ 'matrix-col-current': w === currentWeek }">
                      <div class="matrix-cell-icons">
                        <a v-if="confluenceMap[row.id]?.has(w)" :href="confluenceUrlMap[row.id]?.[w]" target="_blank" class="matrix-icon-link-anchor" title="컨플루언스 열기">
                          <span class="material-symbols-outlined matrix-icon matrix-icon-link">link</span>
                        </a>
                        <span v-if="issueMap[row.id]?.has(w)" class="material-symbols-outlined matrix-icon matrix-icon-issue" title="이슈 등록">warning</span>
                        <span v-if="qnaMap[row.id]?.[w]" class="matrix-count matrix-count-sm" :title="`의견/질문 ${qnaMap[row.id][w]}건`">{{ qnaMap[row.id][w] }}</span>
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

  <!-- 이슈/질문 상세 모달 -->
  <Teleport to="body">
    <div v-if="modal.visible" class="dash-modal-overlay" @click.self="modal.visible = false">
      <div class="dash-modal">
        <div class="dash-modal-header">
          <span>{{ modal.type === 'issue' ? '이슈 상세' : '질문 상세' }}</span>
          <button class="dash-modal-close" @click="modal.visible = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dash-modal-meta">
          <span class="badge badge-blue">{{ getTaskName(modal.item.task_id) }}</span>
          <span v-if="modal.item.assignee" class="badge badge-gray">{{ modal.item.assignee }}</span>
          <span v-if="modal.item.questioner" class="badge badge-purple">{{ modal.item.questioner }}</span>
          <template v-if="modal.item.targets && modal.item.targets.length">
            <span class="material-symbols-outlined" style="font-size:13px;color:var(--text-muted)">arrow_forward</span>
            <span v-for="t in modal.item.targets" :key="t" class="badge badge-blue">{{ t }}</span>
          </template>
          <span class="badge badge-gray">{{ formatWeekLabel(modal.item.week) }}</span>
        </div>
        <div class="dash-modal-body">
          <template v-if="modal.type === 'issue'">
            <TiptapPreview :modelValue="modal.item.issue" class="dash-modal-md" />
          </template>
          <template v-else>
            <div class="dash-modal-q">{{ modal.item.question }}</div>
            <template v-if="modal.item.answers && modal.item.answers.length > 0">
              <div class="dash-modal-a-label">답변</div>
              <TiptapPreview v-for="a in modal.item.answers" :key="a.id" :modelValue="a.answer" class="dash-modal-md" />
            </template>
            <div v-else class="dash-modal-no-answer">아직 답변이 없습니다.</div>
          </template>
        </div>
        <div class="dash-modal-footer">
          <button class="btn btn-ghost btn-sm" @click="modal.visible = false">닫기</button>
          <button class="btn btn-primary btn-sm" @click="navigateFromModal">진행현황에서 보기 →</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import axios from 'axios'
import TiptapPreview from '../components/TiptapPreview.vue'
import TiptapEditor from '../components/TiptapEditor.vue'
import { parseIds } from '../utils/parseIds.js'
import { getCurrentWeek, formatWeekLabel, normalizeWeek, addWeeks } from '../utils/week.js'
import { statusBadgeClass } from '../utils/status.js'

const router = useRouter()

const objectives = ref([])
const tasks      = ref([])
const staffList  = ref([])
const questions  = ref([])
const allQuestions     = ref([])
const allConfluenceLinks = ref([])
const weekIssuesList   = ref([])
const allIssuesList    = ref([])
const matrixOpen = ref(true)

const loading = ref(false)
const actionLoading = ref(false)
const activityOpen = ref(true)
const panelExpanded = reactive({ questions: false, issues: false })

// ── 공지 ──
const notice        = ref('')
const noticeEditing = ref(false)
const noticeDraft   = ref('')
const noticeSaving  = ref(false)
const isAdminMode   = ref(localStorage.getItem('adminMode') === 'true')

async function loadNotice() {
  const { data } = await axios.get('/api/settings/notice')
  notice.value = data.notice || ''
}
function startEditNotice() {
  noticeDraft.value = notice.value
  noticeEditing.value = true
}
function cancelEditNotice() {
  noticeEditing.value = false
  noticeDraft.value = ''
}
async function saveNotice() {
  noticeSaving.value = true
  try {
    const { data } = await axios.put('/api/settings/notice', { notice: noticeDraft.value })
    notice.value = data.notice
    noticeEditing.value = false
    noticeDraft.value = ''
  } finally {
    noticeSaving.value = false
  }
}
const questionFilter = ref('unanswered') // 'unanswered' | 'answered' | 'all'
const qWeekFilter    = ref('this')       // 'this' | 'last'
const issWeekFilter  = ref('this')       // 'this' | 'last'
const activityWeek   = ref('this')       // 'this' | 'last'

const today = new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

const currentWeek = getCurrentWeek()
const lastWeek    = addWeeks(currentWeek, -1)

// ── 목표 통계 ──
const inProgressCount = computed(() => objectives.value.filter(o => o.status === '진행중').length)
const completedCount  = computed(() => objectives.value.filter(o => o.status === '완료').length)
const dangerCount     = computed(() => objectives.value.filter(o => o.status === '위험').length)

// ── 액션 패널 데이터 ──
const unansweredQuestions = computed(() =>
  allQuestions.value.filter(q => !q.answers || q.answers.length === 0)
)

const filteredQuestions = computed(() => {
  const w = qWeekFilter.value === 'last' ? lastWeek : currentWeek
  const qs = allQuestions.value.filter(q => normalizeWeek(q.week) === w)
  if (questionFilter.value === 'answered') return qs.filter(q => q.answers && q.answers.length > 0)
  if (questionFilter.value === 'all') return qs
  return qs.filter(q => !q.answers || q.answers.length === 0)
})

const filteredIssues = computed(() => {
  const w = issWeekFilter.value === 'last' ? lastWeek : currentWeek
  return allIssuesList.value.filter(i => normalizeWeek(i.week) === w)
})

const weekIssues = computed(() => weekIssuesList.value)

// ── 팀원별 활동 통계 ──
const memberStatsMap = computed(() => {
  const w = activityWeek.value === 'last' ? lastWeek : currentWeek
  const wQuestions = allQuestions.value.filter(q => normalizeWeek(q.week) === w)
  const wIssues    = allIssuesList.value.filter(i => normalizeWeek(i.week) === w)
  const map = {}
  staffList.value.forEach(s => {
    map[s.name] = {
      tasks:     parseIds(s.selected_tasks || '').length,
      issues:    wIssues.filter(i => i.assignee === s.name).length,
      questions: wQuestions.filter(q => q.questioner === s.name).length,
      answers:   wQuestions.flatMap(q => q.answers || []).filter(a => a.answer_by === s.name).length,
    }
  })
  return map
})

const maxStats = computed(() => {
  const vals = Object.values(memberStatsMap.value)
  if (!vals.length) return { tasks: 1, issues: 1, questions: 1, answers: 1 }
  return {
    tasks:     Math.max(1, ...vals.map(v => v.tasks)),
    issues:    Math.max(1, ...vals.map(v => v.issues)),
    questions: Math.max(1, ...vals.map(v => v.questions)),
    answers:   Math.max(1, ...vals.map(v => v.answers)),
  }
})

function barWidth(val, max) {
  if (!val) return '0%'
  return `${Math.max(3, Math.round((val / max) * 100))}%`
}

const latestIssueMap = computed(() => {
  const map = {}
  staffList.value.forEach(s => {
    const items = allIssuesList.value
      .filter(i => i.assignee === s.name)
      .sort((a, b) => {
        const [ay, aw] = (a.week || '0-W0').split('-W').map(Number)
        const [by, bw] = (b.week || '0-W0').split('-W').map(Number)
        return ay !== by ? by - ay : bw - aw
      })
    map[s.name] = items[0] ? { week: items[0].week, issue: items[0].issue } : null
  })
  return map
})

// ── 매트릭스 공통 ──
const allWeeks = computed(() => {
  const s = new Set([currentWeek])
  allIssuesList.value.forEach(i => { if (i.week) s.add(normalizeWeek(i.week)) })
  allQuestions.value.forEach(q => { if (q.week) s.add(normalizeWeek(q.week)) })
  allConfluenceLinks.value.forEach(l => { if (l.week) s.add(normalizeWeek(l.week)) })
  return [...s].sort((a, b) => {
    const [ay, aw] = a.split('-W').map(Number)
    const [by, bw] = b.split('-W').map(Number)
    return ay !== by ? ay - by : aw - bw
  })
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
    m[l.task_id].add(normalizeWeek(l.week))
  })
  return m
})

const confluenceUrlMap = computed(() => {
  const m = {}
  allConfluenceLinks.value.forEach(l => {
    if (!l.task_id || !l.url) return
    if (!m[l.task_id]) m[l.task_id] = {}
    m[l.task_id][normalizeWeek(l.week)] = l.url
  })
  return m
})

const issueMap = computed(() => {
  const m = {}
  allIssuesList.value.forEach(iss => {
    if (!iss.task_id) return
    if (!m[iss.task_id]) m[iss.task_id] = new Set()
    m[iss.task_id].add(normalizeWeek(iss.week))
  })
  return m
})

const qnaMap = computed(() => {
  const m = {}
  allQuestions.value.forEach(q => {
    if (!q.task_id) return
    if (!m[q.task_id]) m[q.task_id] = {}
    const w = normalizeWeek(q.week)
    m[q.task_id][w] = (m[q.task_id][w] || 0) + 1
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
// ── 모달 ──
const modal = reactive({ visible: false, type: '', item: null })

function stripMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/`{1,3}[^`\n]*`{1,3}/g, '')
    .replace(/^[-*+]\s+/gm, '')
    .replace(/^>\s+/gm, '')
    .replace(/\[(.+?)\]\(.+?\)/g, '$1')
    .replace(/\n+/g, ' ')
    .trim()
}

function openModal(type, item) {
  modal.type = type
  modal.item = item
  modal.visible = true
}

function navigateFromModal() {
  const item = modal.item
  const type = modal.type
  modal.visible = false
  if (type === 'issue') goToIssue(item)
  else goToQuestion(item)
}

// ── 바로가기 네비게이션 ──
function goToQuestion(q) {
  router.push({ path: '/progress', query: { week: q.week, focusQuestion: q.id } })
}
function goToIssue(p) {
  router.push({ path: '/progress', query: { week: p.week, focusIssueId: p.id } })
}
function goToProgressTask(row) {
  router.push({ path: '/progress', query: { week: currentWeek, focusTask: row.id } })
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

    const [qRes, allQRes, clRes, issWeekRes, issAllRes] = await Promise.all([
      axios.get('/api/qna/questions', { params: { week: currentWeek } }),
      axios.get('/api/qna/questions'),
      axios.get('/api/confluence'),
      axios.get('/api/issues', { params: { week: currentWeek } }),
      axios.get('/api/issues'),
    ])
    questions.value          = qRes.data
    allQuestions.value       = allQRes.data
    allConfluenceLinks.value = clRes.data
    weekIssuesList.value     = issWeekRes.data
    allIssuesList.value      = issAllRes.data
  } finally {
    loading.value = false
    actionLoading.value = false
  }
}

onMounted(() => { refresh(); loadNotice() })
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

/* ── 파트 공지 ── */
.notice-card { border-left: 4px solid var(--primary); }
.notice-header { gap: 8px; }
.notice-empty { font-size: 13px; color: var(--text-muted); font-style: italic; }

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
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.issue-text {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

.q-targets-row {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 4px;
}
.q-targets-icon {
  font-size: 13px;
  color: #7c3aed;
  flex-shrink: 0;
}
.q-target-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f5f3ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
  font-size: 11px;
  font-weight: 600;
}

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
.stat-fill-purple { background: #7c3aed; }
.stat-num-q { color: #7c3aed; }
.stat-num-a { color: #059669; }

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

.panel-header-toggle {
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}
.panel-header-toggle:hover { background: var(--gray-50); }
.q-filter-group {
  display: flex;
  border: 1px solid var(--outline);
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}
.q-filter-btn {
  font-size: 11px;
  padding: 2px 8px;
  background: none;
  border: none;
  border-right: 1px solid var(--outline);
  cursor: pointer;
  color: var(--text-secondary);
  line-height: 1.6;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}
.q-filter-btn:last-child { border-right: none; }
.q-filter-btn:hover { background: var(--gray-50); color: var(--text-primary); }
.q-filter-btn.active { background: var(--primary-light); color: var(--primary); font-weight: 600; }
.panel-list-expanded {
  max-height: none !important;
  overflow-y: visible !important;
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
.matrix-icon-link-anchor { display: inline-flex; text-decoration: none; }
.matrix-icon-link-anchor:hover .matrix-icon { opacity: 0.75; }
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
.matrix-task-link {
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.matrix-task-link:hover {
  background: var(--primary-light);
  color: var(--primary);
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

/* ── 이슈/질문 상세 모달 ── */
.dash-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.dash-modal {
  background: #fff;
  border-radius: 12px;
  width: 580px;
  max-width: 92vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  animation: modal-in 0.15s ease;
}
@keyframes modal-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.dash-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--outline);
  font-weight: 600;
  font-size: 15px;
  flex-shrink: 0;
}
.dash-modal-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 4px;
}
.dash-modal-close:hover { color: var(--text-primary); background: var(--gray-50); }
.dash-modal-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
  padding: 10px 20px;
  border-bottom: 1px solid var(--outline);
  flex-shrink: 0;
}
.dash-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}
.dash-modal-md {
  background: transparent !important;
  padding: 0 !important;
}
.dash-modal-q {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.7;
  margin-bottom: 16px;
  white-space: pre-wrap;
  word-break: keep-all;
}
.dash-modal-a-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--outline);
}
.dash-modal-no-answer {
  font-size: 13px;
  color: var(--text-muted);
  font-style: italic;
}
.dash-modal-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--outline);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}
.badge-purple {
  background: #ede9fe;
  color: #6d28d9;
}
</style>

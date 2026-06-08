<template>
  <div class="page-wrap">
    <div class="ah-page-header">
      <h2 class="page-title-text">답변 현황 히스토리</h2>
      <p class="page-desc">답변 요구로 등록된 모든 댓글의 현황을 전체 기간에서 확인합니다.</p>
    </div>

    <!-- 필터 -->
    <div class="filter-bar">
      <div class="filter-row">
        <div class="filter-group">
          <span class="filter-label">주차</span>
          <select v-model="filterWeek" class="form-control filter-select">
            <option value="">전체</option>
            <option v-for="w in weeks" :key="w" :value="w">{{ weekLabel(w) }}</option>
          </select>
        </div>
        <div class="filter-divider"></div>
        <div class="filter-group">
          <span class="filter-label">과제</span>
          <select v-model="filterTask" class="form-control filter-select">
            <option value="">전체</option>
            <option v-for="t in taskOptions" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>
        <div class="filter-divider"></div>
        <div class="filter-group">
          <span class="filter-label">상태</span>
          <div class="filter-chip-group">
            <button class="filter-chip" :class="{ active: filterStatus === 'unanswered' }" @click="filterStatus = 'unanswered'">미답변</button>
            <button class="filter-chip" :class="{ active: filterStatus === 'answered' }" @click="filterStatus = 'answered'">답변완료</button>
            <button class="filter-chip" :class="{ active: filterStatus === 'all' }" @click="filterStatus = 'all'">전체</button>
          </div>
        </div>
        <div class="filter-divider"></div>
        <div class="filter-group">
          <span class="filter-label">유형</span>
          <div class="filter-chip-group">
            <button class="filter-chip" :class="{ active: filterType === 'all' }" @click="filterType = 'all'">전체</button>
            <button class="filter-chip" :class="{ active: filterType === 'task' }" @click="filterType = 'task'">과제댓글</button>
            <button class="filter-chip" :class="{ active: filterType === 'issue' }" @click="filterType = 'issue'">이슈댓글</button>
          </div>
        </div>
        <span class="filter-count">{{ filtered.length }}건</span>
      </div>
    </div>

    <!-- 목록 -->
    <div v-if="loading" class="empty-state">
      <div class="spinner" style="margin:0 auto"></div>
    </div>
    <div v-else-if="filtered.length === 0" class="empty-state">
      <span class="material-symbols-outlined empty-icon">chat_bubble_outline</span>
      <p>{{ filterStatus === 'answered' ? '답변 완료된 항목이 없습니다' : filterStatus === 'unanswered' ? '미답변 항목이 없습니다 👍' : '등록된 답변 현황이 없습니다' }}</p>
    </div>

    <div v-else class="answer-list">
      <div v-for="c in filtered" :key="c.id" class="answer-card" :class="c.is_answered ? 'card-answered' : 'card-pending'">

        <!-- 과제명 행 -->
        <div class="card-task-row">
          <span class="card-task-name">{{ getTaskName(c.task_id) }}</span>
          <div class="card-task-meta">
            <span class="badge badge-gray" style="font-size:11px">{{ weekLabel(c.week) }}</span>
            <span class="meta-date">{{ formatDate(c.created_at) }}</span>
          </div>
        </div>

        <!-- 댓글 메타 행 -->
        <div class="card-comment-meta">
          <div class="meta-left">
            <span class="type-badge" :class="c.type === 'issue' ? 'type-issue' : 'type-task'">
              {{ c.type === 'issue' ? '이슈댓글' : '과제댓글' }}
            </span>
            <span class="badge badge-gray" style="font-size:11px">{{ c.comment_by }}</span>
            <template v-if="c.tagged_users?.length">
              <span class="material-symbols-outlined" style="font-size:12px;color:var(--text-muted);flex-shrink:0">arrow_forward</span>
              <span v-for="t in c.tagged_users" :key="t" class="target-tag">{{ t }}</span>
            </template>
          </div>
          <div class="meta-status">
            <span v-if="c.is_answered" class="badge badge-green" style="font-size:11px">
              <span class="material-symbols-outlined" style="font-size:11px;vertical-align:-1px">check_circle</span>
              답변됨
            </span>
            <span v-else class="badge-pending-sm">
              <span class="material-symbols-outlined" style="font-size:11px;vertical-align:-1px">hourglass_empty</span>
              답변 대기
            </span>
          </div>
        </div>

        <!-- 댓글 본문 -->
        <div class="answer-body">
          <TiptapPreview :modelValue="c.comment" />
        </div>

        <!-- 액션 버튼 -->
        <div class="answer-actions">
          <button class="btn btn-primary btn-xs action-btn" @click="goToComment(c)">
            <span class="material-symbols-outlined">open_in_new</span>진행현황에서 보기
          </button>
          <button class="btn btn-ghost btn-xs action-btn" @click="goToHistory(c)">
            <span class="material-symbols-outlined">history</span>과제 이력
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import TiptapPreview from '../components/TiptapPreview.vue'

const router = useRouter()

const allComments  = ref([])
const tasks        = ref([])
const loading      = ref(false)
const filterWeek   = ref('')
const filterTask   = ref('')
const filterStatus = ref('unanswered')
const filterType   = ref('all')

const weeks = computed(() => {
  return [...new Set(allComments.value.map(c => c.week).filter(Boolean))].sort().reverse()
})

const taskOptions = computed(() => {
  const seen = new Set()
  const result = []
  for (const c of allComments.value) {
    const tid = resolveParentTaskId(c.task_id)
    if (seen.has(tid)) continue
    seen.add(tid)
    result.push({ id: tid, name: getTaskName(tid) })
  }
  return result.sort((a, b) => a.name.localeCompare(b.name, 'ko'))
})

const filtered = computed(() => {
  let cs = [...allComments.value]
  if (filterWeek.value) cs = cs.filter(c => c.week === filterWeek.value)
  if (filterTask.value) cs = cs.filter(c => resolveParentTaskId(c.task_id) === filterTask.value)
  if (filterStatus.value === 'answered')   cs = cs.filter(c => c.is_answered)
  if (filterStatus.value === 'unanswered') cs = cs.filter(c => !c.is_answered)
  if (filterType.value === 'task')  cs = cs.filter(c => c.type !== 'issue')
  if (filterType.value === 'issue') cs = cs.filter(c => c.type === 'issue')
  return cs.sort((a, b) => (b.created_at || '') > (a.created_at || '') ? 1 : -1)
})

function weekLabel(w) {
  if (!w) return ''
  const m = w.match(/(\d{4})-W(\d+)/)
  return m ? `${m[1].slice(2)}년 ${parseInt(m[2])}주차` : w
}

function formatDate(dt) {
  if (!dt) return ''
  return dt.slice(0, 16).replace('T', ' ')
}

function getTaskName(taskId) {
  const direct = tasks.value.find(t => t.id === taskId)
  if (direct) return direct.name
  for (const t of tasks.value) {
    const st = (t.sub_tasks || []).find(s => s.id === taskId)
    if (st) return `${t.name} › ${st.name || taskId}`
  }
  return taskId
}

function resolveParentTaskId(taskId) {
  if (tasks.value.find(t => t.id === taskId)) return taskId
  for (const t of tasks.value) {
    if ((t.sub_tasks || []).some(st => st.id === taskId)) return t.id
  }
  return taskId
}

function goToComment(c) {
  if (c.type === 'issue') {
    router.push({ path: '/progress', query: { week: c.week, focusIssueId: c.issue_id, commentId: c.id } })
  } else {
    router.push({ path: '/progress', query: { week: c.week, taskId: c.task_id, commentId: c.id } })
  }
}

function goToHistory(c) {
  router.push(`/tasks/${resolveParentTaskId(c.task_id)}/history`)
}

onMounted(async () => {
  loading.value = true
  try {
    const [tasksRes, tcRes, icRes] = await Promise.all([
      axios.get('/api/tasks'),
      axios.get('/api/task-comments'),
      axios.get('/api/issue-comments'),
    ])
    tasks.value = tasksRes.data || []
    const taskComments  = (tcRes.data || []).filter(c => c.requires_answer).map(c => ({ ...c, type: 'task' }))
    const issueComments = (icRes.data || []).filter(c => c.requires_answer).map(c => ({ ...c, type: 'issue' }))
    allComments.value = [...taskComments, ...issueComments]
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-wrap {
  max-width: none;
  padding: 28px 24px;
}
.ah-page-header { margin-bottom: 20px; }
.page-title-text {
  font-size: var(--fs-h2);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  margin: 0 0 4px;
}
.page-desc { font-size: var(--fs-sm); color: var(--text-muted); margin: 0; }

/* 필터 */
.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 16px;
  background: var(--gray-50);
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
}
.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  flex: 1;
}
.filter-select { width: auto; min-width: 130px; font-size: var(--fs-sm); }
.filter-group {
  display: flex;
  align-items: center;
  gap: 6px;
}
.filter-label {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  font-weight: var(--fw-semibold);
  flex-shrink: 0;
}
.filter-divider {
  width: 1px;
  height: 18px;
  background: var(--outline);
  flex-shrink: 0;
}
.filter-chip-group { display: flex; gap: 4px; }
.filter-chip {
  font-size: var(--fs-xs); padding: 4px 10px;
  border: 1px solid var(--outline); border-radius: 14px;
  background: var(--surface); color: var(--text-secondary);
  cursor: pointer; transition: all 0.15s;
}
.filter-chip.active { background: var(--primary); border-color: var(--primary); color: white; font-weight: var(--fw-semibold); }
.filter-count {
  font-size: var(--fs-sm); color: var(--text-muted);
  margin-left: auto; font-weight: var(--fw-medium);
  flex-shrink: 0;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 56px 0;
  color: var(--text-muted);
  font-size: var(--fs-sm);
}
.empty-icon {
  font-size: 40px;
  display: block;
  margin: 0 auto 10px;
  color: var(--gray-300);
}

/* 목록 */
.answer-list { display: flex; flex-direction: column; gap: 10px; }

.answer-card {
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  background: var(--surface);
  overflow: hidden;
  border-left-width: 3px;
}
.card-pending  { border-left-color: var(--warning); }
.card-answered { border-left-color: var(--success); opacity: 0.85; }

/* 과제명 행 */
.card-task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 14px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--outline);
  flex-wrap: wrap;
}
.card-task-name {
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-primary);
  flex: 1;
  min-width: 0;
}
.card-task-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* 댓글 메타 행 */
.card-comment-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 14px;
  border-bottom: 1px solid var(--outline);
  flex-wrap: wrap;
}
.meta-left {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}
.meta-status { flex-shrink: 0; }
.meta-date {
  font-size: var(--fs-2xs);
  color: var(--text-muted);
}

/* 타입 배지 */
.type-badge {
  font-size: 10px; font-weight: var(--fw-semibold);
  padding: 1px 7px; border-radius: 10px;
  flex-shrink: 0;
}
.type-task  { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.type-issue { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }

/* 태그 */
.target-tag {
  font-size: 11px; font-weight: var(--fw-semibold);
  padding: 1px 7px; border-radius: 10px;
  background: var(--primary-light); color: var(--primary);
  border: 1px solid var(--primary);
}

/* 상태 배지 */
.badge-pending-sm {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 99px;
  background: var(--warning-light);
  color: var(--warning);
  border: 1px solid var(--warning);
  font-weight: var(--fw-semibold);
}

/* 댓글 본문 */
.answer-body {
  padding: 12px 14px;
  font-size: var(--fs-sm);
  border-bottom: 1px solid var(--outline);
}

/* 액션 버튼 */
.answer-actions {
  display: flex;
  gap: 6px;
  padding: 8px 14px;
}
.action-btn {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: var(--fs-xs);
}
.action-btn .material-symbols-outlined { font-size: 14px; }
</style>

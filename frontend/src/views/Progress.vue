<template>
  <div>
    <div class="page-header">
      <div>
        <h2>주간 진행 현황</h2>
        <div class="subtitle">주차별 과제 진행 상황 및 Q&A</div>
      </div>
    </div>

    <div class="page-body">
      <!-- 주차 선택 + 인력 필터 -->
      <div class="filter-bar" style="flex-direction:column;align-items:flex-start;gap:10px">
        <div style="display:flex;align-items:center;gap:8px">
          <div class="week-nav" :class="{ 'week-nav-current': selectedWeek === `W${getCurrentWeekNumber()}` }">
            <button class="week-nav-btn" @click="prevWeek" :disabled="getCurrentWeekIndex() <= 0" data-tooltip="이전 주">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <div class="week-nav-info">
              <div style="display:flex;align-items:center;gap:6px">
                <span class="week-nav-label">{{ getWeekDateRange(selectedWeek) }}</span>
                <span v-if="selectedWeek === `W${getCurrentWeekNumber()}`" class="week-current-badge">이번 주</span>
              </div>
              <span class="week-nav-range">{{ selectedWeek }}</span>
            </div>
            <button class="week-nav-btn" @click="nextWeek" :disabled="getCurrentWeekIndex() >= availableWeeks.length - 1" data-tooltip="다음 주">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
          <button
            v-if="selectedWeek !== `W${getCurrentWeekNumber()}`"
            class="btn btn-ghost btn-sm week-today-btn"
            @click="goToCurrentWeek"
            data-tooltip="현재 주차로 이동"
          >이번 주</button>
        </div>
        <div v-if="staffList.length > 0" class="flex gap-6" style="align-items:center;flex-wrap:wrap">
          <span class="filter-label-sm">인력</span>
          <button
            v-for="s in staffList"
            :key="s.id"
            class="staff-chip"
            :class="{ 'staff-chip-active': selectedStaff.includes(s.name) }"
            @click="toggleStaff(s.name)"
          >{{ s.name }}</button>
          <button v-if="selectedStaff.length > 0" class="btn btn-ghost btn-xs" @click="selectedStaff = []" data-tooltip="인력 필터 초기화">전체 보기</button>
        </div>
      </div>

      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="!selectedWeek" class="empty-state">
        <span class="material-symbols-outlined empty-icon">calendar_today</span>
        <p>주차를 선택해주세요.</p>
      </div>

      <div v-else>
        <div v-for="task in filteredTasks" :key="task.id" :id="'task-' + task.id" class="card mb-16">
          <!-- 카드 헤더: 과제명 + Objective + 담당 인력 -->
          <div class="card-header" style="flex-wrap:wrap;gap:8px">
            <div class="flex gap-8" style="align-items:center;flex:1;min-width:0">
              <h3 style="margin:0">{{ task.name }}</h3>
              <span class="badge badge-blue">{{ task.objective_id }}: {{ getObjectiveName(task.objective_id) }}</span>
            </div>
            <div class="member-badges">
              <span
                v-for="m in getTaskMembers(task.id)"
                :key="m.id"
                class="badge badge-gray"
                :title="m.role"
              >{{ m.name }}</span>
              <span v-if="getTaskMembers(task.id).length === 0" class="text-muted text-sm">담당자 미배정</span>
            </div>
          </div>

          <div class="card-body">
            <!-- ① 컨플루언스 링크 -->
            <div class="section-block">
              <div class="section-label">
                <span class="material-symbols-outlined section-icon">link</span>
                컨플루언스
              </div>
              <div v-if="getTaskLink(task.id) && !editingLinkId[task.id]" class="flex gap-8" style="align-items:center">
                <a :href="getTaskLink(task.id).url" target="_blank" class="text-primary link-text">
                  {{ getTaskLink(task.id).url }}
                </a>
                <button class="btn btn-ghost btn-xs" @click="startEditLink(task.id)" data-tooltip="링크 수정">수정</button>
                <button class="btn btn-danger btn-xs" @click="deleteLink(task.id)" data-tooltip="링크 삭제">삭제</button>
              </div>
              <div v-else class="flex gap-8">
                <input
                  v-model="linkInputs[task.id]"
                  class="form-control"
                  placeholder="링크를 입력하세요"
                  style="flex:1"
                  @keyup.enter="saveLink(task.id)"
                />
                <button class="btn btn-primary btn-xs" @click="saveLink(task.id)" :disabled="!linkInputs[task.id]" data-tooltip="링크 저장">저장</button>
                <button v-if="getTaskLink(task.id)" class="btn btn-ghost btn-xs" @click="cancelEditLink(task.id)" data-tooltip="수정 취소">취소</button>
              </div>
            </div>

            <!-- ② 진행 내용 -->
            <ProgressSection
              :progress="progressMap[task.id] || null"
              :staff-list="staffList"
              :task-id="task.id"
              :week="selectedWeek"
              :objective-id="task.objective_id || ''"
              @update:progress="p => onProgressUpdate(task.id, p)"
            />

            <!-- ③ Q&A -->
            <QASection
              :questions="getQuestionsForTask(task.id)"
              :staff-list="staffList"
              :task-id="task.id"
              :week="selectedWeek"
              @update:questions="qs => onQuestionsUpdate(task.id, qs)"
            />
          </div>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useToast } from '../composables/useToast.js'
import { parseIds } from '../utils/parseIds.js'
import ProgressSection from '../components/progress/ProgressSection.vue'
import QASection from '../components/progress/QASection.vue'

const route = useRoute()

const tasks = ref([])
const objectives = ref([])
const staffList = ref([])
const loading = ref(false)
const { toastMsg, showToast } = useToast()

const selectedStaff = ref([])
const filteredTasks = computed(() => {
  if (selectedStaff.value.length === 0) return tasks.value
  return tasks.value.filter(task =>
    getTaskMembers(task.id).some(m => selectedStaff.value.includes(m.name))
  )
})
function toggleStaff(name) {
  const idx = selectedStaff.value.indexOf(name)
  if (idx === -1) selectedStaff.value.push(name)
  else selectedStaff.value.splice(idx, 1)
}

const selectedWeek = ref('')
const qnaList = ref([])
const linkMap = ref({})
const progressMap = ref({})
const linkInputs = ref({})
const editingLinkId = ref({})

// ── 주차 ──
const availableWeeks = computed(() => {
  const n = getCurrentWeekNumber()
  const weeks = []
  for (let i = Math.max(1, n - 4); i <= n + 4; i++) weeks.push(`W${i}`)
  return weeks
})

function getCurrentWeekNumber() {
  const today = new Date()
  const start = new Date(today.getFullYear(), 0, 1)
  return Math.ceil(((today - start) / 86400000 + start.getDay() + 1) / 7)
}

function getWeekDateRange(weekStr) {
  if (!weekStr) return ''
  const weekNum = parseInt(weekStr.replace('W', ''))
  const year = new Date().getFullYear()
  const jan1 = new Date(year, 0, 1)
  const startOffset = (weekNum - 1) * 7 - jan1.getDay()
  const start = new Date(year, 0, 1 + startOffset)
  const end = new Date(year, 0, 1 + startOffset + 6)
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}`
  return `${fmt(start)} – ${fmt(end)}`
}
function getCurrentWeekIndex() { return availableWeeks.value.indexOf(selectedWeek.value) }
function prevWeek() {
  const i = getCurrentWeekIndex()
  if (i > 0) { selectedWeek.value = availableWeeks.value[i - 1]; onWeekChange() }
}
function nextWeek() {
  const i = getCurrentWeekIndex()
  if (i < availableWeeks.value.length - 1) { selectedWeek.value = availableWeeks.value[i + 1]; onWeekChange() }
}
function goToCurrentWeek() {
  selectedWeek.value = `W${getCurrentWeekNumber()}`
  onWeekChange()
}
async function onWeekChange() {
  if (!selectedWeek.value) return
  linkInputs.value = Object.fromEntries(tasks.value.map(t => [t.id, '']))
  editingLinkId.value = {}
  await Promise.all([loadQnA(), loadLinks(), loadProgress()])
}

// ── 헬퍼 ──
function getObjectiveName(id) { return objectives.value.find(o => o.id === id)?.name ?? id }
function getTaskMembers(taskId) { return staffList.value.filter(s => parseIds(s.selected_tasks).includes(taskId)) }
function getQuestionsForTask(taskId) { return qnaList.value.filter(q => q.task_id === taskId) }
function getTaskLink(taskId) { return linkMap.value[taskId] || null }

// ── Q&A 업데이트 핸들러 ──
function onQuestionsUpdate(taskId, newQuestions) {
  const others = qnaList.value.filter(q => q.task_id !== taskId)
  qnaList.value = [...others, ...newQuestions]
}

// ── 진행 내용 업데이트 핸들러 ──
function onProgressUpdate(taskId, saved) {
  if (saved) {
    progressMap.value = { ...progressMap.value, [taskId]: saved }
  } else {
    const map = { ...progressMap.value }
    delete map[taskId]
    progressMap.value = map
  }
}

// ── 컨플루언스 링크 ──
async function loadLinks() {
  const { data } = await axios.get('/api/confluence', { params: { week: selectedWeek.value } })
  const map = {}
  data.forEach(l => { map[l.task_id] = l })
  linkMap.value = map
}
function startEditLink(taskId) {
  editingLinkId.value = { ...editingLinkId.value, [taskId]: true }
  linkInputs.value = { ...linkInputs.value, [taskId]: linkMap.value[taskId]?.url || '' }
}
function cancelEditLink(taskId) {
  const updated = { ...editingLinkId.value }; delete updated[taskId]; editingLinkId.value = updated
}
async function saveLink(taskId) {
  const url = linkInputs.value[taskId]?.trim()
  if (!url) return
  try {
    const existing = linkMap.value[taskId]
    const saved = existing
      ? (await axios.put(`/api/confluence/${existing.id}`, { url })).data
      : (await axios.post('/api/confluence', { week: selectedWeek.value, task_id: taskId, url })).data
    linkMap.value = { ...linkMap.value, [taskId]: saved }
    linkInputs.value[taskId] = ''
    cancelEditLink(taskId)
    showToast('링크가 저장되었습니다')
  } catch { showToast('링크 저장 실패') }
}
async function deleteLink(taskId) {
  if (!confirm('링크를 삭제하시겠습니까?')) return
  try {
    const existing = linkMap.value[taskId]
    if (existing) await axios.delete(`/api/confluence/${existing.id}`)
    const updated = { ...linkMap.value }; delete updated[taskId]; linkMap.value = updated
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}

// ── Q&A 로드 ──
async function loadQnA() {
  const { data } = await axios.get('/api/qna/questions', { params: { week: selectedWeek.value } })
  qnaList.value = data
}

// ── 진행 내용 로드 ──
async function loadProgress() {
  const { data } = await axios.get('/api/progress', { params: { week: selectedWeek.value } })
  const map = {}
  data.forEach(p => { map[p.task_id] = p })
  progressMap.value = map
}

// ── 포커스 이동 ──
async function handleFocusQuery() {
  const { focusQuestion, focusIssue } = route.query
  if (!focusQuestion && !focusIssue) return
  await nextTick()
  await new Promise(r => setTimeout(r, 80))
  const el = focusQuestion
    ? document.getElementById(`qa-${focusQuestion}`)
    : document.getElementById(`task-${focusIssue}`)
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  el.classList.add('highlight-focus')
  setTimeout(() => el?.classList.remove('highlight-focus'), 2200)
}

async function fetchAll() {
  loading.value = true
  try {
    const [tRes, oRes, sRes] = await Promise.all([axios.get('/api/tasks'), axios.get('/api/okrs'), axios.get('/api/staff')])
    tasks.value = tRes.data
    objectives.value = oRes.data
    staffList.value = sRes.data
    linkInputs.value = Object.fromEntries(tasks.value.map(t => [t.id, '']))
    selectedWeek.value = route.query.week || `W${getCurrentWeekNumber()}`
    await onWeekChange()
  } finally { loading.value = false }
  await handleFocusQuery()
}

onMounted(fetchAll)
</script>

<style scoped>
.mb-16 { margin-bottom: 16px; }
.gap-6 { gap: 6px; }

.filter-label-sm {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.week-nav {
  display: inline-flex;
  align-items: stretch;
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  overflow: hidden;
}
.week-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: background 0.15s, color 0.15s;
}
.week-nav-btn:hover:not(:disabled) { background: var(--gray-100); color: var(--text-primary); }
.week-nav-btn:disabled { opacity: 0.25; cursor: not-allowed; }
.week-nav-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 20px;
  border-left: 1px solid var(--outline);
  border-right: 1px solid var(--outline);
  min-width: 150px;
  gap: 2px;
}
.week-nav-label { font-size: 14px; font-weight: 700; color: var(--text-primary); letter-spacing: 0.01em; }
.week-nav-range { font-size: 11px; color: var(--text-muted); letter-spacing: 0.03em; }
.week-nav-current { border-color: var(--color-primary, #4f8ef7); box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary, #4f8ef7) 15%, transparent); }
.week-nav-current .week-nav-btn { color: var(--color-primary, #4f8ef7); }
.week-nav-current .week-nav-btn:hover:not(:disabled) { background: color-mix(in srgb, var(--color-primary, #4f8ef7) 8%, transparent); }
.week-nav-current .week-nav-info { border-color: var(--color-primary, #4f8ef7); }
.week-nav-current .week-nav-label { color: var(--color-primary, #4f8ef7); }
.week-current-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 999px;
  background: var(--color-primary, #4f8ef7);
  color: #fff;
  letter-spacing: 0.02em;
  line-height: 1.6;
}
.week-today-btn {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  color: var(--color-primary, #4f8ef7);
  border-color: var(--color-primary, #4f8ef7);
}

.staff-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--outline);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  background: var(--surface);
  color: var(--text-secondary);
  transition: all 0.15s;
}
.staff-chip:hover { border-color: var(--primary); color: var(--primary); }
.staff-chip-active { background: var(--primary-light); color: var(--primary); border-color: var(--primary); font-weight: 600; }

.member-badges { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }

.section-block {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--outline);
}
.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.section-icon {
  font-size: 14px;
  width: 14px;
  height: 14px;
  color: var(--text-muted);
}
.link-text { flex: 1; font-size: 14px; word-break: break-all; }
</style>

<style>
.md-preview-inline.md-editor-previewOnly { background: transparent !important; padding: 0 !important; }
.md-preview-inline .md-editor-preview-wrapper { padding: 4px 0 !important; }
.md-preview-inline .md-editor-preview { font-size: 14px; line-height: 1.6; color: var(--text-primary); }
.md-preview-inline .md-editor-preview > p:first-child { margin-top: 0; }
.md-preview-inline .md-editor-preview > p:last-child { margin-bottom: 0; }
.md-preview-inline .md-editor-preview img { max-width: 100%; border-radius: 4px; margin: 6px 0; display: block; }
</style>

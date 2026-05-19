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
          <div class="week-nav" :class="{ 'week-nav-current': selectedWeek === getCurrentWeek() }">
            <button class="week-nav-btn" @click="prevWeek" :disabled="getCurrentWeekIndex() <= 0" data-tooltip="이전 주">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <div class="week-nav-info">
              <div style="display:flex;align-items:center;gap:6px">
                <span class="week-nav-label">{{ getWeekDateRange(selectedWeek) }}</span>
                <span v-if="selectedWeek === getCurrentWeek()" class="week-current-badge">이번 주</span>
              </div>
              <span class="week-nav-range">{{ weekDisplayLabel }}</span>
            </div>
            <button class="week-nav-btn" @click="nextWeek" :disabled="getCurrentWeekIndex() >= availableWeeks.length - 1" data-tooltip="다음 주">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
          <button
            v-if="selectedWeek !== getCurrentWeek()"
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
              <span v-if="task.sub_tasks && task.sub_tasks.length > 0" class="badge badge-outline" style="font-size:11px">소과제 {{ task.sub_tasks.length }}개</span>
              <button
                v-if="task.sub_tasks && task.sub_tasks.length > 0"
                class="btn btn-ghost btn-xs subtask-toggle-all"
                @click="toggleAllSubTasks(task)"
                :data-tooltip="isAllSubTasksCollapsed(task) ? '소과제 전체 펼치기' : '소과제 전체 접기'"
              >
                <span class="material-symbols-outlined" style="font-size:13px;vertical-align:-2px">{{ isAllSubTasksCollapsed(task) ? 'unfold_more' : 'unfold_less' }}</span>
                {{ isAllSubTasksCollapsed(task) ? '전체 펼치기' : '전체 접기' }}
              </button>
            </div>
            <div class="member-badges">
              <template v-if="task.sub_tasks && task.sub_tasks.length > 0">
                <span
                  v-for="m in allTaskMembers(task)"
                  :key="m.id"
                  class="badge badge-gray"
                  :title="m.role"
                >{{ m.name }}</span>
                <span v-if="allTaskMembers(task).length === 0" class="text-muted text-sm">담당자 미배정</span>
              </template>
              <template v-else>
                <span
                  v-for="m in taskMembers(task.id)"
                  :key="m.id"
                  class="badge badge-gray"
                  :title="m.role"
                >{{ m.name }}</span>
                <span v-if="taskMembers(task.id).length === 0" class="text-muted text-sm">담당자 미배정</span>
              </template>
            </div>
          </div>

          <div class="card-body">
            <!-- 소과제가 있는 경우: 소과제별 섹션 (컨플루언스 포함) -->
            <template v-if="task.sub_tasks && task.sub_tasks.length > 0">
              <div
                v-for="st in task.sub_tasks"
                :key="st.id"
                class="sub-task-section"
                :class="{ 'sub-task-done': st.done }"
              >
                <div
                  class="sub-task-header"
                  :class="{ 'sub-task-header-collapsed': !expandedSubTaskIds.has(st.id) }"
                  @click="toggleSubTaskCollapse(st.id)"
                >
                  <div class="sub-task-title">
                    <span class="material-symbols-outlined sub-collapse-icon" :class="{ collapsed: !expandedSubTaskIds.has(st.id) }">expand_more</span>
                    <span class="sub-task-id-badge">{{ st.id }}</span>
                    <span class="sub-task-name">{{ st.name || '(이름 없음)' }}</span>
                    <template v-if="!expandedSubTaskIds.has(st.id)">
                      <span v-if="progressMap[st.id]?.issue?.trim()" class="subtask-sum-badge subtask-sum-issue">이슈 1건</span>
                      <span v-if="getQuestionsForTask(st.id).length > 0" class="subtask-sum-badge subtask-sum-qa">Q&A {{ getQuestionsForTask(st.id).length }}건</span>
                    </template>
                  </div>
                  <div class="sub-task-meta" @click.stop>
                    <div class="member-badges">
                      <span v-for="m in subTaskMembers(st.id)" :key="m.id" class="badge badge-gray" :title="m.role">{{ m.name }}</span>
                      <span v-if="subTaskMembers(st.id).length === 0" class="text-muted text-sm">담당자 미배정</span>
                    </div>
                    <button
                      class="btn btn-xs sub-task-done-btn"
                      :class="st.done ? 'btn-success' : 'btn-ghost'"
                      @click="toggleSubTaskDone(task.id, st.id, !st.done)"
                      :data-tooltip="st.done ? '완료됨 — 클릭하여 진행중으로 변경' : '진행중 — 클릭하여 완료 처리'"
                    >
                      <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">{{ st.done ? 'check_circle' : 'radio_button_unchecked' }}</span>
                      {{ st.done ? '완료' : '진행중' }}
                    </button>
                  </div>
                </div>

                <!-- 접힌 상태에서 링크 미리보기 -->
                <div
                  v-if="!expandedSubTaskIds.has(st.id) && getTaskLink(st.id)"
                  class="sub-task-link-row sub-task-link-collapsed-preview"
                  @click.stop
                >
                  <span class="material-symbols-outlined sub-task-link-icon">link</span>
                  <a :href="getTaskLink(st.id).url" target="_blank" class="text-primary sub-task-link-text">{{ getTaskLink(st.id).url }}</a>
                </div>

                <template v-if="expandedSubTaskIds.has(st.id)">
                  <!-- 소과제 컨플루언스 링크 -->
                  <div class="sub-task-link-row">
                    <button class="link-help-btn" :class="{ active: linkHelpOpen.has(st.id) }" @click="toggleLinkHelp(st.id)" data-tooltip="링크 가져오는 방법">?</button>
                    <span class="material-symbols-outlined sub-task-link-icon">link</span>
                    <template v-if="getTaskLink(st.id) && !editingLinkId[st.id]">
                      <a :href="getTaskLink(st.id).url" target="_blank" class="text-primary sub-task-link-text">{{ getTaskLink(st.id).url }}</a>
                      <button class="btn btn-ghost btn-xs" @click="startEditLink(st.id)" data-tooltip="링크 수정">수정</button>
                      <button class="btn btn-danger btn-xs" @click="deleteLink(st.id)" data-tooltip="링크 삭제">삭제</button>
                    </template>
                    <template v-else>
                      <input
                        v-model="linkInputs[st.id]"
                        class="form-control sub-task-link-input"
                        placeholder="컨플루언스 링크"
                        @keyup.enter="saveLink(st.id)"
                      />
                      <button class="btn btn-primary btn-xs" @click="saveLink(st.id)" :disabled="!linkInputs[st.id]" data-tooltip="링크 저장">저장</button>
                      <button v-if="getTaskLink(st.id)" class="btn btn-ghost btn-xs" @click="cancelEditLink(st.id)" data-tooltip="수정 취소">취소</button>
                    </template>
                  </div>
                  <div v-if="linkHelpOpen.has(st.id)" class="link-help-panel">
                    <div class="link-help-step"><span class="link-help-num">1</span><span>컨플루언스 페이지 우 상단 <strong>Share</strong> 버튼 클릭</span></div>
                    <div class="link-help-step"><span class="link-help-num">2</span><span>드롭다운에서 <strong>Share Link</strong> 생성 확인</span></div>
                    <div class="link-help-step"><span class="link-help-num">3</span><span><strong>Copy</strong> 버튼 클릭 → 아래 입력란에 붙여넣기</span></div>
                  </div>

                  <ProgressSection
                    :progress="progressMap[st.id] || null"
                    :staff-list="staffList"
                    :task-id="st.id"
                    :week="selectedWeek"
                    :objective-id="task.objective_id || ''"
                    @update:progress="p => onProgressUpdate(st.id, p)"
                  />

                  <QASection
                    :questions="getQuestionsForTask(st.id)"
                    :staff-list="staffList"
                    :task-id="st.id"
                    :week="selectedWeek"
                    @update:questions="qs => onQuestionsUpdate(st.id, qs)"
                  />
                </template>
              </div>
            </template>

            <!-- 소과제가 없는 경우: 기존 방식 -->
            <template v-else>
              <!-- ① 컨플루언스 링크 -->
              <div class="section-block">
                <div class="section-label">
                  <button class="link-help-btn" :class="{ active: linkHelpOpen.has(task.id) }" @click="toggleLinkHelp(task.id)" data-tooltip="링크 가져오는 방법">?</button>
                  <span class="material-symbols-outlined section-icon">link</span>
                  컨플루언스
                </div>
                <div v-if="linkHelpOpen.has(task.id)" class="link-help-panel">
                  <div class="link-help-step"><span class="link-help-num">1</span><span>컨플루언스 페이지 우 상단 <strong>Share</strong> 버튼 클릭</span></div>
                  <div class="link-help-step"><span class="link-help-num">2</span><span>드롭다운에서 <strong>Share Link</strong> 생성 확인</span></div>
                  <div class="link-help-step"><span class="link-help-num">3</span><span><strong>Copy</strong> 버튼 클릭 → 아래 입력란에 붙여넣기</span></div>
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
            </template>
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
import { getCurrentWeek, getWeekDateRange, addWeeks } from '../utils/week.js'
import { getTaskMembers, getAllTaskMembers } from '../utils/staff.js'
import ProgressSection from '../components/progress/ProgressSection.vue'
import QASection from '../components/progress/QASection.vue'

const route = useRoute()

const tasks = ref([])
const objectives = ref([])
const staffList = ref([])
const loading = ref(false)
const { toastMsg, showToast, toastError } = useToast()

const selectedStaff = ref([])
const filteredTasks = computed(() => {
  if (selectedStaff.value.length === 0) return tasks.value
  return tasks.value.filter(task =>
    getAllTaskMembers(task, staffList.value).some(m => selectedStaff.value.includes(m.name))
  )
})
function toggleStaff(name) {
  const idx = selectedStaff.value.indexOf(name)
  if (idx === -1) selectedStaff.value.push(name)
  else selectedStaff.value.splice(idx, 1)
}

const selectedWeek = ref('')
const weekDisplayLabel = computed(() => {
  const m = selectedWeek.value?.match(/^(\d{4})-W(\d+)$/)
  return m ? `${m[1]}년 W${parseInt(m[2])}` : selectedWeek.value
})
const qnaList = ref([])
const linkMap = ref({})
const progressMap = ref({})
const linkInputs = ref({})
const editingLinkId = ref({})
const linkHelpOpen = ref(new Set())
const expandedSubTaskIds = ref(new Set())

function toggleLinkHelp(id) {
  const next = new Set(linkHelpOpen.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  linkHelpOpen.value = next
}
function toggleSubTaskCollapse(stId) {
  const next = new Set(expandedSubTaskIds.value)
  if (next.has(stId)) next.delete(stId)
  else next.add(stId)
  expandedSubTaskIds.value = next
}
function isAllSubTasksCollapsed(task) {
  return (task.sub_tasks || []).every(st => !expandedSubTaskIds.value.has(st.id))
}
function toggleAllSubTasks(task) {
  const next = new Set(expandedSubTaskIds.value)
  if (isAllSubTasksCollapsed(task)) {
    task.sub_tasks.forEach(st => next.add(st.id))
  } else {
    task.sub_tasks.forEach(st => next.delete(st.id))
  }
  expandedSubTaskIds.value = next
}

// ── 주차 (연도 경계 자동 처리) ──
const availableWeeks = computed(() => {
  const center = selectedWeek.value || getCurrentWeek()
  return [-4, -3, -2, -1, 0, 1, 2, 3, 4].map(d => addWeeks(center, d))
})

function getCurrentWeekIndex() { return availableWeeks.value.indexOf(selectedWeek.value) }
function prevWeek() {
  selectedWeek.value = addWeeks(selectedWeek.value, -1)
  onWeekChange()
}
function nextWeek() {
  selectedWeek.value = addWeeks(selectedWeek.value, 1)
  onWeekChange()
}
function goToCurrentWeek() {
  selectedWeek.value = getCurrentWeek()
  onWeekChange()
}
function initLinkInputs() {
  const ids = []
  tasks.value.forEach(t => {
    ids.push(t.id)
    ;(t.sub_tasks || []).forEach(st => ids.push(st.id))
  })
  linkInputs.value = Object.fromEntries(ids.map(id => [id, '']))
}

async function onWeekChange() {
  if (!selectedWeek.value) return
  initLinkInputs()
  editingLinkId.value = {}
  await Promise.all([loadQnA(), loadLinks(), loadProgress()])
}

// ── 헬퍼 ──
function getObjectiveName(id) { return objectives.value.find(o => o.id === id)?.name ?? id }
function taskMembers(taskId) { return getTaskMembers(taskId, staffList.value) }
function subTaskMembers(subTaskId) { return getTaskMembers(subTaskId, staffList.value) }
function allTaskMembers(task) { return getAllTaskMembers(task, staffList.value) }
function getQuestionsForTask(taskId) { return qnaList.value.filter(q => q.task_id === taskId) }
function getTaskLink(taskId) { return linkMap.value[taskId] || null }

async function toggleSubTaskDone(taskId, subTaskId, done) {
  try {
    await axios.put(`/api/tasks/${taskId}/sub-tasks/${subTaskId}`, { done })
    tasks.value = tasks.value.map(t => {
      if (t.id !== taskId) return t
      return { ...t, sub_tasks: t.sub_tasks.map(st => st.id === subTaskId ? { ...st, done } : st) }
    })
    showToast(done ? '소과제가 완료 처리되었습니다' : '진행중으로 변경되었습니다')
  } catch (e) { toastError(e, '소과제 상태 변경 실패') }
}

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
  } catch (e) { toastError(e, '링크 저장 실패') }
}
async function deleteLink(taskId) {
  if (!confirm('링크를 삭제하시겠습니까?')) return
  try {
    const existing = linkMap.value[taskId]
    if (existing) await axios.delete(`/api/confluence/${existing.id}`)
    const updated = { ...linkMap.value }; delete updated[taskId]; linkMap.value = updated
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '링크 삭제 실패') }
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

  if (focusQuestion) {
    const q = qnaList.value.find(q => q.id === focusQuestion)
    if (q && q.task_id.includes('-')) {
      expandedSubTaskIds.value = new Set([...expandedSubTaskIds.value, q.task_id])
    }
  }

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
    initLinkInputs()
    selectedWeek.value = route.query.week || getCurrentWeek()
    await onWeekChange()
  } finally { loading.value = false }
  await handleFocusQuery()
}

onMounted(fetchAll)
</script>

<style scoped>
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
.link-text { flex: 1; font-size: 14px; word-break: break-all; }

.sub-task-section {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--outline);
  border-left: 3px solid var(--color-primary, #4f8ef7);
  border-radius: 8px;
  background: var(--gray-50, #fafafa);
  transition: opacity 0.2s;
}
.sub-task-section.sub-task-done {
  border-left-color: var(--color-success, #22c55e);
  opacity: 0.75;
}
.sub-task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  border-radius: 6px;
  margin: -4px -4px 12px;
  padding: 4px;
  transition: background 0.15s;
}
.sub-task-header:hover { background: color-mix(in srgb, var(--color-primary, #4f8ef7) 6%, transparent); }
.sub-task-header-collapsed { margin-bottom: 4px !important; }

.sub-task-link-collapsed-preview {
  margin-bottom: 0;
  background: transparent;
  border-color: transparent;
  padding: 3px 4px;
}
.sub-task-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.sub-task-id-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
  font-family: monospace;
  background: color-mix(in srgb, var(--color-primary, #4f8ef7) 12%, transparent);
  color: var(--color-primary, #4f8ef7);
  white-space: nowrap;
  flex-shrink: 0;
}
.sub-task-done .sub-task-id-badge {
  background: color-mix(in srgb, var(--color-success, #22c55e) 12%, transparent);
  color: var(--color-success, #22c55e);
}
.sub-task-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
}
.sub-task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.sub-task-done-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.sub-collapse-icon {
  font-size: 18px;
  color: var(--text-muted);
  flex-shrink: 0;
  transition: transform 0.2s;
}
.sub-collapse-icon.collapsed { transform: rotate(-90deg); }

.subtask-sum-badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  flex-shrink: 0;
}
.subtask-sum-issue {
  background: color-mix(in srgb, #f59e0b 12%, transparent);
  color: #b45309;
}
.subtask-sum-qa {
  background: color-mix(in srgb, var(--color-primary, #4f8ef7) 12%, transparent);
  color: var(--color-primary, #4f8ef7);
}

.subtask-toggle-all {
  font-size: 11px;
  padding: 2px 8px;
  color: var(--text-muted);
  border-color: var(--outline);
}

.link-help-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid var(--outline);
  background: var(--surface);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  line-height: 1;
  padding: 0;
}
.link-help-btn:hover,
.link-help-btn.active {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
}

.link-help-panel {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
  padding: 10px 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 12px;
  color: #1d4ed8;
}
.link-help-step {
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.5;
}
.link-help-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #2563eb;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}

.sub-task-link-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 7px 10px;
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: 6px;
}
.sub-task-link-icon {
  font-size: 15px;
  color: var(--text-muted);
  flex-shrink: 0;
}
.sub-task-link-text {
  flex: 1;
  font-size: 13px;
  word-break: break-all;
}
.sub-task-link-input {
  flex: 1;
  font-size: 13px;
  padding: 4px 8px;
  height: auto;
}
</style>

<style>
.md-preview-inline.md-editor-previewOnly { background: transparent !important; padding: 0 !important; }
.md-preview-inline .md-editor-preview-wrapper { padding: 4px 0 !important; }
.md-preview-inline .md-editor-preview { font-size: 14px; line-height: 1.6; color: var(--text-primary); }
.md-preview-inline .md-editor-preview > p:first-child { margin-top: 0; }
.md-preview-inline .md-editor-preview > p:last-child { margin-bottom: 0; }
.md-preview-inline .md-editor-preview img { max-width: 100%; border-radius: 4px; margin: 6px 0; display: block; }
</style>

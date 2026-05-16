<template>
  <div>
    <div class="page-header">
      <div>
        <h2>주간 진행 현황</h2>
        <div class="subtitle">주차별 과제 진행 상황 및 Q&A</div>
      </div>
    </div>

    <div class="page-body">
      <!-- 주차 선택 -->
      <div class="filter-bar">
        <div class="flex gap-8" style="align-items:center">
          <button class="btn btn-ghost btn-sm" @click="prevWeek" :disabled="getCurrentWeekIndex() <= 0">←</button>
          <select v-model="selectedWeek" class="form-control" @change="onWeekChange" style="min-width:120px">
            <option value="">주차 선택</option>
            <option v-for="w in availableWeeks" :key="w" :value="w">{{ w }}</option>
          </select>
          <button class="btn btn-ghost btn-sm" @click="nextWeek" :disabled="getCurrentWeekIndex() >= availableWeeks.length - 1">→</button>
        </div>
      </div>

      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="!selectedWeek" class="empty-state">
        <div class="empty-icon">📋</div><p>주차를 선택해주세요.</p>
      </div>

      <div v-else>
        <div v-for="task in tasks" :key="task.id" class="card mb-16">
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
              <div class="section-label">📎 컨플루언스</div>
              <div v-if="getTaskLink(task.id) && !editingLinkId[task.id]" class="flex gap-8" style="align-items:center">
                <a :href="getTaskLink(task.id).url" target="_blank" class="text-primary link-text">
                  {{ getTaskLink(task.id).url }}
                </a>
                <button class="btn btn-ghost btn-xs" @click="startEditLink(task.id)">수정</button>
                <button class="btn btn-danger btn-xs" @click="deleteLink(task.id)">삭제</button>
              </div>
              <div v-else class="flex gap-8">
                <input
                  v-model="linkInputs[task.id]"
                  class="form-control"
                  placeholder="링크를 입력하세요"
                  style="flex:1"
                  @keyup.enter="saveLink(task.id)"
                />
                <button class="btn btn-primary btn-xs" @click="saveLink(task.id)" :disabled="!linkInputs[task.id]">저장</button>
                <button v-if="getTaskLink(task.id)" class="btn btn-ghost btn-xs" @click="cancelEditLink(task.id)">취소</button>
              </div>
            </div>

            <!-- ② 진행 내용 & 이슈 -->
            <div class="section-block">
              <div class="section-label">📝 이번 주 진행 내용</div>

              <!-- 저장된 진행 내용 표시 -->
              <template v-if="getProgress(task.id) && !editingProgressId[task.id]">
                <div class="progress-view">
                  <div class="progress-meta">
                    <span class="badge badge-gray">{{ getProgress(task.id).assignee || '담당자 없음' }}</span>
                  </div>
                  <p class="progress-text">{{ getProgress(task.id).result }}</p>
                  <div v-if="getProgress(task.id).issue" class="issue-box">
                    <span class="issue-label">⚠ 이슈</span>
                    <p class="progress-text">{{ getProgress(task.id).issue }}</p>
                  </div>
                  <div class="flex gap-4 mt-8" style="justify-content:flex-end">
                    <button class="btn btn-ghost btn-xs" @click="startEditProgress(task.id)">수정</button>
                    <button class="btn btn-danger btn-xs" @click="deleteProgress(task.id)">삭제</button>
                  </div>
                </div>
              </template>

              <!-- 진행 내용 입력/수정 폼 -->
              <template v-else-if="editingProgressId[task.id] || addingProgressToTask === task.id">
                <div class="progress-form">
                  <div class="form-group">
                    <label class="form-label">담당자</label>
                    <select v-model="progressForm[task.id].assignee" class="form-control">
                      <option value="">선택</option>
                      <option v-for="m in getTaskMembers(task.id)" :key="m.id" :value="m.name">{{ m.name }}</option>
                      <option v-for="s in staffList" :key="s.id" :value="s.name"
                        v-if="!getTaskMembers(task.id).find(m => m.id === s.id)">{{ s.name }}</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">진행 내용</label>
                    <textarea v-model="progressForm[task.id].result" class="form-control" rows="3"
                      placeholder="이번 주 진행한 내용을 입력하세요..." />
                  </div>
                  <div class="form-group">
                    <label class="form-label">이슈 / 블로커 <span class="text-muted text-sm">(선택)</span></label>
                    <textarea v-model="progressForm[task.id].issue" class="form-control" rows="2"
                      placeholder="이슈나 블로커가 있으면 입력하세요..." />
                  </div>
                  <div class="flex gap-8" style="justify-content:flex-end">
                    <button class="btn btn-ghost btn-sm" @click="cancelProgress(task.id)">취소</button>
                    <button class="btn btn-primary btn-sm" @click="saveProgress(task.id)"
                      :disabled="!progressForm[task.id]?.result">저장</button>
                  </div>
                </div>
              </template>

              <!-- 진행 내용 없을 때 -->
              <template v-else>
                <button class="btn btn-ghost btn-sm" @click="startAddProgress(task.id)">+ 진행 내용 입력</button>
              </template>
            </div>

            <!-- ③ Q&A -->
            <div class="section-label">💬 Q&A</div>

            <div v-for="qa in getQuestionsForTask(task.id)" :key="qa.id" class="qa-block">
              <!-- 질문 -->
              <div class="question-row">
                <span class="badge badge-orange">Q</span>
                <div class="qa-content">
                  <template v-if="editingQuestionId === qa.id">
                    <textarea v-model="editingQuestionText" class="form-control" rows="2" />
                    <div class="flex gap-4 mt-8" style="justify-content:flex-end">
                      <button class="btn btn-ghost btn-xs" @click="cancelEditQuestion">취소</button>
                      <button class="btn btn-primary btn-xs" @click="updateQuestion(qa.id)" :disabled="!editingQuestionText">저장</button>
                    </div>
                  </template>
                  <span v-else class="qa-text">{{ qa.question }}</span>
                </div>
                <div v-if="editingQuestionId !== qa.id" class="qa-actions">
                  <button class="btn btn-ghost btn-xs" @click="startEditQuestion(qa)">수정</button>
                  <button class="btn btn-danger btn-xs" @click="deleteQuestion(qa.id)">삭제</button>
                </div>
              </div>

              <!-- 답변 -->
              <div class="answer-row">
                <span class="badge badge-green">A</span>
                <div class="qa-content">
                  <template v-if="qa.answer && editingAnswerId !== qa.answer.id">
                    <span class="qa-text">{{ qa.answer.answer }}</span>
                    <span class="answer-by">
                      — {{ qa.answer.answer_by }}
                      <span class="answer-date">{{ qa.answer.updated_at ?? qa.answer.created_at }}</span>
                      <span v-if="qa.answer.updated_at" class="answer-edited">(수정됨)</span>
                    </span>
                  </template>
                  <template v-else-if="editingAnswerId === qa.answer?.id">
                    <div style="flex:1">
                      <textarea v-model="editingAnswerText" class="form-control" rows="2" />
                      <select v-model="editingAnswerBy" class="form-control mt-8">
                        <option value="">작성자 선택</option>
                        <option v-for="s in staffList" :key="s.id" :value="s.name">{{ s.name }}</option>
                      </select>
                      <div class="flex gap-4 mt-8" style="justify-content:flex-end">
                        <button class="btn btn-ghost btn-xs" @click="cancelEditAnswer">취소</button>
                        <button class="btn btn-primary btn-xs" @click="updateAnswer(qa.answer.id)" :disabled="!editingAnswerText || !editingAnswerBy">저장</button>
                      </div>
                    </div>
                  </template>
                  <template v-else-if="addingAnswerToId === qa.id">
                    <div style="flex:1">
                      <textarea v-model="newAnswerText" class="form-control" rows="2" placeholder="답변을 입력하세요..." />
                      <select v-model="newAnswerBy" class="form-control mt-8">
                        <option value="">작성자 선택</option>
                        <option v-for="s in staffList" :key="s.id" :value="s.name">{{ s.name }}</option>
                      </select>
                      <div class="flex gap-4 mt-8" style="justify-content:flex-end">
                        <button class="btn btn-ghost btn-xs" @click="cancelAddAnswer">취소</button>
                        <button class="btn btn-primary btn-xs" @click="addAnswer(qa.id)" :disabled="!newAnswerText || !newAnswerBy">저장</button>
                      </div>
                    </div>
                  </template>
                  <span v-else class="text-muted text-sm">답변 대기중</span>
                </div>
                <div v-if="qa.answer && editingAnswerId !== qa.answer.id && addingAnswerToId !== qa.id" class="qa-actions">
                  <button class="btn btn-ghost btn-xs" @click="startEditAnswer(qa.answer)">수정</button>
                  <button class="btn btn-danger btn-xs" @click="deleteAnswer(qa.answer.id, qa.id)">삭제</button>
                </div>
                <div v-else-if="!qa.answer && addingAnswerToId !== qa.id" class="qa-actions">
                  <button class="btn btn-ghost btn-xs" @click="startAddAnswer(qa.id)">답변 달기</button>
                </div>
              </div>
            </div>

            <!-- 질문 추가 -->
            <div v-if="addingQuestionToTask === task.id" class="mt-16">
              <textarea v-model="newQuestionText" class="form-control" rows="3" placeholder="질문을 입력하세요..." />
              <div class="flex gap-8 mt-8" style="justify-content:flex-end">
                <button class="btn btn-ghost btn-sm" @click="cancelAddQuestion">취소</button>
                <button class="btn btn-primary btn-sm" @click="addQuestion(task.id)" :disabled="!newQuestionText">질문 추가</button>
              </div>
            </div>
            <div v-else class="mt-8">
              <button class="btn btn-ghost btn-sm" @click="startAddQuestion(task.id)">+ 질문 추가</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const tasks = ref([])
const objectives = ref([])
const staffList = ref([])
const loading = ref(false)
const toastMsg = ref('')

const selectedWeek = ref('')
const qnaList = ref([])
const linkMap = ref({})
const progressMap = ref({}) // task_id -> progress item

// 링크 편집 상태
const linkInputs = ref({})
const editingLinkId = ref({})

// 진행 내용 상태
const addingProgressToTask = ref('')
const editingProgressId = ref({}) // task_id -> boolean
const progressForm = ref({})      // task_id -> { assignee, result, issue }

// 질문 상태
const addingQuestionToTask = ref('')
const newQuestionText = ref('')
const editingQuestionId = ref('')
const editingQuestionText = ref('')

// 답변 상태
const addingAnswerToId = ref('')
const newAnswerText = ref('')
const newAnswerBy = ref('')
const editingAnswerId = ref('')
const editingAnswerText = ref('')
const editingAnswerBy = ref('')

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
function getCurrentWeekIndex() { return availableWeeks.value.indexOf(selectedWeek.value) }
function prevWeek() {
  const i = getCurrentWeekIndex()
  if (i > 0) { selectedWeek.value = availableWeeks.value[i - 1]; onWeekChange() }
}
function nextWeek() {
  const i = getCurrentWeekIndex()
  if (i < availableWeeks.value.length - 1) { selectedWeek.value = availableWeeks.value[i + 1]; onWeekChange() }
}
async function onWeekChange() {
  if (!selectedWeek.value) return
  await Promise.all([loadQnA(), loadLinks(), loadProgress()])
}

// ── 헬퍼 ──
function getObjectiveName(id) { return objectives.value.find(o => o.id === id)?.name ?? id }
function showToast(msg) { toastMsg.value = msg; setTimeout(() => { toastMsg.value = '' }, 2000) }

function getTaskMembers(taskId) {
  return staffList.value.filter(s => {
    const ids = (s.selected_tasks || '').split(',').map(t => t.trim()).filter(Boolean)
    return ids.includes(taskId)
  })
}

// ── 진행 내용 ──
function getProgress(taskId) { return progressMap.value[taskId] || null }

async function loadProgress() {
  const { data } = await axios.get('/api/progress', { params: { week: selectedWeek.value } })
  const map = {}
  data.forEach(p => { map[p.task_id] = p })
  progressMap.value = map
}

function startAddProgress(taskId) {
  addingProgressToTask.value = taskId
  progressForm.value[taskId] = { assignee: '', result: '', issue: '' }
}
function startEditProgress(taskId) {
  const p = progressMap.value[taskId]
  editingProgressId.value = { ...editingProgressId.value, [taskId]: true }
  progressForm.value[taskId] = { assignee: p.assignee || '', result: p.result || '', issue: p.issue || '' }
}
function cancelProgress(taskId) {
  addingProgressToTask.value = ''
  const ei = { ...editingProgressId.value }
  delete ei[taskId]
  editingProgressId.value = ei
}

async function saveProgress(taskId) {
  const form = progressForm.value[taskId]
  if (!form?.result?.trim()) return
  try {
    const existing = progressMap.value[taskId]
    const payload = { week: selectedWeek.value, task_id: taskId, objective: tasks.value.find(t => t.id === taskId)?.objective_id || '', ...form }
    let saved
    if (existing) {
      const { data } = await axios.put(`/api/progress/${existing.id}`, form)
      saved = data
    } else {
      const { data } = await axios.post('/api/progress', payload)
      saved = data
    }
    progressMap.value = { ...progressMap.value, [taskId]: saved }
    cancelProgress(taskId)
    showToast('저장되었습니다')
  } catch { showToast('저장 실패') }
}

async function deleteProgress(taskId) {
  if (!confirm('진행 내용을 삭제하시겠습니까?')) return
  try {
    const p = progressMap.value[taskId]
    await axios.delete(`/api/progress/${p.id}`)
    const map = { ...progressMap.value }
    delete map[taskId]
    progressMap.value = map
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}

// ── 컨플루언스 링크 ──
function getTaskLink(taskId) { return linkMap.value[taskId] || null }

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

// ── Q&A ──
function getQuestionsForTask(taskId) { return qnaList.value.filter(q => q.task_id === taskId) }

async function loadQnA() {
  const { data } = await axios.get('/api/qna/questions', { params: { week: selectedWeek.value } })
  qnaList.value = data
}
function startAddQuestion(taskId) { addingQuestionToTask.value = taskId; newQuestionText.value = '' }
function cancelAddQuestion() { addingQuestionToTask.value = ''; newQuestionText.value = '' }
async function addQuestion(taskId) {
  if (!newQuestionText.value.trim()) return
  try {
    const { data } = await axios.post('/api/qna/questions', { task_id: taskId, week: selectedWeek.value, question: newQuestionText.value.trim() })
    qnaList.value.push(data)
    cancelAddQuestion()
    showToast('질문이 추가되었습니다')
  } catch { showToast('질문 추가 실패') }
}
function startEditQuestion(qa) { editingQuestionId.value = qa.id; editingQuestionText.value = qa.question }
function cancelEditQuestion() { editingQuestionId.value = ''; editingQuestionText.value = '' }
async function updateQuestion(questionId) {
  if (!editingQuestionText.value.trim()) return
  try {
    const { data } = await axios.put(`/api/qna/questions/${questionId}`, { question: editingQuestionText.value.trim() })
    const idx = qnaList.value.findIndex(q => q.id === questionId)
    if (idx !== -1) qnaList.value[idx] = { ...qnaList.value[idx], question: data.question }
    cancelEditQuestion()
    showToast('수정되었습니다')
  } catch { showToast('수정 실패') }
}
async function deleteQuestion(questionId) {
  if (!confirm('질문을 삭제하시겠습니까? 답변도 함께 삭제됩니다.')) return
  try {
    await axios.delete(`/api/qna/questions/${questionId}`)
    qnaList.value = qnaList.value.filter(q => q.id !== questionId)
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}

// ── 답변 ──
function startAddAnswer(questionId) { addingAnswerToId.value = questionId; newAnswerText.value = ''; newAnswerBy.value = '' }
function cancelAddAnswer() { addingAnswerToId.value = ''; newAnswerText.value = ''; newAnswerBy.value = '' }
async function addAnswer(questionId) {
  if (!newAnswerText.value.trim() || !newAnswerBy.value) return
  try {
    const { data } = await axios.post('/api/qna/answers', { question_id: questionId, answer: newAnswerText.value.trim(), answer_by: newAnswerBy.value })
    const idx = qnaList.value.findIndex(q => q.id === questionId)
    if (idx !== -1) qnaList.value[idx] = { ...qnaList.value[idx], answer: data }
    cancelAddAnswer()
    showToast('답변이 저장되었습니다')
  } catch { showToast('답변 저장 실패') }
}
function startEditAnswer(answer) { editingAnswerId.value = answer.id; editingAnswerText.value = answer.answer; editingAnswerBy.value = answer.answer_by }
function cancelEditAnswer() { editingAnswerId.value = ''; editingAnswerText.value = ''; editingAnswerBy.value = '' }
async function updateAnswer(answerId) {
  if (!editingAnswerText.value.trim() || !editingAnswerBy.value) return
  try {
    const { data } = await axios.put(`/api/qna/answers/${answerId}`, { answer: editingAnswerText.value.trim(), answer_by: editingAnswerBy.value })
    const idx = qnaList.value.findIndex(q => q.answer?.id === answerId)
    if (idx !== -1) qnaList.value[idx] = { ...qnaList.value[idx], answer: data }
    cancelEditAnswer()
    showToast('수정되었습니다')
  } catch { showToast('수정 실패') }
}
async function deleteAnswer(answerId, questionId) {
  if (!confirm('답변을 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/qna/answers/${answerId}`)
    const idx = qnaList.value.findIndex(q => q.id === questionId)
    if (idx !== -1) qnaList.value[idx] = { ...qnaList.value[idx], answer: null }
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}

// ── 초기 로드 ──
async function fetchAll() {
  loading.value = true
  try {
    const [tRes, oRes, sRes] = await Promise.all([axios.get('/api/tasks'), axios.get('/api/okrs'), axios.get('/api/staff')])
    tasks.value = tRes.data
    objectives.value = oRes.data
    staffList.value = sRes.data
    selectedWeek.value = `W${getCurrentWeekNumber()}`
    await onWeekChange()
  } finally { loading.value = false }
}

onMounted(fetchAll)
</script>

<style scoped>
.mb-16 { margin-bottom: 16px; }
.mt-8  { margin-top: 8px; }
.mt-16 { margin-top: 16px; }

.member-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

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
}

.link-text {
  flex: 1;
  font-size: 14px;
  word-break: break-all;
}

/* 진행 내용 */
.progress-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.progress-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.progress-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.issue-box {
  background: #fff7ed;
  border-left: 3px solid #f59e0b;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
}
.issue-label {
  font-size: 12px;
  font-weight: 600;
  color: #b45309;
  display: block;
  margin-bottom: 4px;
}
.progress-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Q&A */
.qa-block {
  margin-bottom: 12px;
  padding: 12px;
  background: var(--gray-50);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.question-row,
.answer-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.qa-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.qa-text {
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
}
.qa-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.answer-by {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.answer-date { color: var(--text-muted); }
.answer-edited { font-size: 11px; opacity: 0.7; }
</style>

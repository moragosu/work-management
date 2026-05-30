<template>
  <div>
    <div class="section-label">
      <span class="material-symbols-outlined section-icon">forum</span>
      의견/질문
    </div>

    <div v-for="qa in questions" :key="qa.id" :id="'qa-' + qa.id" class="qa-block">
      <!-- 질문 -->
      <div class="question-row">
        <span class="badge badge-orange">Q</span>
        <div class="qa-content">
          <template v-if="editingQuestionId === qa.id">
            <!-- 대상자 수정 -->
            <div class="target-row">
              <span class="target-label">질문 대상</span>
              <div class="target-chips">
                <button
                  v-for="s in staffList" :key="s.id"
                  class="target-chip"
                  :class="{ active: editingTargets.includes(s.name) }"
                  @click="toggleTarget(editingTargets, s.name)"
                >{{ s.name }}</button>
                <template v-if="qaLeaders.length > 0">
                  <span class="target-group-sep">|</span>
                  <button
                    v-for="l in qaLeaders" :key="l.username"
                    class="target-chip target-chip-leader"
                    :class="{ active: editingTargets.includes(l.name) }"
                    @click="toggleTarget(editingTargets, l.name)"
                  >{{ l.name }}</button>
                </template>
              </div>
            </div>
            <TiptapEditor v-model="editingQuestionText" height="140px" @image-uploaded="url => editQuestionUploads.push(url)" />
            <div class="flex gap-4 mt-8" style="justify-content:flex-end">
              <button class="btn btn-ghost btn-xs" @click="cancelEditQuestion">취소</button>
              <button class="btn btn-primary btn-xs" @click="updateQuestion(qa.id)" :disabled="!hasContent(editingQuestionText)">저장</button>
            </div>
          </template>
          <template v-else>
            <!-- 질문자 / 대상자 표시 -->
            <div v-if="qa.questioner || (qa.targets && qa.targets.length > 0)" class="question-targets">
              <span v-if="qa.questioner" class="badge badge-purple" style="font-size:11px">{{ qa.questioner }}</span>
              <template v-if="qa.targets && qa.targets.length > 0">
                <span class="material-symbols-outlined" style="font-size:13px;color:var(--text-muted)">arrow_forward</span>
                <span v-for="t in qa.targets" :key="t"
                  class="badge" style="font-size:11px"
                  :class="isLeaderTarget(t) ? 'badge-purple' : 'badge-blue'"
                >{{ t }}</span>
              </template>
            </div>
            <TiptapPreview :modelValue="qa.question" />
          </template>
        </div>
        <div v-if="editingQuestionId !== qa.id" class="qa-actions">
          <button class="btn btn-ghost btn-xs" @click="copyLink('question', qa.id)" data-tooltip="링크 복사 — 메신저 공유용">
            <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">link</span>
          </button>
          <button v-if="!readonlyQuestion && auth.isLoggedIn && (qa.created_by === auth.user?.username || auth.isAdmin)" class="btn btn-ghost btn-xs" @click="startEditQuestion(qa)" data-tooltip="의견/질문 수정">수정</button>
          <button v-if="!readonlyQuestion && (qa.created_by === auth.user?.username || auth.isAdmin)" class="btn btn-danger btn-xs" @click="deleteQuestion(qa.id)" data-tooltip="의견/질문 및 모든 답변 삭제">삭제</button>
        </div>
      </div>

      <!-- 답변 없을 때 -->
      <div v-if="qa.answers.length === 0 && addingAnswerToId !== qa.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div class="qa-content">
          <span class="text-muted text-sm">답변 대기중</span>
        </div>
        <div class="qa-actions">
          <button v-if="!readonlyQuestion" class="btn btn-ghost btn-xs" @click="startAddAnswer(qa.id)" data-tooltip="이 질문에 답변 작성">답변 달기</button>
        </div>
      </div>

      <!-- 기존 답변들 -->
      <div v-for="ans in qa.answers" :key="ans.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div class="qa-content">
          <template v-if="editingAnswerId === ans.id">
            <div style="flex:1">
              <TiptapEditor v-model="editingAnswerText" height="160px" @image-uploaded="url => editAnswerUploads.push(url)" />
              <div class="flex gap-4 mt-8" style="justify-content:flex-end">
                <button class="btn btn-ghost btn-xs" @click="cancelEditAnswer">취소</button>
                <button class="btn btn-primary btn-xs" @click="updateAnswer(ans.id)" :disabled="!hasContent(editingAnswerText)">저장</button>
              </div>
            </div>
          </template>
          <template v-else>
            <TiptapPreview :modelValue="ans.answer" />
            <span class="answer-by">
              — {{ ans.answer_by }}
              <span class="answer-date">{{ ans.updated_at ?? ans.created_at }}</span>
              <span v-if="ans.updated_at" class="answer-edited">(수정됨)</span>
            </span>
          </template>
        </div>
        <div v-if="editingAnswerId !== ans.id" class="qa-actions">
          <button v-if="!readonlyQuestion" class="btn btn-ghost btn-xs" @click="startEditAnswer(ans)" data-tooltip="답변 수정">수정</button>
          <button v-if="!readonlyQuestion" class="btn btn-danger btn-xs" @click="deleteAnswer(ans.id, qa.id)" data-tooltip="답변 삭제">삭제</button>
        </div>
      </div>

      <!-- 답변 추가 폼 -->
      <div v-if="addingAnswerToId === qa.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div style="flex:1">
          <TiptapEditor v-model="newAnswerText" height="160px" @image-uploaded="url => addAnswerUploads.push(url)" />
          <div class="flex gap-4 mt-8" style="justify-content:flex-end">
            <button class="btn btn-ghost btn-xs" @click="cancelAddAnswer">취소</button>
            <button class="btn btn-primary btn-xs" @click="addAnswer(qa.id)" :disabled="!hasContent(newAnswerText)">저장</button>
          </div>
        </div>
      </div>

      <!-- 답변 추가 버튼 (기존 답변이 있을 때) -->
      <div v-if="qa.answers.length > 0 && addingAnswerToId !== qa.id && !readonlyQuestion" style="padding-left:8px;margin-top:4px">
        <button class="btn btn-ghost btn-xs" @click="startAddAnswer(qa.id)" data-tooltip="기존 답변에 추가로 답변 작성">+ 답변 추가</button>
      </div>
    </div>

    <!-- 질문 추가 -->
    <div v-if="addingQuestion && !readonlyQuestion" class="mt-16">
      <!-- 대상자 선택 -->
      <div class="target-row">
        <span class="target-label">질문 대상</span>
        <div class="target-chips">
          <button
            v-for="s in staffList" :key="s.id"
            class="target-chip"
            :class="{ active: newTargets.includes(s.name) }"
            @click="toggleTarget(newTargets, s.name)"
          >{{ s.name }}</button>
          <template v-if="qaLeaders.length > 0">
            <span class="target-group-sep">|</span>
            <button
              v-for="l in qaLeaders" :key="l.username"
              class="target-chip target-chip-leader"
              :class="{ active: newTargets.includes(l.name) }"
              @click="toggleTarget(newTargets, l.name)"
            >{{ l.name }}</button>
          </template>
        </div>
      </div>
      <TiptapEditor v-model="newQuestionText" height="160px" @image-uploaded="url => addQuestionUploads.push(url)" />
      <div class="flex gap-8 mt-8" style="justify-content:flex-end">
        <button class="btn btn-ghost btn-sm" @click="cancelAddQuestion">취소</button>
        <button class="btn btn-primary btn-sm" @click="addQuestion" :disabled="!hasContent(newQuestionText)">등록</button>
      </div>
    </div>
    <div v-else-if="!readonlyQuestion && auth.isLoggedIn" class="mt-8">
      <button class="btn btn-ghost btn-sm" @click="openAddQuestion" data-tooltip="이 과제에 의견/질문 등록">+ 의견/질문 추가</button>
    </div>

  </div>

  <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import TiptapPreview from '../TiptapPreview.vue'
import TiptapEditor from '../TiptapEditor.vue'
import { useToast } from '../../composables/useToast.js'
import { hasContent } from '../../utils/content.js'
import { useAuthStore } from '../../stores/auth.js'
import { copyToClipboard } from '../../utils/clipboard.js'
import { deleteOrphanedImages, deleteAllImages, deleteUrls } from '../../composables/useImageCleanup.js'

const props = defineProps({
  questions:       { type: Array,   default: () => [] },
  staffList:       { type: Array,   default: () => [] },
  qaLeaders:       { type: Array,   default: () => [] },
  taskId:          { type: String,  required: true },
  week:            { type: String,  required: true },
  readonlyQuestion:{ type: Boolean, default: false },
})
const emit = defineEmits(['update:questions'])
const { toastMsg, showToast, toastError } = useToast()
const auth = useAuthStore()

function isLeaderTarget(name) {
  return props.qaLeaders.some(l => l.name === name)
}

// ── 링크 복사 ──
async function copyLink(type, id) {
  const url = `${window.location.origin}/go/${id}`
  await copyToClipboard(url)
  showToast('링크가 복사되었습니다')
}

// ── 대상자 토글 ──
function toggleTarget(arr, name) {
  const idx = arr.indexOf(name)
  if (idx === -1) arr.push(name)
  else arr.splice(idx, 1)
}

// ── 질문 추가 ──
const addingQuestion = ref(false)
const newQuestionText = ref('')
const newTargets = ref([])
const addQuestionUploads = ref([])

function openAddQuestion() {
  addQuestionUploads.value = []
  addingQuestion.value = true
}

function resetAddQuestionForm() {
  addingQuestion.value = false; newQuestionText.value = ''; newTargets.value = []; addQuestionUploads.value = []
}
function cancelAddQuestion() {
  deleteUrls(addQuestionUploads.value)
  resetAddQuestionForm()
}

async function addQuestion() {
  if (!hasContent(newQuestionText.value)) return
  try {
    const { data } = await axios.post('/api/qna/questions', {
      task_id: props.taskId, week: props.week,
      question: newQuestionText.value.trim(),
      targets: [...newTargets.value],
      questioner: auth.user?.name || '',
    })
    await deleteUrls(addQuestionUploads.value.filter(u => !newQuestionText.value.includes(u)))
    emit('update:questions', [...props.questions, data])
    resetAddQuestionForm()
    showToast('의견/질문이 추가되었습니다')
  } catch (e) { toastError(e, '의견/질문 추가 실패') }
}

// ── 질문 수정 ──
const editingQuestionId = ref('')
const editingQuestionText = ref('')
const editingTargets = ref([])
const editQuestionUploads = ref([])

function startEditQuestion(qa) {
  editingQuestionId.value = qa.id
  editingQuestionText.value = qa.question
  editingTargets.value = [...(qa.targets || [])]
  editQuestionUploads.value = []
}
function resetEditQuestionForm() {
  editingQuestionId.value = ''; editingQuestionText.value = ''; editingTargets.value = []; editQuestionUploads.value = []
}
function cancelEditQuestion() {
  deleteUrls(editQuestionUploads.value)
  resetEditQuestionForm()
}

async function updateQuestion(questionId) {
  if (!hasContent(editingQuestionText.value)) return
  try {
    const oldQ = props.questions.find(q => q.id === questionId)
    const { data } = await axios.put(`/api/qna/questions/${questionId}`, {
      question: editingQuestionText.value.trim(),
      targets: [...editingTargets.value],
    })
    await deleteOrphanedImages(oldQ?.question, editingQuestionText.value)
    await deleteUrls(editQuestionUploads.value.filter(u => !editingQuestionText.value.includes(u)))
    emit('update:questions', props.questions.map(q => q.id === questionId ? { ...q, ...data } : q))
    resetEditQuestionForm()
    showToast('수정되었습니다')
  } catch (e) { toastError(e, '의견/질문 수정 실패') }
}

// ── 질문 삭제 ──
async function deleteQuestion(questionId) {
  if (!confirm('의견/질문과 모든 답변이 삭제됩니다. 계속하시겠습니까?')) return
  try {
    const target = props.questions.find(q => q.id === questionId)
    await axios.delete(`/api/qna/questions/${questionId}`)
    if (target) {
      const allTexts = [target.question, ...(target.answers || []).map(a => a.answer)]
      await deleteAllImages(...allTexts)
    }
    emit('update:questions', props.questions.filter(q => q.id !== questionId))
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '의견/질문 삭제 실패') }
}

// ── 답변 ──
const addingAnswerToId = ref('')
const newAnswerText = ref('')
const addAnswerUploads = ref([])
const editingAnswerId = ref('')
const editingAnswerText = ref('')
const editingAnswerBy = ref('')
const editAnswerUploads = ref([])

function startAddAnswer(questionId) { addingAnswerToId.value = questionId; newAnswerText.value = ''; addAnswerUploads.value = [] }
function resetAddAnswerForm() {
  addingAnswerToId.value = ''; newAnswerText.value = ''; addAnswerUploads.value = []
}
function cancelAddAnswer() {
  deleteUrls(addAnswerUploads.value)
  resetAddAnswerForm()
}
function startEditAnswer(answer) { editingAnswerId.value = answer.id; editingAnswerText.value = answer.answer; editingAnswerBy.value = answer.answer_by; editAnswerUploads.value = [] }
function resetEditAnswerForm() {
  editingAnswerId.value = ''; editingAnswerText.value = ''; editingAnswerBy.value = ''; editAnswerUploads.value = []
}
function cancelEditAnswer() {
  deleteUrls(editAnswerUploads.value)
  resetEditAnswerForm()
}

async function addAnswer(questionId) {
  if (!hasContent(newAnswerText.value)) return
  try {
    const { data } = await axios.post('/api/qna/answers', {
      question_id: questionId,
      answer: newAnswerText.value.trim(),
      answer_by: auth.user?.name || '',
    })
    await deleteUrls(addAnswerUploads.value.filter(u => !newAnswerText.value.includes(u)))
    emit('update:questions', props.questions.map(q =>
      q.id === questionId ? { ...q, answers: [...(q.answers || []), data] } : q
    ))
    resetAddAnswerForm()
    showToast('답변이 저장되었습니다')
  } catch (e) { toastError(e, '답변 저장 실패') }
}

async function updateAnswer(answerId) {
  if (!hasContent(editingAnswerText.value)) return
  try {
    const oldAnswer = props.questions.flatMap(q => q.answers || []).find(a => a.id === answerId)
    const { data } = await axios.put(`/api/qna/answers/${answerId}`, {
      answer: editingAnswerText.value.trim(),
      answer_by: editingAnswerBy.value,
    })
    await deleteOrphanedImages(oldAnswer?.answer, editingAnswerText.value)
    await deleteUrls(editAnswerUploads.value.filter(u => !editingAnswerText.value.includes(u)))
    emit('update:questions', props.questions.map(q => ({
      ...q,
      answers: q.answers?.map(a => a.id === answerId ? data : a) ?? [],
    })))
    resetEditAnswerForm()
    showToast('수정되었습니다')
  } catch (e) { toastError(e, '답변 수정 실패') }
}

async function deleteAnswer(answerId, questionId) {
  if (!confirm('답변을 삭제하시겠습니까?')) return
  try {
    const target = props.questions.flatMap(q => q.answers || []).find(a => a.id === answerId)
    await axios.delete(`/api/qna/answers/${answerId}`)
    await deleteAllImages(target?.answer)
    emit('update:questions', props.questions.map(q =>
      q.id === questionId ? { ...q, answers: q.answers.filter(a => a.id !== answerId) } : q
    ))
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '답변 삭제 실패') }
}
</script>

<style scoped>
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

/* 질문 대상자 */
.target-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.target-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}
.target-chips { display: flex; gap: 4px; flex-wrap: wrap; }
.target-chip {
  padding: 3px 10px;
  border-radius: 12px;
  border: 1px solid var(--outline);
  background: var(--surface);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.target-chip.active {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
  font-weight: 600;
}
.target-chip-leader {
  border-color: #8b5cf6;
  color: #8b5cf6;
}
.target-chip-leader.active {
  background: #f3effe;
  border-color: #8b5cf6;
  color: #8b5cf6;
  font-weight: 600;
}
.target-group-sep {
  color: var(--text-muted);
  font-size: 12px;
  align-self: center;
  padding: 0 2px;
}
.question-targets {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}
</style>

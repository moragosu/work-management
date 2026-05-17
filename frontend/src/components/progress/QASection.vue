<template>
  <div>
    <div class="section-label">💬 Q&A</div>

    <div v-for="qa in questions" :key="qa.id" :id="'qa-' + qa.id" class="qa-block">
      <!-- 질문 -->
      <div class="question-row">
        <span class="badge badge-orange">Q</span>
        <div class="qa-content">
          <template v-if="editingQuestionId === qa.id">
            <MarkdownEditor v-model="editingQuestionText" height="140px" />
            <div class="flex gap-4 mt-8" style="justify-content:flex-end">
              <button class="btn btn-ghost btn-xs" @click="cancelEditQuestion">취소</button>
              <button class="btn btn-primary btn-xs" @click="updateQuestion(qa.id)" :disabled="!hasContent(editingQuestionText)">저장</button>
            </div>
          </template>
          <MdPreview v-else language="en-US" :modelValue="qa.question" class="md-preview-inline" />
        </div>
        <div v-if="editingQuestionId !== qa.id" class="qa-actions">
          <button class="btn btn-ghost btn-xs" @click="startEditQuestion(qa)">수정</button>
          <button class="btn btn-danger btn-xs" @click="deleteQuestion(qa.id)">삭제</button>
        </div>
      </div>

      <!-- 답변 없을 때 -->
      <div v-if="qa.answers.length === 0 && addingAnswerToId !== qa.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div class="qa-content">
          <span class="text-muted text-sm">답변 대기중</span>
        </div>
        <div class="qa-actions">
          <button class="btn btn-ghost btn-xs" @click="startAddAnswer(qa.id)">답변 달기</button>
        </div>
      </div>

      <!-- 기존 답변들 -->
      <div v-for="ans in qa.answers" :key="ans.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div class="qa-content">
          <template v-if="editingAnswerId === ans.id">
            <div style="flex:1">
              <MarkdownEditor v-model="editingAnswerText" height="160px" />
              <select v-model="editingAnswerBy" class="form-control mt-8">
                <option value="">작성자 선택</option>
                <option v-for="s in staffList" :key="s.id" :value="s.name">{{ s.name }}</option>
              </select>
              <div class="flex gap-4 mt-8" style="justify-content:flex-end">
                <button class="btn btn-ghost btn-xs" @click="cancelEditAnswer">취소</button>
                <button class="btn btn-primary btn-xs" @click="updateAnswer(ans.id)" :disabled="!hasContent(editingAnswerText) || !editingAnswerBy">저장</button>
              </div>
            </div>
          </template>
          <template v-else>
            <MdPreview language="en-US" :modelValue="ans.answer" class="md-preview-inline" />
            <span class="answer-by">
              — {{ ans.answer_by }}
              <span class="answer-date">{{ ans.updated_at ?? ans.created_at }}</span>
              <span v-if="ans.updated_at" class="answer-edited">(수정됨)</span>
            </span>
          </template>
        </div>
        <div v-if="editingAnswerId !== ans.id" class="qa-actions">
          <button class="btn btn-ghost btn-xs" @click="startEditAnswer(ans)">수정</button>
          <button class="btn btn-danger btn-xs" @click="deleteAnswer(ans.id, qa.id)">삭제</button>
        </div>
      </div>

      <!-- 답변 추가 폼 -->
      <div v-if="addingAnswerToId === qa.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div style="flex:1">
          <MarkdownEditor v-model="newAnswerText" height="160px" />
          <select v-model="newAnswerBy" class="form-control mt-8">
            <option value="">작성자 선택</option>
            <option v-for="s in staffList" :key="s.id" :value="s.name">{{ s.name }}</option>
          </select>
          <div class="flex gap-4 mt-8" style="justify-content:flex-end">
            <button class="btn btn-ghost btn-xs" @click="cancelAddAnswer">취소</button>
            <button class="btn btn-primary btn-xs" @click="addAnswer(qa.id)" :disabled="!hasContent(newAnswerText) || !newAnswerBy">저장</button>
          </div>
        </div>
      </div>

      <!-- 답변 추가 버튼 (기존 답변이 있을 때) -->
      <div v-if="qa.answers.length > 0 && addingAnswerToId !== qa.id" style="padding-left:8px;margin-top:4px">
        <button class="btn btn-ghost btn-xs" @click="startAddAnswer(qa.id)">+ 답변 추가</button>
      </div>
    </div>

    <!-- 질문 추가 -->
    <div v-if="addingQuestion" class="mt-16">
      <MarkdownEditor v-model="newQuestionText" height="160px" />
      <div class="flex gap-8 mt-8" style="justify-content:flex-end">
        <button class="btn btn-ghost btn-sm" @click="cancelAddQuestion">취소</button>
        <button class="btn btn-primary btn-sm" @click="addQuestion" :disabled="!hasContent(newQuestionText)">질문 추가</button>
      </div>
    </div>
    <div v-else class="mt-8">
      <button class="btn btn-ghost btn-sm" @click="addingQuestion = true">+ 질문 추가</button>
    </div>

    <!-- 질문 삭제 비밀번호 모달 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>질문 삭제 확인</h3>
          <button class="modal-close" @click="closeDeleteModal">✕</button>
        </div>
        <div class="modal-body">
          <p class="text-sm text-muted" style="margin-bottom:12px">질문과 모든 답변이 삭제됩니다. 비밀번호를 입력하세요.</p>
          <input
            v-model="deletePassword"
            type="password"
            class="form-control"
            placeholder="비밀번호"
            @keyup.enter="confirmDelete"
            ref="deletePasswordInput"
          />
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost btn-sm" @click="closeDeleteModal">취소</button>
          <button class="btn btn-danger btn-sm" @click="confirmDelete">삭제</button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import { MdPreview } from 'md-editor-v3'
import MarkdownEditor from '../MarkdownEditor.vue'
import { useToast } from '../../composables/useToast.js'
import { ADMIN_PASSWORD } from '../../config.js'

const props = defineProps({
  questions: { type: Array, default: () => [] },
  staffList: { type: Array, default: () => [] },
  taskId: { type: String, required: true },
  week: { type: String, required: true },
})
const emit = defineEmits(['update:questions'])
const { toastMsg, showToast } = useToast()

function hasContent(text) { return !!(text && text.trim()) }

// ── 질문 ──
const addingQuestion = ref(false)
const newQuestionText = ref('')
const editingQuestionId = ref('')
const editingQuestionText = ref('')

function startEditQuestion(qa) { editingQuestionId.value = qa.id; editingQuestionText.value = qa.question }
function cancelEditQuestion() { editingQuestionId.value = ''; editingQuestionText.value = '' }
function cancelAddQuestion() { addingQuestion.value = false; newQuestionText.value = '' }

async function addQuestion() {
  if (!hasContent(newQuestionText.value)) return
  try {
    const { data } = await axios.post('/api/qna/questions', {
      task_id: props.taskId, week: props.week, question: newQuestionText.value.trim(),
    })
    emit('update:questions', [...props.questions, data])
    cancelAddQuestion()
    showToast('질문이 추가되었습니다')
  } catch { showToast('질문 추가 실패') }
}

async function updateQuestion(questionId) {
  if (!hasContent(editingQuestionText.value)) return
  try {
    const { data } = await axios.put(`/api/qna/questions/${questionId}`, { question: editingQuestionText.value.trim() })
    emit('update:questions', props.questions.map(q => q.id === questionId ? { ...q, question: data.question } : q))
    cancelEditQuestion()
    showToast('수정되었습니다')
  } catch { showToast('수정 실패') }
}

// ── 질문 삭제 (비밀번호 보호) ──
const showDeleteModal = ref(false)
const deletePassword = ref('')
const pendingDeleteId = ref(null)
const deletePasswordInput = ref(null)

function deleteQuestion(questionId) {
  pendingDeleteId.value = questionId
  deletePassword.value = ''
  showDeleteModal.value = true
  nextTick(() => deletePasswordInput.value?.focus())
}

function closeDeleteModal() {
  showDeleteModal.value = false
  deletePassword.value = ''
  pendingDeleteId.value = null
}

async function confirmDelete() {
  if (deletePassword.value !== ADMIN_PASSWORD) {
    showToast('비밀번호가 올바르지 않습니다')
    deletePassword.value = ''
    nextTick(() => deletePasswordInput.value?.focus())
    return
  }
  try {
    await axios.delete(`/api/qna/questions/${pendingDeleteId.value}`)
    emit('update:questions', props.questions.filter(q => q.id !== pendingDeleteId.value))
    showToast('삭제되었습니다')
    closeDeleteModal()
  } catch { showToast('삭제 실패') }
}

// ── 답변 ──
const addingAnswerToId = ref('')
const newAnswerText = ref('')
const newAnswerBy = ref('')
const editingAnswerId = ref('')
const editingAnswerText = ref('')
const editingAnswerBy = ref('')

function startAddAnswer(questionId) { addingAnswerToId.value = questionId; newAnswerText.value = ''; newAnswerBy.value = '' }
function cancelAddAnswer() { addingAnswerToId.value = ''; newAnswerText.value = ''; newAnswerBy.value = '' }
function startEditAnswer(answer) { editingAnswerId.value = answer.id; editingAnswerText.value = answer.answer; editingAnswerBy.value = answer.answer_by }
function cancelEditAnswer() { editingAnswerId.value = ''; editingAnswerText.value = ''; editingAnswerBy.value = '' }

async function addAnswer(questionId) {
  if (!hasContent(newAnswerText.value) || !newAnswerBy.value) return
  try {
    const { data } = await axios.post('/api/qna/answers', {
      question_id: questionId, answer: newAnswerText.value.trim(), answer_by: newAnswerBy.value,
    })
    emit('update:questions', props.questions.map(q =>
      q.id === questionId ? { ...q, answers: [...(q.answers || []), data] } : q
    ))
    cancelAddAnswer()
    showToast('답변이 저장되었습니다')
  } catch { showToast('답변 저장 실패') }
}

async function updateAnswer(answerId) {
  if (!hasContent(editingAnswerText.value) || !editingAnswerBy.value) return
  try {
    const { data } = await axios.put(`/api/qna/answers/${answerId}`, {
      answer: editingAnswerText.value.trim(), answer_by: editingAnswerBy.value,
    })
    emit('update:questions', props.questions.map(q => ({
      ...q,
      answers: q.answers?.map(a => a.id === answerId ? data : a) ?? [],
    })))
    cancelEditAnswer()
    showToast('수정되었습니다')
  } catch { showToast('수정 실패') }
}

async function deleteAnswer(answerId, questionId) {
  if (!confirm('답변을 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/qna/answers/${answerId}`)
    emit('update:questions', props.questions.map(q =>
      q.id === questionId ? { ...q, answers: q.answers.filter(a => a.id !== answerId) } : q
    ))
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}
</script>

<style scoped>
.mt-8  { margin-top: 8px; }
.mt-16 { margin-top: 16px; }

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

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
</style>

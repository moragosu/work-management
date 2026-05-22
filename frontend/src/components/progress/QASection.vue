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
            <!-- 질문자 수정 (필수) -->
            <div v-if="questioners.length > 0" class="target-row">
              <span class="target-label">질문자 <span style="color:var(--danger)">*</span></span>
              <select v-model="editingQuestioner" class="form-control" style="max-width:200px">
                <option v-for="q in questioners" :key="q" :value="q">{{ q }}</option>
              </select>
            </div>
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
              </div>
            </div>
            <MarkdownEditor v-model="editingQuestionText" height="140px" @image-uploaded="url => editQuestionUploads.push(url)" />
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
                <span v-for="t in qa.targets" :key="t" class="badge badge-blue" style="font-size:11px">{{ t }}</span>
              </template>
            </div>
            <MdPreview language="en-US" :modelValue="qa.question" class="md-preview-inline" :noImgZoomIn="true" />
          </template>
        </div>
        <div v-if="editingQuestionId !== qa.id" class="qa-actions">
          <button class="btn btn-ghost btn-xs" @click="copyLink('question', qa.id)" data-tooltip="링크 복사 — 메신저 공유용">
            <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">link</span>
          </button>
          <button class="btn btn-ghost btn-xs" @click="startEditQuestion(qa)" data-tooltip="의견/질문 수정">수정</button>
          <button class="btn btn-danger btn-xs" @click="deleteQuestion(qa.id)" data-tooltip="의견/질문 및 모든 답변 삭제">삭제</button>
        </div>
      </div>

      <!-- 답변 없을 때 -->
      <div v-if="qa.answers.length === 0 && addingAnswerToId !== qa.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div class="qa-content">
          <span class="text-muted text-sm">답변 대기중</span>
        </div>
        <div class="qa-actions">
          <button class="btn btn-ghost btn-xs" @click="startAddAnswer(qa.id)" data-tooltip="이 질문에 답변 작성">답변 달기</button>
        </div>
      </div>

      <!-- 기존 답변들 -->
      <div v-for="ans in qa.answers" :key="ans.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div class="qa-content">
          <template v-if="editingAnswerId === ans.id">
            <div style="flex:1">
              <MarkdownEditor v-model="editingAnswerText" height="160px" @image-uploaded="url => editAnswerUploads.push(url)" />
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
            <MdPreview language="en-US" :modelValue="ans.answer" class="md-preview-inline" :noImgZoomIn="true" />
            <span class="answer-by">
              — {{ ans.answer_by }}
              <span class="answer-date">{{ ans.updated_at ?? ans.created_at }}</span>
              <span v-if="ans.updated_at" class="answer-edited">(수정됨)</span>
            </span>
          </template>
        </div>
        <div v-if="editingAnswerId !== ans.id" class="qa-actions">
          <button class="btn btn-ghost btn-xs" @click="startEditAnswer(ans)" data-tooltip="답변 수정">수정</button>
          <button class="btn btn-danger btn-xs" @click="deleteAnswer(ans.id, qa.id)" data-tooltip="답변 삭제">삭제</button>
        </div>
      </div>

      <!-- 답변 추가 폼 -->
      <div v-if="addingAnswerToId === qa.id" class="answer-row">
        <span class="badge badge-green">A</span>
        <div style="flex:1">
          <MarkdownEditor v-model="newAnswerText" height="160px" @image-uploaded="url => addAnswerUploads.push(url)" />
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
        <button class="btn btn-ghost btn-xs" @click="startAddAnswer(qa.id)" data-tooltip="기존 답변에 추가로 답변 작성">+ 답변 추가</button>
      </div>
    </div>

    <!-- 질문 추가 -->
    <div v-if="addingQuestion" class="mt-16">
      <!-- 질문자 선택 (필수) -->
      <div v-if="questioners.length > 0" class="target-row">
        <span class="target-label">질문자 <span style="color:var(--danger)">*</span></span>
        <select v-model="newQuestioner" class="form-control" style="max-width:200px">
          <option v-for="q in questioners" :key="q" :value="q">{{ q }}</option>
        </select>
      </div>
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
        </div>
      </div>
      <MarkdownEditor v-model="newQuestionText" height="160px" @image-uploaded="url => addQuestionUploads.push(url)" />
      <div class="flex gap-8 mt-8" style="justify-content:flex-end">
        <button class="btn btn-ghost btn-sm" @click="cancelAddQuestion">취소</button>
        <button class="btn btn-primary btn-sm" @click="addQuestion" :disabled="!hasContent(newQuestionText) || (questioners.length > 0 && !newQuestioner)">등록</button>
      </div>
    </div>
    <div v-else class="mt-8">
      <button class="btn btn-ghost btn-sm" @click="openAddQuestion" data-tooltip="이 과제에 의견/질문 등록">+ 의견/질문 추가</button>
    </div>

  </div>

  <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>

  <!-- 비밀번호 확인 모달 -->
  <Teleport to="body">
    <div v-if="pwModal.open" class="pw-overlay" @click.self="closePwModal">
      <div class="pw-dialog">
        <div class="pw-title">관리자 암호 확인</div>
        <p class="pw-desc">의견/질문과 모든 답변이 삭제됩니다.<br>관리자 암호를 입력해주세요.</p>
        <input
          ref="pwInputRef"
          v-model="pwModal.value"
          type="password"
          class="pw-input"
          placeholder="암호 입력"
          @keyup.enter="confirmDelete"
          @keyup.esc="closePwModal"
        />
        <div v-if="pwModal.error" class="pw-error">{{ pwModal.error }}</div>
        <div class="pw-actions">
          <button class="btn btn-ghost btn-sm" @click="closePwModal">취소</button>
          <button class="btn btn-danger btn-sm" @click="confirmDelete" :disabled="!pwModal.value">삭제</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import { MdPreview } from 'md-editor-v3'
import MarkdownEditor from '../MarkdownEditor.vue'
import { useToast } from '../../composables/useToast.js'
import { hasContent } from '../../utils/content.js'
import { ADMIN_PASSWORD } from '../../config.js'
import { copyToClipboard } from '../../utils/clipboard.js'
import { deleteOrphanedImages, deleteAllImages, deleteUrls } from '../../composables/useImageCleanup.js'

const props = defineProps({
  questions:   { type: Array, default: () => [] },
  staffList:   { type: Array, default: () => [] },
  questioners: { type: Array, default: () => [] },
  taskId:      { type: String, required: true },
  week:        { type: String, required: true },
})
const emit = defineEmits(['update:questions'])
const { toastMsg, showToast, toastError } = useToast()

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
const newQuestioner = ref('')
const addQuestionUploads = ref([])

function openAddQuestion() {
  newQuestioner.value = props.questioners[0] || ''
  addQuestionUploads.value = []
  addingQuestion.value = true
}

function cancelAddQuestion() {
  deleteUrls(addQuestionUploads.value.filter(u => !newQuestionText.value.includes(u)))
  addingQuestion.value = false
  newQuestionText.value = ''
  newTargets.value = []
  newQuestioner.value = ''
  addQuestionUploads.value = []
}

async function addQuestion() {
  if (!hasContent(newQuestionText.value)) return
  try {
    const { data } = await axios.post('/api/qna/questions', {
      task_id: props.taskId, week: props.week,
      question: newQuestionText.value.trim(),
      targets: [...newTargets.value],
      questioner: newQuestioner.value || '',
    })
    await deleteUrls(addQuestionUploads.value.filter(u => !newQuestionText.value.includes(u)))
    emit('update:questions', [...props.questions, data])
    cancelAddQuestion()
    showToast('의견/질문이 추가되었습니다')
  } catch (e) { toastError(e, '의견/질문 추가 실패') }
}

// ── 질문 수정 ──
const editingQuestionId = ref('')
const editingQuestionText = ref('')
const editingTargets = ref([])
const editingQuestioner = ref('')
const editQuestionUploads = ref([])

function startEditQuestion(qa) {
  editingQuestionId.value = qa.id
  editingQuestionText.value = qa.question
  editingTargets.value = [...(qa.targets || [])]
  editingQuestioner.value = qa.questioner || props.questioners[0] || ''
  editQuestionUploads.value = []
}
function cancelEditQuestion() {
  deleteUrls(editQuestionUploads.value.filter(u => !editingQuestionText.value.includes(u)))
  editingQuestionId.value = ''
  editingQuestionText.value = ''
  editingTargets.value = []
  editingQuestioner.value = ''
  editQuestionUploads.value = []
}

async function updateQuestion(questionId) {
  if (!hasContent(editingQuestionText.value)) return
  try {
    const oldQ = props.questions.find(q => q.id === questionId)
    const { data } = await axios.put(`/api/qna/questions/${questionId}`, {
      question: editingQuestionText.value.trim(),
      targets: [...editingTargets.value],
      questioner: editingQuestioner.value || '',
    })
    await deleteOrphanedImages(oldQ?.question, editingQuestionText.value)
    await deleteUrls(editQuestionUploads.value.filter(u => !editingQuestionText.value.includes(u)))
    emit('update:questions', props.questions.map(q => q.id === questionId ? { ...q, ...data } : q))
    cancelEditQuestion()
    showToast('수정되었습니다')
  } catch (e) { toastError(e, '의견/질문 수정 실패') }
}

// ── 질문 삭제 (비밀번호 확인) ──
const pwInputRef = ref(null)
const pwModal = ref({ open: false, questionId: '', value: '', error: '' })

function deleteQuestion(questionId) {
  pwModal.value = { open: true, questionId, value: '', error: '' }
  nextTick(() => pwInputRef.value?.focus())
}

function closePwModal() {
  pwModal.value = { open: false, questionId: '', value: '', error: '' }
}

async function confirmDelete() {
  if (!pwModal.value.value) return
  if (pwModal.value.value !== ADMIN_PASSWORD) {
    pwModal.value.error = '암호가 올바르지 않습니다'
    pwModal.value.value = ''
    nextTick(() => pwInputRef.value?.focus())
    return
  }
  try {
    const target = props.questions.find(q => q.id === pwModal.value.questionId)
    await axios.delete(`/api/qna/questions/${pwModal.value.questionId}`, {
      headers: { 'X-Admin-Password': ADMIN_PASSWORD },
    })
    if (target) {
      const allTexts = [target.question, ...(target.answers || []).map(a => a.answer)]
      await deleteAllImages(...allTexts)
    }
    emit('update:questions', props.questions.filter(q => q.id !== pwModal.value.questionId))
    closePwModal()
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '의견/질문 삭제 실패') }
}

// ── 답변 ──
const addingAnswerToId = ref('')
const newAnswerText = ref('')
const newAnswerBy = ref('')
const addAnswerUploads = ref([])
const editingAnswerId = ref('')
const editingAnswerText = ref('')
const editingAnswerBy = ref('')
const editAnswerUploads = ref([])

function startAddAnswer(questionId) { addingAnswerToId.value = questionId; newAnswerText.value = ''; newAnswerBy.value = ''; addAnswerUploads.value = [] }
function cancelAddAnswer() {
  deleteUrls(addAnswerUploads.value.filter(u => !newAnswerText.value.includes(u)))
  addingAnswerToId.value = ''; newAnswerText.value = ''; newAnswerBy.value = ''; addAnswerUploads.value = []
}
function startEditAnswer(answer) { editingAnswerId.value = answer.id; editingAnswerText.value = answer.answer; editingAnswerBy.value = answer.answer_by; editAnswerUploads.value = [] }
function cancelEditAnswer() {
  deleteUrls(editAnswerUploads.value.filter(u => !editingAnswerText.value.includes(u)))
  editingAnswerId.value = ''; editingAnswerText.value = ''; editingAnswerBy.value = ''; editAnswerUploads.value = []
}

async function addAnswer(questionId) {
  if (!hasContent(newAnswerText.value) || !newAnswerBy.value) return
  try {
    const { data } = await axios.post('/api/qna/answers', {
      question_id: questionId, answer: newAnswerText.value.trim(), answer_by: newAnswerBy.value,
    })
    await deleteUrls(addAnswerUploads.value.filter(u => !newAnswerText.value.includes(u)))
    emit('update:questions', props.questions.map(q =>
      q.id === questionId ? { ...q, answers: [...(q.answers || []), data] } : q
    ))
    cancelAddAnswer()
    showToast('답변이 저장되었습니다')
  } catch (e) { toastError(e, '답변 저장 실패') }
}

async function updateAnswer(answerId) {
  if (!hasContent(editingAnswerText.value) || !editingAnswerBy.value) return
  try {
    const oldAnswer = props.questions.flatMap(q => q.answers || []).find(a => a.id === answerId)
    const { data } = await axios.put(`/api/qna/answers/${answerId}`, {
      answer: editingAnswerText.value.trim(), answer_by: editingAnswerBy.value,
    })
    await deleteOrphanedImages(oldAnswer?.answer, editingAnswerText.value)
    await deleteUrls(editAnswerUploads.value.filter(u => !editingAnswerText.value.includes(u)))
    emit('update:questions', props.questions.map(q => ({
      ...q,
      answers: q.answers?.map(a => a.id === answerId ? data : a) ?? [],
    })))
    cancelEditAnswer()
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
.question-targets {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}

/* 비밀번호 모달 */
.pw-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center; z-index: 9999;
}
.pw-dialog {
  background: var(--surface); border-radius: 10px; padding: 24px 28px;
  width: 320px; box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  display: flex; flex-direction: column; gap: 12px;
}
.pw-title { font-size: 15px; font-weight: 700; color: var(--text); }
.pw-desc { font-size: 13px; color: var(--text-muted); line-height: 1.6; margin: 0; }
.pw-input {
  width: 100%; padding: 8px 10px; border: 1px solid var(--outline);
  border-radius: 6px; font-size: 14px; background: var(--background);
  color: var(--text); outline: none; box-sizing: border-box;
}
.pw-input:focus { border-color: var(--primary); }
.pw-error { font-size: 12px; color: var(--danger); }
.pw-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }
</style>

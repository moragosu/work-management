<template>
  <div class="section-block">
    <div class="section-label">
      <span class="material-symbols-outlined section-icon">chat_bubble_outline</span>
      과제 댓글
    </div>

    <!-- 댓글 목록 -->
    <div v-for="c in comments" :key="c.id" class="comment-item">
      <div class="comment-meta-row">
        <span class="badge badge-gray">{{ c.comment_by }}</span>
        <template v-if="c.tagged_users && c.tagged_users.length">
          <span class="material-symbols-outlined comment-tag-arrow">arrow_forward</span>
          <span v-for="t in c.tagged_users" :key="t" class="badge comment-tag-badge">{{ t }}</span>
        </template>
        <span v-if="c.requires_answer && !c.is_answered" class="badge-pending">
          <span class="material-symbols-outlined" style="font-size:11px;vertical-align:-2px">hourglass_empty</span>
          답변 대기
        </span>
        <span v-if="c.requires_answer && c.is_answered" class="badge badge-green" style="font-size:11px">답변됨</span>
        <span class="meta-date">{{ (c.updated_at ?? c.created_at)?.slice(0, 19) }}</span>
        <span v-if="c.updated_at" class="meta-edited">수정됨</span>
        <div v-if="!readonly" class="comment-actions">
          <button class="btn btn-ghost btn-xs" @click="startReply(c.id)">↩ 답글</button>
          <button v-if="c.created_by === auth.user?.username || auth.isAdmin" class="btn btn-ghost btn-xs" @click="startEditComment(c)">수정</button>
          <button v-if="c.created_by === auth.user?.username || auth.isAdmin" class="btn btn-danger btn-xs" @click="deleteComment(c.id)">삭제</button>
        </div>
      </div>
      <!-- 수정 폼 -->
      <div v-if="editingCommentId === c.id">
        <div v-if="staffList.length > 0" class="comment-tag-row">
          <span class="comment-tag-label">@태그</span>
          <button
            v-for="s in staffList.filter(s => s.name !== auth.user?.name)"
            :key="s.id || s.name"
            class="target-chip"
            :class="{ active: editTagged.includes(s.name) }"
            @click="toggleEditTag(s.name)"
          >{{ s.name }}</button>
        </div>
        <TiptapEditor v-model="editCommentText" height="100px" />
        <div class="flex gap-4 mt-6" style="align-items:center;justify-content:flex-end">
          <label class="requires-answer-toggle">
            <input type="checkbox" v-model="editRequiresAnswer" />
            답변 요구
          </label>
          <button class="btn btn-ghost btn-xs" @click="cancelEditComment">취소</button>
          <button class="btn btn-primary btn-xs" @click="saveEditComment(c.id)" :disabled="!hasContent(editCommentText)">저장</button>
        </div>
      </div>
      <div v-else class="comment-body">
        <TiptapPreview :modelValue="c.comment" />
      </div>
      <!-- 대댓글 -->
      <div v-for="r in (c.replies || [])" :key="r.id" class="reply-item">
        <div class="reply-indent-line"></div>
        <div class="reply-body">
          <div class="comment-meta-row">
            <span class="badge badge-gray">{{ r.comment_by }}</span>
            <span class="meta-date">{{ (r.updated_at ?? r.created_at)?.slice(0, 19) }}</span>
            <span v-if="r.updated_at" class="meta-edited">수정됨</span>
            <div v-if="!readonly" class="comment-actions">
              <button v-if="r.created_by === auth.user?.username || auth.isAdmin" class="btn btn-ghost btn-xs" @click="startEditComment(r)">수정</button>
              <button v-if="r.created_by === auth.user?.username || auth.isAdmin" class="btn btn-danger btn-xs" @click="deleteComment(r.id)">삭제</button>
            </div>
          </div>
          <div v-if="editingCommentId === r.id">
            <TiptapEditor v-model="editCommentText" height="80px" />
            <div class="flex gap-4 mt-6" style="justify-content:flex-end">
              <button class="btn btn-ghost btn-xs" @click="cancelEditComment">취소</button>
              <button class="btn btn-primary btn-xs" @click="saveEditComment(r.id)" :disabled="!hasContent(editCommentText)">저장</button>
            </div>
          </div>
          <div v-else class="comment-body">
            <TiptapPreview :modelValue="r.comment" />
          </div>
        </div>
      </div>
      <!-- 대댓글 입력 폼 -->
      <div v-if="replyingToId === c.id" class="reply-editor-form">
        <div class="reply-indent-line"></div>
        <div style="flex:1">
          <TiptapEditor v-model="newCommentText" height="100px" placeholder="답글을 입력하세요..." />
          <div class="flex gap-4 mt-6" style="justify-content:flex-end">
            <button class="btn btn-ghost btn-xs" @click="cancelComment">취소</button>
            <button class="btn btn-primary btn-xs" @click="submitComment(c.id)" :disabled="!hasContent(newCommentText)">등록</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 댓글 입력 폼 -->
    <div v-if="!readonly">
      <div v-if="commenting && !replyingToId" class="comment-editor-form">
        <!-- @태그 chip -->
        <div v-if="staffList.length > 0" class="comment-tag-row">
          <span class="comment-tag-label">@태그</span>
          <button
            v-for="s in staffList.filter(s => s.name !== auth.user?.name)"
            :key="s.id || s.name"
            class="target-chip"
            :class="{ active: tagged.includes(s.name) }"
            @click="toggleTag(s.name)"
          >{{ s.name }}</button>
        </div>
        <TiptapEditor ref="editorRef" v-model="newCommentText" height="120px" placeholder="댓글을 입력하세요..." />
        <div class="flex gap-4 mt-6" style="align-items:center;justify-content:flex-end">
          <label class="requires-answer-toggle">
            <input type="checkbox" v-model="requiresAnswer" />
            답변 요구
          </label>
          <button class="btn btn-ghost btn-xs" @click="cancelComment">취소</button>
          <button class="btn btn-primary btn-xs" @click="submitComment(null)" :disabled="!hasContent(newCommentText)">등록</button>
        </div>
      </div>
      <button v-else-if="!commenting" class="btn-add-action mt-4" @click="startComment">
        <span class="material-symbols-outlined" style="font-size:13px;vertical-align:-2px">chat_bubble_outline</span>
        댓글
      </button>
    </div>

    <!-- 기존 Q&A 읽기 전용 -->
    <div v-if="legacyQA.length > 0" class="legacy-qa-section">
      <div class="legacy-qa-label">이전 의견/질문 (읽기 전용)</div>
      <div v-for="qa in legacyQA" :key="qa.id" class="legacy-qa-item">
        <div class="comment-meta-row">
          <span class="badge badge-purple" style="font-size:11px">Q</span>
          <span class="badge badge-gray">{{ qa.questioner }}</span>
          <span class="meta-date">{{ (qa.updated_at ?? qa.created_at)?.slice(0, 19) }}</span>
        </div>
        <div class="comment-body"><TiptapPreview :modelValue="qa.question" /></div>
        <div v-for="ans in (qa.answers || [])" :key="ans.id" class="reply-item" style="margin-top:6px">
          <div class="reply-indent-line"></div>
          <div class="reply-body">
            <div class="comment-meta-row">
              <span class="badge badge-green" style="font-size:11px">A</span>
              <span class="badge badge-gray">{{ ans.answer_by }}</span>
              <span class="meta-date">{{ (ans.updated_at ?? ans.created_at)?.slice(0, 19) }}</span>
            </div>
            <div class="comment-body"><TiptapPreview :modelValue="ans.answer" /></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import TiptapPreview from '../TiptapPreview.vue'
import TiptapEditor from '../TiptapEditor.vue'
import { useToast } from '../../composables/useToast.js'
import { hasContent } from '../../utils/content.js'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  taskId:   { type: String, required: true },
  week:     { type: String, required: true },
  staffList: { type: Array, default: () => [] },
  qaLeaders: { type: Array, default: () => [] },
  readonly: { type: Boolean, default: false },
})

const { toastMsg, showToast, toastError } = useToast()
const auth = useAuthStore()

const comments = ref([])
const legacyQA = ref([])

const commenting = ref(false)
const replyingToId = ref('')
const newCommentText = ref('')
const tagged = ref([])
const requiresAnswer = ref(false)
const editorRef = ref(null)
const editingCommentId = ref('')
const editCommentText = ref('')
const editTagged = ref([])
const editRequiresAnswer = ref(false)

onMounted(async () => {
  await Promise.all([loadComments(), loadLegacyQA()])
})

async function loadComments() {
  try {
    const { data } = await axios.get(`/api/tasks/${props.taskId}/comments`, { params: { week: props.week } })
    comments.value = data
  } catch (e) { /* 조용히 실패 */ }
}

async function loadLegacyQA() {
  try {
    const { data } = await axios.get('/api/qna/questions', { params: { task_id: props.taskId, week: props.week } })
    legacyQA.value = data
  } catch (e) { /* 조용히 실패 */ }
}

function startComment() {
  commenting.value = true
  newCommentText.value = ''
  tagged.value = []
  requiresAnswer.value = false
}

function startReply(commentId) {
  commenting.value = true
  replyingToId.value = commentId
  newCommentText.value = ''
  tagged.value = []
  requiresAnswer.value = false
}

function cancelComment() {
  commenting.value = false
  replyingToId.value = ''
  newCommentText.value = ''
  tagged.value = []
  requiresAnswer.value = false
}

function toggleTag(name) {
  const idx = tagged.value.indexOf(name)
  if (idx === -1) {
    tagged.value.push(name)
    editorRef.value?.insertText(` @${name} `)
  } else {
    tagged.value.splice(idx, 1)
  }
}

async function submitComment(parentId) {
  if (!hasContent(newCommentText.value)) return
  try {
    const { data } = await axios.post(`/api/tasks/${props.taskId}/comments`, {
      comment: newCommentText.value.trim(),
      comment_by: auth.user?.name || '',
      week: props.week,
      parent_id: parentId || null,
      requires_answer: requiresAnswer.value,
      tagged_users: [...tagged.value],
    })
    window.dispatchEvent(new Event('refresh-notifications'))
    if (parentId) {
      comments.value = comments.value.map(c =>
        c.id === parentId
          ? { ...c, replies: [...(c.replies || []), data], is_answered: c.requires_answer ? 1 : c.is_answered }
          : c
      )
    } else {
      comments.value = [...comments.value, { ...data, replies: [] }]
    }
    cancelComment()
  } catch (e) { toastError(e, '댓글 등록 실패') }
}

function startEditComment(c) {
  editingCommentId.value = c.id
  editCommentText.value = c.comment
  editTagged.value = [...(c.tagged_users || [])]
  editRequiresAnswer.value = !!c.requires_answer
}

function cancelEditComment() {
  editingCommentId.value = ''
  editCommentText.value = ''
  editTagged.value = []
  editRequiresAnswer.value = false
}

function toggleEditTag(name) {
  const idx = editTagged.value.indexOf(name)
  if (idx === -1) editTagged.value.push(name)
  else editTagged.value.splice(idx, 1)
}

async function saveEditComment(commentId) {
  if (!hasContent(editCommentText.value)) return
  try {
    const { data } = await axios.put(`/api/tasks/${props.taskId}/comments/${commentId}`, {
      comment: editCommentText.value.trim(),
      tagged_users: [...editTagged.value],
      requires_answer: editRequiresAnswer.value,
    })
    comments.value = comments.value.map(c =>
      c.id === commentId
        ? { ...c, ...data }
        : { ...c, replies: (c.replies || []).map(r => r.id === commentId ? { ...r, ...data } : r) }
    )
    cancelEditComment()
    showToast('수정되었습니다')
  } catch (e) { toastError(e, '수정 실패') }
}

async function deleteComment(commentId) {
  if (!confirm('삭제하시겠습니까?')) return
  try {
    const { data } = await axios.delete(`/api/tasks/${props.taskId}/comments/${commentId}`)
    comments.value = comments.value
      .filter(c => c.id !== commentId)
      .map(c => {
        const filtered = (c.replies || []).filter(r => r.id !== commentId)
        // 답글 삭제로 부모가 미답변 복원된 경우
        const unanswered = data.parent_unanswered === c.id
        return { ...c, replies: filtered, is_answered: unanswered ? 0 : c.is_answered }
      })
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '삭제 실패') }
}
</script>

<style scoped>
.section-block {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--outline);
}
.comment-item {
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  margin-bottom: 6px;
}
.comment-item:last-child { margin-bottom: 0; }
.comment-meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: var(--fs-xs);
}
.comment-actions { display: flex; gap: 2px; flex-shrink: 0; margin-left: auto; }
.comment-body { font-size: var(--fs-sm); }
.reply-item {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.reply-indent-line {
  width: 2px;
  flex-shrink: 0;
  background: var(--outline);
  border-radius: 1px;
  align-self: stretch;
  min-height: 20px;
}
.reply-body {
  flex: 1;
  min-width: 0;
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
}
.reply-editor-form {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.comment-editor-form { margin-top: 8px; }
.comment-tag-row {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.comment-tag-label {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  font-weight: var(--fw-semibold);
  flex-shrink: 0;
}
.target-chip {
  font-size: var(--fs-xs);
  padding: 2px 8px;
  border-radius: 99px;
  border: 1px solid var(--outline);
  background: var(--bg-main);
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.1s, color 0.1s, border-color 0.1s;
}
.target-chip:hover { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }
.target-chip.active { background: var(--primary); border-color: var(--primary); color: #fff; }
.requires-answer-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--fs-xs);
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}
.comment-tag-arrow {
  font-size: 12px;
  color: var(--text-muted);
  vertical-align: middle;
}
.comment-tag-badge {
  font-size: 11px;
  padding: 1px 6px;
  background: var(--primary-light);
  color: var(--primary);
  border: 1px solid var(--primary);
  border-radius: 99px;
}
.badge-pending {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 99px;
  background: var(--warning-light);
  color: var(--warning);
  border: 1px solid var(--warning);
  font-weight: var(--fw-semibold);
}
.mt-4 { margin-top: 4px; }

/* 기존 Q&A 읽기 전용 */
.legacy-qa-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed var(--outline);
}
.legacy-qa-label {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  font-weight: var(--fw-semibold);
  margin-bottom: 8px;
}
.legacy-qa-item {
  background: var(--gray-50, #f9fafb);
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  margin-bottom: 6px;
  opacity: 0.85;
}
</style>

<template>
  <div class="section-block">
    <div class="section-label">
      <span class="material-symbols-outlined section-icon">warning</span>
      진행 현황 및 이슈
    </div>

    <!-- 등록된 이슈 목록 -->
    <div v-for="iss in issues" :key="iss.id" class="issue-item">
      <template v-if="editingId === iss.id">
        <div class="form-group">
          <label class="form-label">등록자</label>
          <select v-model="editAssignee" class="form-control">
            <option value="">선택</option>
            <option v-for="s in staffList" :key="s.username" :value="s.name">{{ s.name }}</option>
          </select>
        </div>
        <TiptapEditor v-model="editText" height="140px" @image-uploaded="url => editUploads.push(url)" />
        <div class="flex gap-8 mt-8" style="justify-content:flex-end">
          <button class="btn btn-ghost btn-sm" @click="cancelEdit">취소</button>
          <button class="btn btn-primary btn-sm" @click="saveEdit(iss.id)" :disabled="!hasContent(editText) || !editAssignee">저장</button>
        </div>
      </template>
      <template v-else>
        <div :id="'issue-' + iss.id" class="issue-box">
          <TiptapPreview :modelValue="iss.issue" />
        </div>
        <div class="flex gap-4 mt-8" style="align-items:center">
          <span v-if="iss.assignee" class="badge badge-gray">{{ iss.assignee }}</span>
          <span class="meta-date">{{ (iss.updated_at ?? iss.created_at)?.slice(0, 19) }}</span>
          <span v-if="iss.updated_at" class="meta-edited">수정됨</span>
          <div style="margin-left:auto;display:flex;gap:4px">
            <button class="btn btn-ghost btn-xs" @click="copyLink(iss)" data-tooltip="링크 복사 — 메신저 공유용">
              <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">link</span>
            </button>
            <button v-if="!readonly" class="btn btn-ghost btn-xs" @click="startEdit(iss)" data-tooltip="이슈 수정">수정</button>
            <button v-if="!readonly" class="btn btn-danger btn-xs" @click="deleteIssue(iss.id)" data-tooltip="이슈 삭제">삭제</button>
          </div>
        </div>

        <!-- 댓글 영역 -->
        <div class="comment-section">
          <div v-if="(iss.comments || []).length > 0" class="comment-section-label">
            <span class="material-symbols-outlined">chat_bubble_outline</span>
            댓글 {{ (iss.comments || []).length }}개
          </div>
          <div v-for="c in (iss.comments || [])" :key="c.id" :id="`comment-${c.id}`" class="comment-item">
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
                <button class="btn btn-ghost btn-xs" @click="startReplyToComment(iss.id, c.id)">↩ 답글</button>
                <button v-if="c.created_by === auth.user?.username || auth.isAdmin" class="btn btn-ghost btn-xs" @click="startEditComment(iss.id, c)">수정</button>
                <button v-if="c.created_by === auth.user?.username || auth.isAdmin" class="btn btn-danger btn-xs" @click="deleteComment(iss.id, c.id)">삭제</button>
              </div>
            </div>
            <div class="comment-body">
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
                    <button v-if="r.created_by === auth.user?.username || auth.isAdmin" class="btn btn-ghost btn-xs" @click="startEditComment(iss.id, r)">수정</button>
                    <button v-if="r.created_by === auth.user?.username || auth.isAdmin" class="btn btn-danger btn-xs" @click="deleteComment(iss.id, r.id)">삭제</button>
                  </div>
                </div>
                <div class="comment-body">
                  <TiptapPreview :modelValue="r.comment" />
                </div>
              </div>
            </div>
            <!-- 대댓글 입력 폼 -->
            <div v-if="replyingToCommentId === c.id" class="reply-editor-form">
              <div class="reply-indent-line"></div>
              <div style="flex:1">
                <TiptapEditor v-model="newCommentText" height="100px" placeholder="답글을 입력하세요..." />
                <div class="flex gap-4 mt-6" style="justify-content:flex-end">
                  <button class="btn btn-ghost btn-xs" @click="cancelComment">취소</button>
                  <button class="btn btn-primary btn-xs" @click="submitComment(iss.id, c.id)" :disabled="!hasContent(newCommentText)">등록</button>
                </div>
              </div>
            </div>
          </div>
          <!-- 댓글 입력 -->
          <div v-if="!readonly">
            <div v-if="commentingIssueId === iss.id && !replyingToCommentId" class="comment-editor-form">
              <!-- @태그 chip -->
              <div v-if="staffList.length > 0" class="comment-tag-row">
                <span class="comment-tag-label">@태그</span>
                <button
                  v-for="s in staffList.filter(s => s.name !== auth.user?.name)"
                  :key="s.id || s.name"
                  class="target-chip"
                  :class="{ active: commentTagged.includes(s.name) }"
                  @click="toggleCommentTag(s.name, iss.id)"
                >{{ s.name }}</button>
              </div>
              <TiptapEditor ref="commentEditorRef" v-model="newCommentText" height="120px" placeholder="댓글을 입력하세요..." />
              <div class="flex gap-4 mt-6" style="align-items:center;justify-content:flex-end">
                <label v-if="auth.isLeader" class="requires-answer-toggle">
                  <input type="checkbox" v-model="commentRequiresAnswer" />
                  답변 요구
                </label>
                <button class="btn btn-ghost btn-xs" @click="cancelComment">취소</button>
                <button class="btn btn-primary btn-xs" @click="submitComment(iss.id, null)" :disabled="!hasContent(newCommentText) || (staffList.length > 0 && commentTagged.length === 0)">
                  {{ editingCommentId ? '저장' : '등록' }}
                </button>
              </div>
            </div>
            <button v-else-if="commentingIssueId !== iss.id" class="btn-add-action mt-4" @click="startComment(iss.id)">
              <span class="material-symbols-outlined" style="font-size:13px;vertical-align:-2px">chat_bubble_outline</span>
              댓글
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- 이슈 추가 폼 -->
    <div v-if="adding" class="issue-item">
      <TiptapEditor v-model="newText" height="140px" @image-uploaded="onAddImageUploaded" />
      <div class="flex gap-8 mt-8" style="justify-content:flex-end">
        <button class="btn btn-ghost btn-sm" @click="cancelAdd">취소</button>
        <button class="btn btn-primary btn-sm" @click="addIssue" :disabled="!hasContent(newText)">저장</button>
      </div>
    </div>

    <div v-if="!adding && !readonly" class="issue-add-row">
      <button class="btn-add-action" @click="openAdd" data-tooltip="이번 주 진행 현황 및 이슈를 등록합니다">
        <span class="material-symbols-outlined" style="font-size:13px;vertical-align:-2px">add</span>
        진행 현황 및 이슈 등록
      </button>
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
import { copyToClipboard } from '../../utils/clipboard.js'
import { deleteOrphanedImages, deleteAllImages, deleteUrls } from '../../composables/useImageCleanup.js'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  issues:   { type: Array,  default: () => [] },
  staffList: { type: Array, default: () => [] },
  taskId:   { type: String, required: true },
  week:     { type: String, required: true },
  readonly: { type: Boolean, default: false },
})
const emit = defineEmits(['update:issues'])
const { toastMsg, showToast, toastError } = useToast()
const auth = useAuthStore()

// ── 링크 복사 ──
async function copyLink(iss) {
  const url = `${window.location.origin}/go/${iss.id}`
  await copyToClipboard(url)
  showToast('링크가 복사되었습니다')
}

// ── 추가 ──
const adding      = ref(false)
const newText     = ref('')
const addUploads  = ref([])

function openAdd() { adding.value = true; addUploads.value = [] }
function onAddImageUploaded(url) { addUploads.value.push(url) }
function resetAddForm() {
  adding.value = false; newText.value = ''; addUploads.value = []
}
function cancelAdd() {
  deleteUrls(addUploads.value)
  resetAddForm()
}

async function addIssue() {
  if (!hasContent(newText.value)) return
  try {
    const { data } = await axios.post('/api/issues', {
      task_id: props.taskId,
      week: props.week,
      issue: newText.value.trim(),
      assignee: auth.user?.name || '',
    })
    await deleteUrls(addUploads.value.filter(u => !newText.value.includes(u)))
    emit('update:issues', [...props.issues, data])
    resetAddForm()
    showToast('이슈가 등록되었습니다')
  } catch (e) { toastError(e, '이슈 등록 실패') }
}

// ── 수정 ──
const editingId   = ref('')
const editText    = ref('')
const editAssignee = ref('')
const editUploads = ref([])

function startEdit(iss) {
  editingId.value = iss.id; editText.value = iss.issue; editAssignee.value = iss.assignee
  editUploads.value = []
}
function resetEditForm() {
  editingId.value = ''; editText.value = ''; editAssignee.value = ''; editUploads.value = []
}
function cancelEdit() {
  deleteUrls(editUploads.value)
  resetEditForm()
}

async function saveEdit(id) {
  if (!hasContent(editText.value) || !editAssignee.value) return
  try {
    const oldIssue = props.issues.find(i => i.id === id)
    const { data } = await axios.put(`/api/issues/${id}`, {
      issue: editText.value.trim(),
      assignee: editAssignee.value,
    })
    await deleteOrphanedImages(oldIssue?.issue, editText.value)
    await deleteUrls(editUploads.value.filter(u => !editText.value.includes(u)))
    emit('update:issues', props.issues.map(i => i.id === id ? data : i))
    resetEditForm()
    showToast('수정되었습니다')
  } catch (e) { toastError(e, '수정 실패') }
}

// ── 삭제 ──
async function deleteIssue(id) {
  if (!confirm('이슈를 삭제하시겠습니까?')) return
  try {
    const target = props.issues.find(i => i.id === id)
    await axios.delete(`/api/issues/${id}`)
    await deleteAllImages(target?.issue)
    emit('update:issues', props.issues.filter(i => i.id !== id))
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '삭제 실패') }
}

// ── 댓글 ──
const commentingIssueId = ref('')
const replyingToCommentId = ref('')
const newCommentText = ref('')
const editingCommentId = ref('')
const commentTagged = ref([])
const commentRequiresAnswer = ref(false)
const commentEditorRef = ref(null)

function startComment(issueId) {
  commentingIssueId.value = issueId
  newCommentText.value = ''
  replyingToCommentId.value = ''
  commentTagged.value = []
  commentRequiresAnswer.value = false
}
function startReplyToComment(issueId, commentId) {
  commentingIssueId.value = issueId
  replyingToCommentId.value = commentId
  newCommentText.value = ''
  commentTagged.value = []
  commentRequiresAnswer.value = false
}
function cancelComment() {
  commentingIssueId.value = ''
  replyingToCommentId.value = ''
  editingCommentId.value = ''
  newCommentText.value = ''
  commentTagged.value = []
  commentRequiresAnswer.value = false
}
function startEditComment(issueId, c) {
  commentingIssueId.value = issueId
  editingCommentId.value = c.id
  newCommentText.value = c.comment
  commentTagged.value = [...(c.tagged_users || [])]
  commentRequiresAnswer.value = !!c.requires_answer
}

function toggleCommentTag(name) {
  const idx = commentTagged.value.indexOf(name)
  if (idx === -1) {
    commentTagged.value.push(name)
    commentEditorRef.value?.insertText(` @${name} `)
  } else {
    commentTagged.value.splice(idx, 1)
  }
}

function _updateComments(issueId, fn) {
  return props.issues.map(i => i.id === issueId ? { ...i, comments: fn(i.comments || []) } : i)
}

async function submitComment(issueId, parentId) {
  if (!hasContent(newCommentText.value)) return
  try {
    if (editingCommentId.value) {
      const { data } = await axios.put(`/api/issues/${issueId}/comments/${editingCommentId.value}`, {
        comment: newCommentText.value.trim(),
        tagged_users: [...commentTagged.value],
        requires_answer: commentRequiresAnswer.value,
      })
      emit('update:issues', _updateComments(issueId, comments =>
        comments.map(c => c.id === editingCommentId.value
          ? { ...c, ...data }
          : { ...c, replies: (c.replies || []).map(r => r.id === editingCommentId.value ? { ...r, ...data } : r) }
        )
      ))
      cancelComment()
    } else {
      const { data } = await axios.post(`/api/issues/${issueId}/comments`, {
        comment: newCommentText.value.trim(),
        comment_by: auth.user?.name || '',
        parent_id: parentId || null,
        requires_answer: commentRequiresAnswer.value,
        tagged_users: [...commentTagged.value],
      })
      window.dispatchEvent(new Event('refresh-notifications'))
      if (parentId) {
        emit('update:issues', _updateComments(issueId, comments =>
          comments.map(c => c.id === parentId
            ? { ...c, replies: [...(c.replies || []), data], is_answered: c.requires_answer ? 1 : c.is_answered }
            : c
          )
        ))
      } else {
        emit('update:issues', _updateComments(issueId, comments => [...comments, { ...data, replies: [] }]))
      }
    }
    cancelComment()
  } catch (e) { toastError(e, '댓글 등록 실패') }
}

async function deleteComment(issueId, commentId) {
  if (!confirm('삭제하시겠습니까?')) return
  try {
    const { data } = await axios.delete(`/api/issues/${issueId}/comments/${commentId}`)
    emit('update:issues', _updateComments(issueId, comments =>
      comments
        .filter(c => c.id !== commentId)
        .map(c => {
          const filtered = (c.replies || []).filter(r => r.id !== commentId)
          const unanswered = data.parent_unanswered === c.id
          return { ...c, replies: filtered, is_answered: unanswered ? 0 : c.is_answered }
        })
    ))
  } catch (e) { toastError(e, '삭제 실패') }
}
</script>

<style scoped>
.section-block {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--outline);
}
.issue-item {
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  background: var(--surface);
  overflow: hidden;
}
.issue-box {
  background: #fff7ed;
  border-left: 3px solid #f59e0b;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
}
.mt-4 { margin-top: 4px; }
.comment-section {
  margin: 10px -12px -12px -12px;
  padding: 10px 12px 12px;
  background: var(--gray-50);
  border-top: 1px solid var(--outline);
}
.comment-section-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--fs-xs);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  margin-bottom: 8px;
}
.comment-section-label .material-symbols-outlined { font-size: 14px; }
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

.issue-add-row {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--outline);
}
</style>

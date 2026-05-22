<template>
  <div class="section-block">
    <div class="section-label">
      <span class="material-symbols-outlined section-icon">warning</span>
      이슈
    </div>

    <!-- 등록된 이슈 목록 -->
    <div v-for="iss in issues" :key="iss.id" :id="'issue-' + iss.id" class="issue-item">
      <template v-if="editingId === iss.id">
        <div class="form-group">
          <label class="form-label">등록자</label>
          <select v-model="editAssignee" class="form-control">
            <option value="">선택</option>
            <option v-for="s in staffList" :key="s.id" :value="s.name">{{ s.name }}</option>
          </select>
        </div>
        <TiptapEditor v-model="editText" height="140px" @image-uploaded="url => editUploads.push(url)" />
        <div class="flex gap-8 mt-8" style="justify-content:flex-end">
          <button class="btn btn-ghost btn-sm" @click="cancelEdit">취소</button>
          <button class="btn btn-primary btn-sm" @click="saveEdit(iss.id)" :disabled="!hasContent(editText) || !editAssignee">저장</button>
        </div>
      </template>
      <template v-else>
        <div class="issue-box">
          <TiptapPreview :modelValue="iss.issue" />
        </div>
        <div class="flex gap-4 mt-8" style="align-items:center">
          <span v-if="iss.assignee" class="badge badge-gray">{{ iss.assignee }}</span>
          <span class="issue-date">{{ iss.updated_at ?? iss.created_at }}</span>
          <div style="margin-left:auto;display:flex;gap:4px">
            <button class="btn btn-ghost btn-xs" @click="copyLink(iss)" data-tooltip="링크 복사 — 메신저 공유용">
              <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">link</span>
            </button>
            <button class="btn btn-ghost btn-xs" @click="startEdit(iss)" data-tooltip="이슈 수정">수정</button>
            <button class="btn btn-danger btn-xs" @click="deleteIssue(iss.id)" data-tooltip="이슈 삭제">삭제</button>
          </div>
        </div>
      </template>
    </div>

    <!-- 이슈 추가 폼 -->
    <div v-if="adding" class="issue-item">
      <div class="form-group">
        <label class="form-label">등록자</label>
        <select v-model="newAssignee" class="form-control">
          <option value="">선택</option>
          <option v-for="s in staffList" :key="s.id" :value="s.name">{{ s.name }}</option>
        </select>
      </div>
      <TiptapEditor v-model="newText" height="140px" @image-uploaded="url => addUploads.push(url)" />
      <div class="flex gap-8 mt-8" style="justify-content:flex-end">
        <button class="btn btn-ghost btn-sm" @click="cancelAdd">취소</button>
        <button class="btn btn-primary btn-sm" @click="addIssue" :disabled="!hasContent(newText) || !newAssignee">저장</button>
      </div>
    </div>

    <button v-if="!adding" class="btn btn-ghost btn-sm mt-4" @click="openAdd" data-tooltip="이번 주 이슈를 등록합니다">+ 이슈 등록</button>
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

const props = defineProps({
  issues:   { type: Array,  default: () => [] },
  staffList: { type: Array, default: () => [] },
  taskId:   { type: String, required: true },
  week:     { type: String, required: true },
})
const emit = defineEmits(['update:issues'])
const { toastMsg, showToast, toastError } = useToast()

// ── 링크 복사 ──
async function copyLink(iss) {
  const url = `${window.location.origin}/go/${iss.id}`
  await copyToClipboard(url)
  showToast('링크가 복사되었습니다')
}

// ── 추가 ──
const adding      = ref(false)
const newText     = ref('')
const newAssignee = ref('')
const addUploads  = ref([])

function openAdd() { adding.value = true; addUploads.value = [] }
function cancelAdd() {
  deleteUrls(addUploads.value.filter(u => !newText.value.includes(u)))
  adding.value = false; newText.value = ''; newAssignee.value = ''; addUploads.value = []
}

async function addIssue() {
  if (!hasContent(newText.value) || !newAssignee.value) return
  try {
    const { data } = await axios.post('/api/issues', {
      task_id: props.taskId,
      week: props.week,
      issue: newText.value.trim(),
      assignee: newAssignee.value,
    })
    await deleteUrls(addUploads.value.filter(u => !newText.value.includes(u)))
    emit('update:issues', [...props.issues, data])
    cancelAdd()
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
function cancelEdit() {
  deleteUrls(editUploads.value.filter(u => !editText.value.includes(u)))
  editingId.value = ''; editText.value = ''; editAssignee.value = ''; editUploads.value = []
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
    cancelEdit()
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
</script>

<style scoped>
.section-block {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--outline);
}
.issue-item {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed var(--outline);
}
.issue-item:last-of-type { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.issue-box {
  background: #fff7ed;
  border-left: 3px solid #f59e0b;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
}
.issue-date { font-size: 11px; color: var(--text-muted); }
.mt-4 { margin-top: 4px; }
</style>

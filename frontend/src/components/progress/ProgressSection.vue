<template>
  <div class="section-block">
    <div class="section-label">
      <span class="material-symbols-outlined section-icon">warning</span>
      이슈
    </div>

    <!-- 저장된 이슈 표시 -->
    <template v-if="progress?.issue && !editing">
      <div class="issue-box">
        <MdPreview language="en-US" :modelValue="progress.issue" class="md-preview-inline" />
      </div>
      <div class="flex gap-4 mt-8" style="align-items:center">
        <span v-if="progress.assignee" class="badge badge-gray">{{ progress.assignee }}</span>
        <div style="margin-left:auto;display:flex;gap:4px">
          <button class="btn btn-ghost btn-xs" @click="startEdit">수정</button>
          <button class="btn btn-danger btn-xs" @click="handleDelete">삭제</button>
        </div>
      </div>
    </template>

    <!-- 이슈 입력/수정 폼 -->
    <template v-else-if="editing || adding">
      <div class="form-group">
        <label class="form-label">등록자</label>
        <select v-model="assigneeName" class="form-control">
          <option value="">선택</option>
          <option v-for="s in staffList" :key="s.id" :value="s.name">{{ s.name }}</option>
        </select>
      </div>
      <MarkdownEditor v-model="issueText" height="140px" />
      <div class="flex gap-8 mt-8" style="justify-content:flex-end">
        <button class="btn btn-ghost btn-sm" @click="cancel">취소</button>
        <button class="btn btn-primary btn-sm" @click="handleSave" :disabled="!hasContent(issueText) || !assigneeName">저장</button>
      </div>
    </template>

    <!-- 이슈 없을 때 -->
    <template v-else>
      <button class="btn btn-ghost btn-sm" @click="startAdd">+ 이슈 등록</button>
    </template>
  </div>

  <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { MdPreview } from 'md-editor-v3'
import MarkdownEditor from '../MarkdownEditor.vue'
import { useToast } from '../../composables/useToast.js'

const props = defineProps({
  progress: { type: Object, default: null },
  staffList: { type: Array, default: () => [] },
  taskId: { type: String, required: true },
  week: { type: String, required: true },
  objectiveId: { type: String, default: '' },
})
const emit = defineEmits(['update:progress'])
const { toastMsg, showToast } = useToast()

const adding = ref(false)
const editing = ref(false)
const issueText = ref('')
const assigneeName = ref('')

function hasContent(text) { return !!(text && text.trim()) }

function startAdd() {
  adding.value = true
  issueText.value = ''
  assigneeName.value = ''
}

function startEdit() {
  editing.value = true
  issueText.value = props.progress?.issue || ''
  assigneeName.value = props.progress?.assignee || ''
}

function cancel() {
  adding.value = false
  editing.value = false
}

watch(() => props.progress, () => {
  if (!props.progress) { adding.value = false; editing.value = false }
})

async function handleSave() {
  if (!hasContent(issueText.value) || !assigneeName.value) return
  try {
    const payload = {
      week: props.week,
      task_id: props.taskId,
      objective: props.objectiveId,
      result: props.progress?.result || '',
      issue: issueText.value.trim(),
      assignee: assigneeName.value,
    }
    let saved
    if (props.progress) {
      const { data } = await axios.put(`/api/progress/${props.progress.id}`, { issue: issueText.value.trim(), assignee: assigneeName.value })
      saved = data
    } else {
      const { data } = await axios.post('/api/progress', payload)
      saved = data
    }
    emit('update:progress', saved)
    cancel()
    showToast('저장되었습니다')
  } catch { showToast('저장 실패') }
}

async function handleDelete() {
  if (!confirm('이슈를 삭제하시겠습니까?')) return
  try {
    if (props.progress?.result) {
      const { data } = await axios.put(`/api/progress/${props.progress.id}`, { issue: '' })
      emit('update:progress', data)
    } else {
      await axios.delete(`/api/progress/${props.progress.id}`)
      emit('update:progress', null)
    }
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}
</script>

<style scoped>
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
.mt-8 { margin-top: 8px; }
.issue-box {
  background: #fff7ed;
  border-left: 3px solid #f59e0b;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
}
</style>

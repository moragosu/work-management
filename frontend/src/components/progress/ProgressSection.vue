<template>
  <div v-if="show" class="section-block">
    <div class="section-label">
      <span class="material-symbols-outlined section-icon">edit_note</span>
      이번 주 진행 내용
    </div>

    <!-- 저장된 진행 내용 표시 -->
    <template v-if="progress && !editing">
      <div class="progress-view">
        <div class="progress-meta">
          <span class="badge badge-gray">{{ progress.assignee || '담당자 없음' }}</span>
        </div>
        <MdPreview language="en-US" :modelValue="progress.result" class="md-preview-inline" />
        <div v-if="progress.issue" class="issue-box">
          <span class="issue-label">
            <span class="material-symbols-outlined" style="font-size:13px;width:13px;height:13px;vertical-align:middle">warning</span>
            이슈
          </span>
          <MdPreview language="en-US" :modelValue="progress.issue" class="md-preview-inline" />
        </div>
        <div class="flex gap-4 mt-8" style="justify-content:flex-end">
          <button class="btn btn-ghost btn-xs" @click="startEdit">수정</button>
          <button class="btn btn-danger btn-xs" @click="handleDelete">삭제</button>
        </div>
      </div>
    </template>

    <!-- 진행 내용 입력/수정 폼 -->
    <template v-else-if="editing || adding">
      <div class="progress-form">
        <div class="form-group">
          <label class="form-label">담당자</label>
          <select v-model="form.assignee" class="form-control">
            <option value="">선택</option>
            <option v-for="m in taskMembers" :key="m.id" :value="m.name">{{ m.name }}</option>
            <template v-for="s in staffList" :key="s.id">
              <option v-if="!taskMembers.find(m => m.id === s.id)" :value="s.name">{{ s.name }}</option>
            </template>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">진행 내용</label>
          <MarkdownEditor v-model="form.result" height="220px" />
        </div>
        <div class="form-group">
          <label class="form-label">이슈 <span class="text-muted text-sm">(선택)</span></label>
          <MarkdownEditor v-model="form.issue" height="140px" />
        </div>
        <div class="flex gap-8" style="justify-content:flex-end">
          <button class="btn btn-ghost btn-sm" @click="cancel">취소</button>
          <button class="btn btn-primary btn-sm" @click="handleSave" :disabled="!hasContent(form.result)">저장</button>
        </div>
      </div>
    </template>

    <!-- 진행 내용 없을 때 -->
    <template v-else>
      <button class="btn btn-ghost btn-sm" @click="startAdd">+ 진행 내용 입력</button>
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
  taskMembers: { type: Array, default: () => [] },
  taskId: { type: String, required: true },
  week: { type: String, required: true },
  objectiveId: { type: String, default: '' },
  show: { type: Boolean, default: true },
})
const emit = defineEmits(['update:progress'])
const { toastMsg, showToast } = useToast()

const adding = ref(false)
const editing = ref(false)
const form = ref({ assignee: '', result: '', issue: '' })

function hasContent(text) { return !!(text && text.trim()) }

function startAdd() {
  adding.value = true
  form.value = { assignee: '', result: '', issue: '' }
}

function startEdit() {
  editing.value = true
  form.value = { assignee: props.progress?.assignee || '', result: props.progress?.result || '', issue: props.progress?.issue || '' }
}

function cancel() {
  adding.value = false
  editing.value = false
}

watch(() => props.progress, () => {
  if (!props.progress) { adding.value = false; editing.value = false }
})

async function handleSave() {
  if (!hasContent(form.value.result)) return
  try {
    const payload = {
      week: props.week,
      task_id: props.taskId,
      objective: props.objectiveId,
      ...form.value,
    }
    let saved
    if (props.progress) {
      const { data } = await axios.put(`/api/progress/${props.progress.id}`, form.value)
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
  if (!confirm('진행 내용을 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/progress/${props.progress.id}`)
    emit('update:progress', null)
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
.progress-view { display: flex; flex-direction: column; gap: 8px; }
.progress-meta { display: flex; align-items: center; gap: 8px; }
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
.progress-form { display: flex; flex-direction: column; gap: 12px; }
</style>

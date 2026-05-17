<template>
  <div>
    <div class="grid-4" style="margin-bottom:20px">
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">전체 과제</div>
      </div></div>
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value" style="color:var(--primary)">{{ stats.totalKR }}</div>
        <div class="stat-label">전체 KR</div>
      </div></div>
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value" style="color:#22c55e">{{ stats.withMembers }}</div>
        <div class="stat-label">인력 배정 완료</div>
      </div></div>
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value" style="color:#f59e0b">{{ stats.noMembers }}</div>
        <div class="stat-label">인력 미배정</div>
      </div></div>
    </div>

    <div class="flex-between" style="margin-bottom:16px">
      <button class="btn btn-ghost btn-sm" @click="exportCsv" data-tooltip="과제 목록을 CSV 파일로 내보내기">⬇ CSV 다운로드</button>
      <button class="btn btn-primary btn-sm" @click="openModal()" data-tooltip="새 과제 추가">+ 과제 추가</button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="tasks.length === 0" class="empty-state">
        <div class="empty-icon">📋</div><p>등록된 과제가 없습니다.</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>과제명</th><th>목표</th><th>참여 인력</th><th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in tasks" :key="t.id" :id="'task-row-' + t.id">
              <td><span class="badge badge-blue">{{ t.id }}</span></td>
              <td style="font-weight:600">{{ t.name }}</td>
              <td><span class="text-sm">{{ getObjectiveName(t.objective_id) }}</span></td>
              <td>
                <div v-if="getTaskMembers(t.id).length > 0" class="member-chips">
                  <span v-for="m in getTaskMembers(t.id)" :key="m.id" class="badge badge-gray" :title="m.role">{{ m.name }}</span>
                </div>
                <span v-else class="text-muted text-sm">미배정</span>
              </td>
              <td>
                <div class="flex gap-8">
                  <button class="btn btn-ghost btn-xs" @click="openModal(t)" data-tooltip="과제 정보 수정">수정</button>
                  <button class="btn btn-danger btn-xs" @click="deleteTask(t)" data-tooltip="과제 삭제">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Task Form Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingId ? '과제 수정' : '과제 추가' }}</h3>
          <button class="modal-close" @click="showModal = false" data-tooltip="닫기">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">과제 ID</label>
            <input v-model="form.id" class="form-control" :placeholder="nextId" disabled />
            <span class="text-sm text-muted">자동 생성</span>
          </div>
          <div class="form-group">
            <label class="form-label">과제명 *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">연결 목표</label>
            <select v-model="form.objective_id" class="form-control">
              <option value="">없음</option>
              <option v-for="o in objectives" :key="o.id" :value="o.id">{{ o.id }}: {{ o.name }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showModal = false" data-tooltip="변경사항 취소">취소</button>
          <button class="btn btn-primary" @click="submitTask" :disabled="!form.name" data-tooltip="과제 저장">저장</button>
        </div>
      </div>
    </div>

    <!-- Task Member Modal -->
    <div v-if="showMemberModal" class="modal-overlay" @click.self="showMemberModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>인력 연결 - {{ selectedTask?.name }}</h3>
          <button class="modal-close" @click="showMemberModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedTask?.members?.length > 0" style="margin-bottom:16px">
            <div class="text-sm text-muted" style="margin-bottom:8px">연결된 인력:</div>
            <div v-for="m in selectedTask.members" :key="m.staff_id" class="kr-edit-item">
              <div class="flex gap-8" style="align-items:center">
                <div style="flex:1">
                  <div>{{ m.name }}</div>
                  <div class="text-xs text-muted">{{ m.role || '역할 없음' }}</div>
                </div>
                <button class="btn btn-danger btn-xs" @click="removeMember(m.staff_id)">✕</button>
              </div>
            </div>
          </div>
          <div class="text-sm text-muted" style="margin-bottom:8px">인력 추가:</div>
          <select v-model="selectedStaffId" class="form-control" style="margin-bottom:8px">
            <option value="">선택</option>
            <option v-for="s in availableStaff" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <input v-model="selectedStaffRole" class="form-control" placeholder="역할을 입력하세요" style="margin-bottom:8px" />
          <button class="btn btn-primary btn-sm" @click="addMember" :disabled="!selectedStaffId">추가</button>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showMemberModal = false">닫기</button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useToast } from '../../composables/useToast.js'
import { parseIds } from '../../utils/parseIds.js'

const props = defineProps({
  tasks: { type: Array, default: () => [] },
  objectives: { type: Array, default: () => [] },
  staffList: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  nextId: { type: String, default: 'T1' },
})
const emit = defineEmits(['refresh'])
const route = useRoute()
const { toastMsg, showToast } = useToast()

// ── 통계 ──
const stats = computed(() => ({
  total: props.tasks.length,
  totalKR: props.objectives.reduce((s, o) => s + (o.key_results?.length || 0), 0),
  withMembers: props.tasks.filter(t => getTaskMembers(t.id).length > 0).length,
  noMembers: props.tasks.filter(t => getTaskMembers(t.id).length === 0).length,
}))

// ── 헬퍼 ──
function getTaskMembers(taskId) { return props.staffList.filter(s => parseIds(s.selected_tasks).includes(taskId)) }
function getObjectiveName(id) {
  if (!id) return '-'
  const o = props.objectives.find(obj => obj.id === id)
  return o ? `${o.id}: ${o.name}` : id
}
function exportCsv() { window.open('/api/admin/export/tasks', '_blank') }

// ── Task Form Modal ──
const showModal = ref(false)
const editingId = ref(null)
const defaultForm = () => ({ id: '', name: '', objective_id: '' })
const form = ref(defaultForm())

function openModal(t = null) {
  if (t) {
    form.value = { ...t }
    editingId.value = t.id
  } else {
    form.value = { ...defaultForm(), id: props.nextId }
    editingId.value = null
  }
  showModal.value = true
}

async function submitTask() {
  try {
    if (editingId.value) {
      await axios.put(`/api/tasks/${editingId.value}`, form.value)
    } else {
      await axios.post('/api/tasks', form.value)
    }
    showModal.value = false
    showToast('저장되었습니다')
    emit('refresh')
  } catch (e) {
    showToast(e.response?.data?.detail || '저장 실패')
  }
}

async function deleteTask(t) {
  if (!confirm(`"${t.name}"을(를) 삭제하시겠습니까?`)) return
  await axios.delete(`/api/tasks/${t.id}`)
  showToast('삭제되었습니다')
  emit('refresh')
}

// ── Task Member Modal ──
const showMemberModal = ref(false)
const selectedTask = ref(null)
const selectedStaffId = ref('')
const selectedStaffRole = ref('')

const availableStaff = computed(() => {
  if (!selectedTask.value) return []
  const memberIds = selectedTask.value.members?.map(m => m.staff_id) || []
  return props.staffList.filter(s => !memberIds.includes(s.id))
})

async function addMember() {
  if (!selectedStaffId.value) return
  const staff = props.staffList.find(s => s.id === selectedStaffId.value)
  if (!staff) return
  selectedTask.value.members = selectedTask.value.members || []
  selectedTask.value.members.push({ staff_id: staff.id, name: staff.name, role: selectedStaffRole.value })
  try {
    await axios.put(`/api/tasks/${selectedTask.value.id}`, { members: selectedTask.value.members })
    emit('refresh')
    selectedStaffId.value = ''
    selectedStaffRole.value = ''
    showToast('인력이 추가되었습니다')
  } catch { showToast('추가 실패') }
}

async function removeMember(staffId) {
  selectedTask.value.members = selectedTask.value.members.filter(m => m.staff_id !== staffId)
  try {
    await axios.put(`/api/tasks/${selectedTask.value.id}`, { members: selectedTask.value.members })
    showToast('삭제되었습니다')
    emit('refresh')
  } catch { showToast('삭제 실패') }
}

// ── focusTask (대시보드에서 이동 시) ──
onMounted(async () => {
  if (route.query.focusTask) {
    await nextTick()
    await new Promise(r => setTimeout(r, 100))
    const el = document.getElementById(`task-row-${route.query.focusTask}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      el.classList.add('highlight-focus')
      setTimeout(() => el?.classList.remove('highlight-focus'), 2200)
    }
  }
})
</script>

<style scoped>
.kr-edit-item {
  background: var(--gray-50);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 8px;
}
.member-chips { display: flex; flex-wrap: wrap; gap: 4px; }
</style>

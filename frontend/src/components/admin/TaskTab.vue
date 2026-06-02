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

    <div class="flex-between" style="margin-bottom:12px">
      <button class="btn btn-ghost btn-sm" @click="exportCsv" data-tooltip="과제 목록을 CSV 파일로 내보내기">⬇ CSV 다운로드</button>
      <div style="display:flex;gap:8px;align-items:center">
        <button
          v-if="hasAnySubTasks"
          class="btn btn-ghost btn-sm"
          @click="toggleAllExpand"
          :data-tooltip="allExpanded ? '소과제 행을 모두 접습니다' : '소과제 행을 모두 펼칩니다'"
        >
          <span class="material-symbols-outlined" style="font-size:15px;vertical-align:-3px">{{ allExpanded ? 'unfold_less' : 'unfold_more' }}</span>
          {{ allExpanded ? '전체 접기' : '전체 펼치기' }}
        </button>
        <button class="btn btn-primary btn-sm" @click="openModal()" data-tooltip="새 과제 추가">+ 과제 추가</button>
      </div>
    </div>

    <div v-if="props.staffList.length > 0" class="filter-bar staff-filter-bar">
      <span class="filter-label-sm">인력</span>
      <button
        v-for="s in props.staffList"
        :key="s.username"
        class="staff-chip"
        :class="{ 'staff-chip-active': selectedStaffFilter.includes(s.username) }"
        @click="toggleStaffFilter(s.username)"
      >{{ s.name }}</button>
      <button v-if="selectedStaffFilter.length > 0" class="btn btn-ghost btn-xs" @click="selectedStaffFilter = []" data-tooltip="인력 필터 초기화">전체 보기</button>
    </div>

    <!-- 일괄 적용 툴바 -->
    <div v-if="selectedTaskIds.length > 0" class="bulk-toolbar">
      <span class="bulk-count">{{ selectedTaskIds.length }}개 선택됨</span>
      <select v-model="bulkTarget" class="form-control bulk-select">
        <option value="">적용 대상 선택</option>
        <option v-for="t in props.taskTargets" :key="t" :value="t">{{ t }}</option>
      </select>
      <button class="btn btn-primary btn-sm" @click="applyBulkTarget" :disabled="!bulkTarget">일괄 적용</button>
      <button class="btn btn-ghost btn-sm" @click="selectedTaskIds = []">선택 해제</button>
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
              <th style="width:36px">
                <input type="checkbox" :checked="isAllSelected" :indeterminate.prop="isPartialSelected" @change="toggleAll" />
              </th>
              <th>ID</th><th>적용 대상</th><th>과제명</th><th>목표</th><th>참여 인력</th><th></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="t in sortedTasks" :key="t.id">
              <tr :id="'task-row-' + t.id" :class="{ 'row-selected': selectedTaskIds.includes(t.id) }">
                <td><input type="checkbox" :checked="selectedTaskIds.includes(t.id)" @change="toggleTask(t.id)" /></td>
                <td>
                  <div style="display:flex;align-items:center;gap:4px">
                    <button
                      v-if="t.sub_tasks && t.sub_tasks.length > 0"
                      class="expand-btn"
                      @click="toggleExpand(t.id)"
                      :data-tooltip="collapsedTaskIds.has(t.id) ? '소과제 펼치기' : '소과제 접기'"
                    >
                      <span class="material-symbols-outlined expand-icon" :class="{ collapsed: collapsedTaskIds.has(t.id) }">expand_more</span>
                    </button>
                    <span v-else style="width:20px;display:inline-block"></span>
                    <span class="badge badge-blue">{{ t.id }}</span>
                    <span v-if="t.sub_tasks && t.sub_tasks.length > 0" class="sub-count-badge" :title="`소과제 ${t.sub_tasks.length}개`">{{ t.sub_tasks.length }}</span>
                  </div>
                </td>
                <td><span v-if="t.target" :class="targetBadgeClass(t.target)">{{ t.target }}</span><span v-else class="text-muted text-sm">-</span></td>
                <td style="font-weight:600">{{ t.name }}</td>
                <td><span class="text-sm">{{ getObjectiveName(t.objective_id) }}</span></td>
                <td>
                  <div v-if="taskMembers(t.id).length > 0" class="member-chips">
                    <span v-for="m in taskMembers(t.id)" :key="m.username" class="badge badge-gray" :title="m.job_title">{{ m.name }}</span>
                  </div>
                  <span v-else class="text-muted text-sm">미배정</span>
                </td>
                <td>
                  <div class="flex gap-8">
                    <button class="btn btn-ghost btn-xs" @click="router.push(`/tasks/${t.id}/history`)" data-tooltip="주차별 이력 보기">이력</button>
                    <button class="btn btn-ghost btn-xs" @click="openModal(t)" data-tooltip="과제 정보 수정">수정</button>
                    <button class="btn btn-danger btn-xs" @click="deleteTask(t)" data-tooltip="과제 삭제">삭제</button>
                  </div>
                </td>
              </tr>
              <tr
                v-for="st in (collapsedTaskIds.has(t.id) ? [] : (t.sub_tasks || []))"
                :key="st.id"
                class="sub-task-row"
                :class="{ 'sub-task-row-done': st.done }"
              >
                <td></td>
                <td>
                  <div class="sub-task-row-id">
                    <span class="sub-task-row-indent">└</span>
                    <span class="sub-task-row-badge">{{ st.id }}</span>
                    <span v-if="st.done" class="sub-task-done-pill">완료</span>
                  </div>
                </td>
                <td></td>
                <td class="sub-task-row-name">{{ st.name || '(이름 없음)' }}</td>
                <td></td>
                <td>
                  <div v-if="subTaskMembers(st.id).length > 0" class="member-chips">
                    <span v-for="m in subTaskMembers(st.id)" :key="m.username" class="badge badge-gray" :title="m.job_title">{{ m.name }}</span>
                  </div>
                  <span v-else class="text-muted text-sm">미배정</span>
                </td>
                <td></td>
              </tr>
            </template>
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
            <input
              v-model="form.id"
              class="form-control"
              :class="{ 'input-error': idConflict }"
              :disabled="!!editingId"
            />
            <span v-if="idConflict" class="text-sm" style="color:var(--danger)">이미 존재하는 ID입니다</span>
            <div v-if="!editingId && props.reusableIds.length > 0" class="reusable-ids">
              <span class="text-sm text-muted">재사용 가능:</span>
              <button
                v-for="rid in props.reusableIds"
                :key="rid"
                type="button"
                class="reusable-chip"
                @click="form.id = rid"
              >{{ rid }}</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">과제명 *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">적용 대상</label>
            <select v-model="form.target" class="form-control">
              <option value="">선택 안함</option>
              <option v-for="t in props.taskTargets" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">연결 목표</label>
            <select v-model="form.objective_id" class="form-control">
              <option value="">없음</option>
              <option v-for="o in objectives" :key="o.id" :value="o.id">{{ o.id }}: {{ o.name }}</option>
            </select>
          </div>
          <div v-if="editingId" class="form-group">
            <label class="form-label">소과제</label>
            <div class="sub-task-list">
              <div v-for="(st, idx) in form.sub_tasks" :key="idx" class="sub-task-edit-row">
                <span class="badge badge-gray sub-task-id">{{ st.id }}</span>
                <input v-model="st.name" class="form-control sub-task-input" placeholder="소과제명" />
                <label class="done-toggle" :title="st.done ? '완료 취소' : '완료로 표시'">
                  <input type="checkbox" v-model="st.done" />
                  <span>완료</span>
                </label>
                <button type="button" class="btn btn-danger btn-xs" @click="removeSubTask(idx)">✕</button>
              </div>
              <button type="button" class="btn btn-ghost btn-sm" @click="addSubTask">+ 소과제 추가</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showModal = false" data-tooltip="변경사항 취소">취소</button>
          <button class="btn btn-primary" @click="submitTask" :disabled="!form.name || !form.id || idConflict" data-tooltip="과제 저장">저장</button>
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
            <div v-for="m in selectedTask.members" :key="m.username" class="kr-edit-item">
              <div class="flex gap-8" style="align-items:center">
                <div style="flex:1">
                  <div>{{ m.name }}</div>
                  <div class="text-xs text-muted">{{ m.role || '역할 없음' }}</div>
                </div>
                <button class="btn btn-danger btn-xs" @click="removeMember(m.username)">✕</button>
              </div>
            </div>
          </div>
          <div class="text-sm text-muted" style="margin-bottom:8px">인력 추가:</div>
          <select v-model="selectedStaffId" class="form-control" style="margin-bottom:8px">
            <option value="">선택</option>
            <option v-for="s in availableStaff" :key="s.username" :value="s.username">{{ s.name }}</option>
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
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useToast } from '../../composables/useToast.js'
import { getTaskMembers } from '../../utils/staff.js'

const props = defineProps({
  tasks: { type: Array, default: () => [] },
  objectives: { type: Array, default: () => [] },
  staffList: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  nextId: { type: String, default: 'T1' },
  reusableIds: { type: Array, default: () => [] },
  taskTargets: { type: Array, default: () => ['MX', 'VD', 'DA', '공통'] },
})
const emit = defineEmits(['refresh'])
const route = useRoute()
const router = useRouter()
const { toastMsg, showToast, toastError } = useToast()

// ── 통계 ──
const stats = computed(() => ({
  total: props.tasks.length,
  totalKR: props.objectives.reduce((s, o) => s + (o.key_results?.length || 0), 0),
  withMembers: props.tasks.filter(t => taskMembers(t.id).length > 0).length,
  noMembers: props.tasks.filter(t => taskMembers(t.id).length === 0).length,
}))

// ── 헬퍼 ──
function taskMembers(taskId) { return getTaskMembers(taskId, props.staffList) }
function subTaskMembers(subTaskId) { return getTaskMembers(subTaskId, props.staffList) }
function getObjectiveName(id) {
  if (!id) return '-'
  const o = props.objectives.find(obj => obj.id === id)
  return o ? `${o.id}: ${o.name}` : id
}
function exportCsv() { window.open('/api/admin/export/tasks', '_blank') }

const TARGET_CLASSES = { MX: 'badge badge-blue', VD: 'badge badge-green', DA: 'badge badge-orange', '공통': 'badge badge-gray' }
function targetBadgeClass(target) { return TARGET_CLASSES[target] || 'badge badge-gray' }

// ── 소과제 접기/펼치기 ──
const collapsedTaskIds = ref(new Set())

function toggleExpand(taskId) {
  const next = new Set(collapsedTaskIds.value)
  if (next.has(taskId)) next.delete(taskId)
  else next.add(taskId)
  collapsedTaskIds.value = next
}

const hasAnySubTasks = computed(() =>
  props.tasks.some(t => t.sub_tasks?.length > 0)
)
const allExpanded = computed(() =>
  props.tasks.filter(t => t.sub_tasks?.length > 0).every(t => !collapsedTaskIds.value.has(t.id))
)
function toggleAllExpand() {
  if (allExpanded.value) {
    collapsedTaskIds.value = new Set(props.tasks.filter(t => t.sub_tasks?.length > 0).map(t => t.id))
  } else {
    collapsedTaskIds.value = new Set()
  }
}

// ── 인력 필터 ──
const selectedStaffFilter = ref([])
function toggleStaffFilter(staffId) {
  const idx = selectedStaffFilter.value.indexOf(staffId)
  if (idx === -1) selectedStaffFilter.value.push(staffId)
  else selectedStaffFilter.value.splice(idx, 1)
}

const sortedTasks = computed(() => {
  let list = props.tasks
  if (selectedStaffFilter.value.length > 0) {
    list = list.filter(t => taskMembers(t.id).some(m => selectedStaffFilter.value.includes(m.username)))
  }
  return [...list].sort((a, b) => {
    const aNum = parseInt(a.id.replace('T', '')) || 0
    const bNum = parseInt(b.id.replace('T', '')) || 0
    return aNum - bNum
  })
})

// ── 일괄 선택 ──
const selectedTaskIds = ref([])
const bulkTarget = ref('')

const isAllSelected = computed(() =>
  sortedTasks.value.length > 0 && sortedTasks.value.every(t => selectedTaskIds.value.includes(t.id))
)
const isPartialSelected = computed(() =>
  selectedTaskIds.value.length > 0 && !isAllSelected.value
)

function toggleAll(e) {
  if (e.target.checked) selectedTaskIds.value = sortedTasks.value.map(t => t.id)
  else selectedTaskIds.value = []
}
function toggleTask(id) {
  const idx = selectedTaskIds.value.indexOf(id)
  if (idx === -1) selectedTaskIds.value.push(id)
  else selectedTaskIds.value.splice(idx, 1)
}

async function applyBulkTarget() {
  if (!bulkTarget.value || selectedTaskIds.value.length === 0) return
  const count = selectedTaskIds.value.length
  const target = bulkTarget.value
  try {
    await axios.put('/api/tasks/bulk-target', { task_ids: selectedTaskIds.value, target })
    showToast(`${count}개 과제에 '${target}' 적용 완료`)
    selectedTaskIds.value = []
    bulkTarget.value = ''
    emit('refresh')
  } catch (e) { toastError(e, '일괄 적용 실패') }
}

// ── Task Form Modal ──
const showModal = ref(false)
const editingId = ref(null)
const defaultForm = () => ({ id: '', name: '', objective_id: '', target: '', sub_tasks: [] })
const form = ref(defaultForm())

const idConflict = computed(() =>
  !editingId.value && !!form.value.id && props.tasks.some(t => t.id === form.value.id)
)

function openModal(t = null) {
  if (t) {
    form.value = { ...t, sub_tasks: (t.sub_tasks || []).map(st => ({ ...st })) }
    editingId.value = t.id
  } else {
    form.value = { ...defaultForm(), id: props.nextId }
    editingId.value = null
  }
  showModal.value = true
}

function addSubTask() {
  const existing = form.value.sub_tasks || []
  const nums = existing.map(st => parseInt(st.id.split('-').at(-1)) || 0)
  const next = Math.max(0, ...nums) + 1
  form.value.sub_tasks = [...existing, { id: `${form.value.id}-${next}`, name: '', done: false }]
}

function removeSubTask(idx) {
  form.value.sub_tasks = form.value.sub_tasks.filter((_, i) => i !== idx)
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
  } catch (e) { toastError(e, '저장 실패') }
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
  const memberUsernames = selectedTask.value.members?.map(m => m.username) || []
  return props.staffList.filter(s => !memberUsernames.includes(s.username))
})

async function addMember() {
  if (!selectedStaffId.value) return
  const staff = props.staffList.find(s => s.username === selectedStaffId.value)
if (!staff) return
  selectedTask.value.members = selectedTask.value.members || []
  selectedTask.value.members.push({ username: staff.username, name: staff.name, role: selectedStaffRole.value })
  try {
    await axios.put(`/api/tasks/${selectedTask.value.id}`, { members: selectedTask.value.members })
    emit('refresh')
    selectedStaffId.value = ''
    selectedStaffRole.value = ''
    showToast('인력이 추가되었습니다')
  } catch (e) { toastError(e, '인력 추가 실패') }
}

async function removeMember(staffId) {
  selectedTask.value.members = selectedTask.value.members.filter(m => m.username !== staffId)
  try {
    await axios.put(`/api/tasks/${selectedTask.value.id}`, { members: selectedTask.value.members })
    showToast('삭제되었습니다')
    emit('refresh')
  } catch (e) { toastError(e, '인력 삭제 실패') }
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
.staff-filter-bar { gap: 6px; margin-bottom: 12px; }
.filter-label-sm { font-size: var(--fs-xs); font-weight: var(--fw-semibold); color: var(--text-muted); white-space: nowrap; }
.staff-chip {
  display: inline-flex; align-items: center; padding: 3px 10px;
  border-radius: 999px; border: 1px solid var(--outline);
  font-size: var(--fs-xs); font-family: inherit; cursor: pointer;
  background: var(--surface); color: var(--text-secondary); transition: all 0.15s;
}
.staff-chip:hover { border-color: var(--primary); color: var(--primary); }
.staff-chip-active { background: var(--primary-light); color: var(--primary); border-color: var(--primary); font-weight: var(--fw-semibold); }

.reusable-ids { display: flex; align-items: center; gap: 6px; margin-top: 6px; flex-wrap: wrap; }
.reusable-chip {
  padding: 2px 10px; border-radius: var(--radius-lg); font-size: var(--fs-xs); cursor: pointer;
  border: 1px solid var(--primary); color: var(--primary); background: transparent;
  transition: background 0.15s;
}
.reusable-chip:hover { background: var(--primary); color: #fff; }
.input-error { border-color: var(--danger) !important; }
.kr-edit-item {
  background: var(--gray-50);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 8px;
}
.member-chips { display: flex; flex-wrap: wrap; gap: 4px; }

.sub-count-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 16px; height: 16px; border-radius: var(--radius-md);
  background: var(--primary); color: #fff;
  font-size: var(--fs-3xs); font-weight: var(--fw-bold); padding: 0 4px;
  margin-left: 4px; vertical-align: middle;
}

.sub-task-list { display: flex; flex-direction: column; gap: 8px; }
.sub-task-edit-row {
  display: flex; align-items: center; gap: 8px;
  background: var(--gray-50); border-radius: 6px; padding: 6px 10px;
}
.sub-task-id { flex-shrink: 0; }
.sub-task-input { flex: 1; }
.done-toggle {
  display: flex; align-items: center; gap: 4px;
  font-size: var(--fs-xs); color: var(--text-muted); cursor: pointer; white-space: nowrap; flex-shrink: 0;
}

.bulk-toolbar {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; margin-bottom: 8px;
  background: var(--primary-light); border: 1px solid var(--primary);
  border-radius: var(--radius-md);
}
.bulk-count { font-size: var(--fs-sm); font-weight: var(--fw-semibold); color: var(--primary); white-space: nowrap; }
.bulk-select { max-width: 140px; padding: 4px 8px; font-size: var(--fs-sm); height: auto; }
.row-selected { background: var(--primary-light) !important; }

.expand-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  padding: 0;
  transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
}
.expand-btn:hover { background: var(--gray-100); color: var(--text-primary); }
.expand-icon {
  font-size: var(--fs-h3);
  transition: transform 0.2s;
}
.expand-icon.collapsed { transform: rotate(-90deg); }

.sub-task-row { background: var(--gray-50); }
.sub-task-row:hover { background: var(--gray-100) !important; }
.sub-task-row-done { opacity: 0.6; }
.sub-task-row td { padding-top: 5px !important; padding-bottom: 5px !important; border-bottom: 1px dashed var(--outline); }
.sub-task-row:last-of-type td { border-bottom: 1px solid var(--outline); }

.sub-task-row-id {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-left: 4px;
}
.sub-task-row-indent {
  color: var(--text-muted);
  font-size: var(--fs-sm);
  flex-shrink: 0;
}
.sub-task-row-badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-2xs);
  font-weight: var(--fw-bold);
  font-family: monospace;
  background: color-mix(in srgb, var(--color-primary, #4f8ef7) 10%, transparent);
  color: var(--color-primary, #4f8ef7);
  border: 1px solid color-mix(in srgb, var(--color-primary, #4f8ef7) 25%, transparent);
}
.sub-task-row-done .sub-task-row-badge {
  background: color-mix(in srgb, #22c55e 10%, transparent);
  color: var(--success);
  border-color: color-mix(in srgb, #22c55e 25%, transparent);
}
.sub-task-done-pill {
  display: inline-flex;
  align-items: center;
  padding: 1px 6px;
  border-radius: 999px;
  font-size: var(--fs-3xs);
  font-weight: var(--fw-semibold);
  background: color-mix(in srgb, #22c55e 15%, transparent);
  color: var(--success);
}
.sub-task-row-name {
  font-size: var(--fs-sm);
  color: var(--text-secondary);
  padding-left: 24px !important;
}
</style>

<template>
  <div>
    <div v-if="!embedded" class="page-header">
      <div>
        <h2>인력 관리</h2>
        <div class="subtitle">팀원 기술 현황 및 참여 목표</div>
      </div>
      <button class="btn btn-primary btn-sm" @click="openAddModal">+ 인력 추가</button>
    </div>

    <div :class="{ 'page-body': !embedded }">
      <div v-if="!embedded" class="grid-4" style="margin-bottom:24px">
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--primary)">{{ totalStaffCount }}</div>
            <div class="text-muted text-sm mt-8">총 인원</div>
          </div>
        </div>
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--primary)">{{ objectiveStats.O1?.count || 0 }}</div>
            <div class="text-muted text-sm mt-8">O1 참여</div>
          </div>
        </div>
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--primary)">{{ objectiveStats.O2?.count || 0 }}</div>
            <div class="text-muted text-sm mt-8">O2 참여</div>
          </div>
        </div>
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--primary)">{{ objectiveStats.O3?.count || 0 }}</div>
            <div class="text-muted text-sm mt-8">O3 참여</div>
          </div>
        </div>
      </div>

      <!-- 인력 필터 칩 -->
      <div v-if="staff.length > 0" class="filter-bar staff-filter-bar">
        <span class="filter-label-sm">인력</span>
        <button
          v-for="s in staff"
          :key="s.username"
          class="staff-chip"
          :class="{ 'staff-chip-active': selectedStaffFilter.includes(s.username) }"
          @click="toggleStaffFilter(s.username)"
        >{{ s.name }}</button>
        <button v-if="selectedStaffFilter.length > 0" class="btn btn-ghost btn-xs" @click="selectedStaffFilter = []">전체 보기</button>
      </div>

      <div class="card">
        <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
        <div v-else-if="staff.length === 0" class="empty-state">
          <div class="empty-icon">👥</div>
          <p>등록된 인력이 없습니다.</p>
        </div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th @click="sortBy('name')" style="cursor:pointer">
                  이름 <span v-if="sortKey === 'name'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('job_title')" style="cursor:pointer">
                  직책 <span v-if="sortKey === 'job_title'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('main_skills')" style="cursor:pointer">
                  주 기술 <span v-if="sortKey === 'main_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('sub_skills')" style="cursor:pointer">
                  부 기술 <span v-if="sortKey === 'sub_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th>참여 목표</th>
                <th style="width:90px"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in sortedStaff" :key="member.username">
                <td style="white-space:nowrap">
                  <div style="font-weight:600">{{ member.name }}</div>
                  <div style="font-size:11px;color:var(--text-muted);margin-top:2px">{{ member.username }}</div>
                </td>
                <td>
                  <input
                    class="form-control inline"
                    :value="member.job_title"
                    @input="debounceSave(member, 'job_title', $event.target.value)"
                  />
                </td>
                <td>
                  <input
                    class="form-control inline"
                    style="min-width:120px"
                    :value="member.main_skills"
                    @input="debounceSave(member, 'main_skills', $event.target.value)"
                  />
                </td>
                <td>
                  <input
                    class="form-control inline"
                    style="min-width:100px"
                    :value="member.sub_skills"
                    @input="debounceSave(member, 'sub_skills', $event.target.value)"
                  />
                </td>
                <td>
                  <div class="objective-task-list">
                    <div v-for="objId in getTaskIdsObjectiveIds(member.task_ids || [])" :key="objId" class="objective-item">
                      <div class="objective-header">
                        <span class="badge badge-blue">{{ objId }}</span>
                        <span class="objective-label">{{ getObjectiveName(objId) }}</span>
                      </div>
                      <div class="task-list">
                        <div
                          v-for="task in getTasksForObjective(member.task_ids || [], objId)"
                          :key="task.id"
                          class="task-item"
                          :class="{ 'sub-task-item': task.isSub }"
                        >
                          <span class="badge badge-gray">{{ task.id }}</span>
                          <span class="task-name">{{ task.name }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
                <td>
                  <div style="display:flex;gap:8px">
                    <button class="btn btn-ghost btn-xs" @click="editMember(member)">수정</button>
                    <button class="btn btn-danger btn-xs" @click="deleteMember(member)">삭제</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 추가/수정 모달 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedMember ? '인력 수정' : '인력 추가' }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="!selectedMember" class="form-group">
            <label class="form-label">아이디 (username) *</label>
            <input v-model="form.username" class="form-control" placeholder="예: gildong.hong" />
          </div>
          <div class="form-group">
            <label class="form-label">이름 *</label>
            <input v-model="form.name" class="form-control" :disabled="!!selectedMember" />
          </div>
          <div class="form-group">
            <label class="form-label">직책</label>
            <input v-model="form.job_title" class="form-control" />
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">주 기술</label>
              <input v-model="form.main_skills" class="form-control" placeholder="Python, PyTorch, ..." />
            </div>
            <div class="form-group">
              <label class="form-label">부 기술</label>
              <input v-model="form.sub_skills" class="form-control" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">참여 과제</label>
            <div class="task-group-list">
              <div v-for="objective in objectives" :key="objective.id" class="objective-group">
                <label class="objective-header objective-select-all">
                  <input
                    type="checkbox"
                    :checked="isObjectiveAllSelected(objective.id)"
                    v-indeterminate="isObjectivePartialSelected(objective.id)"
                    @change="toggleObjectiveTasks(objective.id, $event.target.checked)"
                  />
                  <span class="badge badge-blue">{{ objective.id }}</span>
                  <span class="objective-name">{{ objective.name }}</span>
                  <span class="objective-task-count text-sm text-muted">
                    ({{ getSelectedCountForObjective(objective.id) }}/{{ getObjectiveTasks(objective.id).length }})
                  </span>
                </label>
                <div class="task-checkboxes">
                  <template v-for="task in getObjectiveTasks(objective.id)" :key="task.id">
                    <label class="task-checkbox-label">
                      <input type="checkbox" :value="task.id" :checked="form.taskIds.includes(task.id)" @change="updateTaskSelection(task.id, $event.target.checked)" />
                      <span class="badge badge-gray" style="font-size:11px">{{ task.id }}</span>
                      {{ task.name }}
                    </label>
                    <label v-for="st in (task.sub_tasks || [])" :key="st.id" class="task-checkbox-label sub-task-checkbox-label">
                      <input type="checkbox" :value="st.id" :checked="form.taskIds.includes(st.id)" @change="updateTaskSelection(st.id, $event.target.checked)" />
                      <span class="badge badge-gray" style="font-size:11px">{{ st.id }}</span>
                      {{ st.name }}
                    </label>
                  </template>
                </div>
              </div>
              <div v-if="unlinkedTasks.length > 0" class="objective-group">
                <label class="objective-header objective-select-all">
                  <input type="checkbox" :checked="isUnlinkedAllSelected" v-indeterminate="isUnlinkedPartialSelected" @change="toggleUnlinkedTasks($event.target.checked)" />
                  <span class="badge badge-gray">미연결</span>
                  <span class="objective-name">목표 없음</span>
                  <span class="objective-task-count text-sm text-muted">({{ unlinkedSelectedCount }}/{{ unlinkedTasks.length }})</span>
                </label>
                <div class="task-checkboxes">
                  <template v-for="task in unlinkedTasks" :key="task.id">
                    <label class="task-checkbox-label">
                      <input type="checkbox" :value="task.id" :checked="form.taskIds.includes(task.id)" @change="updateTaskSelection(task.id, $event.target.checked)" />
                      <span class="badge badge-gray" style="font-size:11px">{{ task.id }}</span>
                      {{ task.name }}
                    </label>
                    <label v-for="st in (task.sub_tasks || [])" :key="st.id" class="task-checkbox-label sub-task-checkbox-label">
                      <input type="checkbox" :value="st.id" :checked="form.taskIds.includes(st.id)" @change="updateTaskSelection(st.id, $event.target.checked)" />
                      <span class="badge badge-gray" style="font-size:11px">{{ st.id }}</span>
                      {{ st.name }}
                    </label>
                  </template>
                </div>
              </div>
            </div>
            <div v-if="form.taskIds.length > 0" class="selected-tasks-summary mt-16">
              <div class="text-sm text-muted">선택된 과제: {{ form.taskIds.length }}개</div>
              <div class="flex gap-4" style="flex-wrap:wrap;margin-top:8px">
                <span v-for="taskId in form.taskIds" :key="taskId" class="badge badge-gray">{{ taskId }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="closeModal">취소</button>
          <button class="btn btn-primary" @click="submitForm" :disabled="!form.name.trim() || (!selectedMember && !form.username.trim())">
            {{ selectedMember ? '수정' : '추가' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from '../composables/useToast.js'
import { useModal } from '../composables/useModal.js'

const props = defineProps({ embedded: { type: Boolean, default: false } })
const emit = defineEmits(['updated'])

const vIndeterminate = {
  mounted(el, { value }) { el.indeterminate = value },
  updated(el, { value }) { el.indeterminate = value },
}

const staff = ref([])
const objectives = ref([])
const tasks = ref([])
const loading = ref(false)
const selectedStaffFilter = ref([])
const { show: showModal, open: openModal, close: closeModal } = useModal()
const { toastMsg, showToast, toastError } = useToast()
const debounceTimers = {}

const defaultForm = () => ({ username: '', name: '', job_title: '', main_skills: '', sub_skills: '', taskIds: [] })
const form = ref(defaultForm())
const selectedMember = ref(null)

async function fetchStaff() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/staff')
    staff.value = data
  } finally { loading.value = false }
}

async function fetchObjectives() {
  const { data } = await axios.get('/api/okrs')
  objectives.value = data
}

async function fetchTasks() {
  const { data } = await axios.get('/api/tasks')
  tasks.value = data
}

function toggleStaffFilter(username) {
  const idx = selectedStaffFilter.value.indexOf(username)
  if (idx === -1) selectedStaffFilter.value.push(username)
  else selectedStaffFilter.value.splice(idx, 1)
}

function getObjectiveTasks(objectiveId) {
  return tasks.value.filter(t => t.objective_id === objectiveId)
}

const unlinkedTasks = computed(() => tasks.value.filter(t => !t.objective_id))
const unlinkedSelectedCount = computed(() =>
  unlinkedTasks.value.filter(t => form.value.taskIds.includes(t.id)).length
)
const isUnlinkedAllSelected = computed(() =>
  unlinkedTasks.value.length > 0 && unlinkedTasks.value.every(t => form.value.taskIds.includes(t.id))
)
const isUnlinkedPartialSelected = computed(() => {
  const c = unlinkedSelectedCount.value
  return c > 0 && c < unlinkedTasks.value.length
})
function toggleUnlinkedTasks(sel) { unlinkedTasks.value.forEach(t => updateTaskSelection(t.id, sel)) }

function getObjectiveName(id) {
  return objectives.value.find(o => o.id === id)?.name || id
}

function resolveTaskObjectiveId(id) {
  let t = tasks.value.find(t => t.id === id)
  if (!t) {
    const pid = id.split('-').slice(0, -1).join('-')
    t = tasks.value.find(t => t.id === pid)
  }
  return t?.objective_id || null
}

// task_ids 배열에서 목표 ID 목록 추출
function getTaskIdsObjectiveIds(taskIds) {
  const seen = new Set()
  const result = []
  taskIds.forEach(id => {
    const objId = resolveTaskObjectiveId(id)
    if (objId && !seen.has(objId)) { seen.add(objId); result.push(objId) }
  })
  return result
}

// task_ids 배열에서 특정 목표에 속하는 과제 목록
function getTasksForObjective(taskIds, objId) {
  const selected = new Set(taskIds)
  const result = []
  tasks.value.filter(t => t.objective_id === objId).forEach(t => {
    if (selected.has(t.id)) result.push({ id: t.id, name: t.name, isSub: false })
    ;(t.sub_tasks || []).forEach(st => {
      if (selected.has(st.id)) result.push({ id: st.id, name: st.name, isSub: true })
    })
  })
  return result
}

function getSelectedCountForObjective(objectiveId) {
  return getObjectiveTasks(objectiveId).filter(t => form.value.taskIds.includes(t.id)).length
}
function isObjectiveAllSelected(objectiveId) {
  const ts = getObjectiveTasks(objectiveId)
  return ts.length > 0 && ts.every(t => form.value.taskIds.includes(t.id))
}
function isObjectivePartialSelected(objectiveId) {
  const c = getSelectedCountForObjective(objectiveId)
  return c > 0 && c < getObjectiveTasks(objectiveId).length
}
function toggleObjectiveTasks(objectiveId, sel) {
  getObjectiveTasks(objectiveId).forEach(t => updateTaskSelection(t.id, sel))
}
function updateTaskSelection(id, sel) {
  if (sel) { if (!form.value.taskIds.includes(id)) form.value.taskIds.push(id) }
  else { const i = form.value.taskIds.indexOf(id); if (i > -1) form.value.taskIds.splice(i, 1) }
}

function debounceSave(member, field, value) {
  const key = `${member.username}-${field}`
  clearTimeout(debounceTimers[key])
  debounceTimers[key] = setTimeout(async () => {
    member[field] = value
    try {
      await axios.put(`/api/staff/${member.username}`, { [field]: value })
      showToast('저장됨')
    } catch (e) { toastError(e, '저장 실패') }
  }, 800)
}

function openAddModal() {
  form.value = defaultForm()
  selectedMember.value = null
  openModal()
}

function editMember(member) {
  selectedMember.value = member
  form.value = {
    name: member.name,
    job_title: member.job_title || '',
    main_skills: member.main_skills || '',
    sub_skills: member.sub_skills || '',
    taskIds: [...(member.task_ids || [])],
  }
  openModal()
}

function deriveOkrs(taskIds) {
  return [...new Set(taskIds.map(resolveTaskObjectiveId).filter(Boolean))].join(', ')
}

async function submitForm() {
  const payload = {
    ...form.value,
    okrs: deriveOkrs(form.value.taskIds),
    task_ids: form.value.taskIds,
  }
  try {
    if (selectedMember.value) {
      const { data } = await axios.put(`/api/staff/${selectedMember.value.username}`, payload)
      const idx = staff.value.findIndex(s => s.username === selectedMember.value.username)
      if (idx !== -1) staff.value[idx] = data
      showToast('인력 정보가 수정되었습니다')
    } else {
      const { data } = await axios.post('/api/staff', payload)
      staff.value.push(data)
      showToast('인력이 추가되었습니다 (임시 비밀번호로 계정 생성됨)')
    }
    closeModal()
    emit('updated')
  } catch (e) { toastError(e, selectedMember.value ? '수정 실패' : '추가 실패') }
}

async function deleteMember(member) {
  if (!confirm(`"${member.name}" 계정을 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/staff/${member.username}`)
    staff.value = staff.value.filter(s => s.username !== member.username)
    showToast('삭제되었습니다')
    emit('updated')
  } catch (e) { toastError(e, '삭제 실패') }
}

const sortKey = ref('name')
const sortOrder = ref('asc')

const sortedStaff = computed(() => {
  const filtered = selectedStaffFilter.value.length > 0
    ? staff.value.filter(s => selectedStaffFilter.value.includes(s.username))
    : staff.value
  return [...filtered].sort((a, b) => {
    let aV = a[sortKey.value] || ''
    let bV = b[sortKey.value] || ''
    if (typeof aV === 'string') { aV = aV.toLowerCase(); bV = bV.toLowerCase() }
    const r = aV < bV ? -1 : aV > bV ? 1 : 0
    return sortOrder.value === 'asc' ? r : -r
  })
})

function sortBy(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const totalStaffCount = computed(() => staff.value.length)
const objectiveStats = computed(() => {
  const stats = {}
  staff.value.forEach(m => {
    getTaskIdsObjectiveIds(m.task_ids || []).forEach(id => {
      if (!stats[id]) stats[id] = { count: 0 }
      stats[id].count++
    })
  })
  return stats
})

onMounted(async () => {
  await Promise.all([fetchStaff(), fetchObjectives(), fetchTasks()])
})

defineExpose({ openAddModal })
</script>

<style scoped>
.staff-filter-bar { gap: 6px; }
.filter-label-sm { font-size: 12px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }
.staff-chip {
  display: inline-flex; align-items: center; padding: 3px 10px;
  border-radius: 999px; border: 1px solid var(--outline); font-size: 12px;
  font-family: inherit; cursor: pointer; background: var(--surface); color: var(--text-secondary);
  transition: all 0.15s;
}
.staff-chip:hover { border-color: var(--primary); color: var(--primary); }
.staff-chip-active { background: var(--primary-light); color: var(--primary); border-color: var(--primary); font-weight: 600; }
.objective-task-list { display: flex; flex-direction: column; gap: 8px; }
.objective-item { display: flex; flex-direction: column; gap: 4px; }
.objective-header { display: flex; align-items: center; gap: 8px; }
.task-list { margin-left: 24px; display: flex; flex-direction: column; gap: 2px; margin-top: 2px; }
.task-item { display: flex; align-items: center; gap: 8px; line-height: 1.4; }
.task-name { font-size: 12px; color: var(--text-muted); }
.objective-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); }
.task-group-list { display: flex; flex-direction: column; gap: 16px; max-height: 400px; overflow-y: auto; padding: 8px; }
.objective-group { border: 1px solid var(--outline); border-radius: 6px; padding: 12px; }
.objective-group .objective-header { margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--outline); }
.objective-select-all { display: flex; align-items: center; gap: 8px; cursor: pointer; width: 100%; }
.objective-select-all input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; flex-shrink: 0; }
.objective-task-count { margin-left: auto; }
.objective-name { font-weight: 600; margin-left: 8px; }
.task-checkboxes { display: flex; flex-direction: column; gap: 8px; }
.task-checkbox-label { display: flex; align-items: flex-start; gap: 8px; padding: 6px 10px; background: var(--gray-50); border-radius: 4px; cursor: pointer; font-size: 14px; }
.task-checkbox-label:hover { background: var(--gray-100); }
.task-checkbox-label input { margin-top: 4px; }
.sub-task-checkbox-label { margin-left: 20px; background: transparent; border-left: 2px solid var(--outline); border-radius: 0 4px 4px 0; font-size: 13px; color: var(--text-secondary); }
.sub-task-item { margin-left: 20px; border-left: 2px solid var(--outline); padding-left: 8px; font-size: 12px; color: var(--text-muted); }
</style>

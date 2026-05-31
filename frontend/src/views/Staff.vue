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
      <!-- Summary cards: 독립 페이지에서만 표시 -->
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

      <!-- Filter bar -->
      <div v-if="staff.length > 0" class="filter-bar staff-filter-bar">
        <span class="filter-label-sm">인력</span>
        <button
          v-for="s in staff"
          :key="s.id"
          class="staff-chip"
          :class="{ 'staff-chip-active': selectedStaffFilter.includes(s.id) }"
          @click="toggleStaffFilter(s.id)"
        >{{ s.name }}</button>
        <button v-if="selectedStaffFilter.length > 0" class="btn btn-ghost btn-xs" @click="selectedStaffFilter = []" data-tooltip="인력 필터 초기화">전체 보기</button>
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
                <th @click="sortBy('role')" style="cursor:pointer">
                  역할 <span v-if="sortKey === 'role'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('main_skills')" style="cursor:pointer">
                  주 기술 <span v-if="sortKey === 'main_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('sub_skills')" style="cursor:pointer">
                  부 기술 <span v-if="sortKey === 'sub_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('objectives')" style="cursor:pointer">
                  참여 목표 <span v-if="sortKey === 'objectives'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th style="width:90px"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in sortedStaff" :key="member.id">
                <td style="white-space:nowrap">
                  <div style="font-weight:600">{{ member.name }}</div>
                  <div style="font-size:10px;color:var(--text-muted);margin-top:2px;font-family:monospace">{{ member.id }}</div>
                </td>
                <td>
                  <input
                    class="form-control inline"
                    :value="member.role"
                    @input="debounceSave(member, 'role', $event.target.value)"
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
                    <template v-if="member.selected_tasks">
                      <div v-for="objId in getSelectedTaskObjectiveIds(member)" :key="objId" class="objective-item">
                        <div class="objective-header">
                          <span class="badge badge-blue">{{ objId }}</span>
                          <span class="objective-label">{{ getObjectiveName(objId) }}</span>
                        </div>
                        <div class="task-list">
                          <div
                            v-for="task in getSelectedTasksForObjective(member, objId)"
                            :key="task.id"
                            class="task-item"
                            :class="{ 'sub-task-item': task.isSub }"
                          >
                            <span class="badge badge-gray">{{ task.id }}</span>
                            <span class="task-name">{{ task.name }}</span>
                          </div>
                        </div>
                      </div>
                    </template>
                    <template v-else>
                      <div v-for="objId in getObjectiveIds(member.objectives || member.okrs)" :key="objId" class="objective-item">
                        <div class="objective-header">
                          <span class="badge badge-blue">{{ objId }}</span>
                          <span class="objective-label">{{ getObjectiveName(objId) }}</span>
                        </div>
                        <div v-if="getObjectiveTasks(objId).length > 0" class="task-list">
                          <div v-for="task in getObjectiveTasks(objId)" :key="task.id" class="task-item">
                            <span class="badge badge-gray">{{ task.id }}</span>
                            <span class="task-name">{{ task.name }}</span>
                          </div>
                        </div>
                      </div>
                    </template>
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

    <!-- Add Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedMember ? '인력 수정' : '인력 추가' }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">이름 *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">역할</label>
            <input v-model="form.role" class="form-control" />
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
                      <input
                        type="checkbox"
                        :value="task.id"
                        :checked="form.taskIds.includes(task.id)"
                        @change="updateTaskSelection(task.id, $event.target.checked)"
                      />
                      <span class="badge badge-gray" style="font-size:11px">{{ task.id }}</span>
                      {{ task.name }}
                    </label>
                    <label
                      v-for="st in (task.sub_tasks || [])"
                      :key="st.id"
                      class="task-checkbox-label sub-task-checkbox-label"
                    >
                      <input
                        type="checkbox"
                        :value="st.id"
                        :checked="form.taskIds.includes(st.id)"
                        @change="updateTaskSelection(st.id, $event.target.checked)"
                      />
                      <span class="badge badge-gray" style="font-size:11px">{{ st.id }}</span>
                      {{ st.name }}
                      <span v-if="st.done" class="text-muted text-sm">(완료)</span>
                    </label>
                  </template>
                </div>
              </div>
              <!-- 목표 미연결 과제 -->
              <div v-if="unlinkedTasks.length > 0" class="objective-group">
                <label class="objective-header objective-select-all">
                  <input
                    type="checkbox"
                    :checked="isUnlinkedAllSelected"
                    v-indeterminate="isUnlinkedPartialSelected"
                    @change="toggleUnlinkedTasks($event.target.checked)"
                  />
                  <span class="badge badge-gray">미연결</span>
                  <span class="objective-name">목표 없음</span>
                  <span class="objective-task-count text-sm text-muted">
                    ({{ unlinkedSelectedCount }}/{{ unlinkedTasks.length }})
                  </span>
                </label>
                <div class="task-checkboxes">
                  <template v-for="task in unlinkedTasks" :key="task.id">
                    <label class="task-checkbox-label">
                      <input
                        type="checkbox"
                        :value="task.id"
                        :checked="form.taskIds.includes(task.id)"
                        @change="updateTaskSelection(task.id, $event.target.checked)"
                      />
                      <span class="badge badge-gray" style="font-size:11px">{{ task.id }}</span>
                      {{ task.name }}
                    </label>
                    <label
                      v-for="st in (task.sub_tasks || [])"
                      :key="st.id"
                      class="task-checkbox-label sub-task-checkbox-label"
                    >
                      <input
                        type="checkbox"
                        :value="st.id"
                        :checked="form.taskIds.includes(st.id)"
                        @change="updateTaskSelection(st.id, $event.target.checked)"
                      />
                      <span class="badge badge-gray" style="font-size:11px">{{ st.id }}</span>
                      {{ st.name }}
                    </label>
                  </template>
                </div>
              </div>
            </div>
            <!-- 선택된 과제 요약 -->
            <div v-if="form.taskIds.length > 0" class="selected-tasks-summary mt-16">
              <div class="text-sm text-muted">선택된 과제: {{ form.taskIds.length }}개</div>
              <div class="flex gap-4" style="flex-wrap:wrap;margin-top:8px">
                <span v-for="taskId in form.taskIds" :key="taskId" class="badge badge-gray">
                  {{ taskId }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="closeModal">취소</button>
          <button class="btn btn-primary" @click="submitForm" :disabled="!form.name.trim()">
            {{ selectedMember ? '수정' : '추가' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Objective Select Modal -->
    <div v-if="showObjectiveModal" class="modal-overlay" @click.self="closeObjectiveModal">
      <div class="modal">
        <div class="modal-header">
          <h3>참여 목표 선택 - {{ selectedMember?.name }}</h3>
          <button class="modal-close" @click="closeObjectiveModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="flex gap-8" style="flex-wrap:wrap">
            <label v-for="o in objectives" :key="o.id" class="checkbox-label">
              <input type="checkbox" :value="o.id" v-model="selectedObjectiveIds" />
              {{ o.id }}: {{ o.name }}
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="closeObjectiveModal">취소</button>
          <button class="btn btn-primary" @click="saveObjectives">저장</button>
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
import { parseIds } from '../utils/parseIds.js'

const props = defineProps({
  embedded: { type: Boolean, default: false }
})
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
const { show: showObjectiveModal, open: openObjectiveModal, close: closeObjectiveModal } = useModal()
const { toastMsg, showToast, toastError } = useToast()
const debounceTimers = {}

const defaultForm = () => ({ name: '', role: '', main_skills: '', sub_skills: '', taskIds: [] })
const form = ref(defaultForm())

const selectedMember = ref(null)
const selectedObjectiveIds = ref([])

// Objective 내 선택된 Task 수
function getSelectedCountForObjective(objectiveId) {
  return getObjectiveTasks(objectiveId).filter(t => form.value.taskIds.includes(t.id)).length
}

// Objective 내 Task 전체 선택 여부
function isObjectiveAllSelected(objectiveId) {
  const objTasks = getObjectiveTasks(objectiveId)
  return objTasks.length > 0 && objTasks.every(t => form.value.taskIds.includes(t.id))
}

// Objective 내 Task 일부 선택 여부 (indeterminate)
function isObjectivePartialSelected(objectiveId) {
  const count = getSelectedCountForObjective(objectiveId)
  const total = getObjectiveTasks(objectiveId).length
  return count > 0 && count < total
}

// Objective 내 Task 일괄 선택/해제
function toggleObjectiveTasks(objectiveId, isSelected) {
  getObjectiveTasks(objectiveId).forEach(task => updateTaskSelection(task.id, isSelected))
}

// 과제 선택 관련 함수 추가
function updateTaskSelection(taskId, isSelected) {
  if (isSelected) {
    // 과제가 선택되었을 때
    if (!form.value.taskIds.includes(taskId)) {
      form.value.taskIds.push(taskId)
    }
  } else {
    // 과제가 선택 해제되었을 때
    const index = form.value.taskIds.indexOf(taskId)
    if (index > -1) {
      form.value.taskIds.splice(index, 1)
    }
  }
}


const getTaskIds = parseIds
const getObjectiveIds = parseIds

async function fetchStaff() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/staff')
    staff.value = data
  } finally {
    loading.value = false
  }
}

function toggleStaffFilter(staffId) {
  const idx = selectedStaffFilter.value.indexOf(staffId)
  if (idx === -1) selectedStaffFilter.value.push(staffId)
  else selectedStaffFilter.value.splice(idx, 1)
}

async function fetchObjectives() {
  const { data } = await axios.get('/api/okrs')
  objectives.value = data
}

async function fetchTasks() {
  const { data } = await axios.get('/api/tasks')
  tasks.value = data
}

// Objective별 관련 과제 가져오기
function getObjectiveTasks(objectiveId) {
  return tasks.value.filter(task => task.objective_id === objectiveId)
}

// 목표 미연결 과제
const unlinkedTasks = computed(() =>
  tasks.value.filter(t => !t.objective_id)
)
const unlinkedSelectedCount = computed(() =>
  unlinkedTasks.value.filter(t => form.value.taskIds.includes(t.id)).length
)
const isUnlinkedAllSelected = computed(() =>
  unlinkedTasks.value.length > 0 && unlinkedTasks.value.every(t => form.value.taskIds.includes(t.id))
)
const isUnlinkedPartialSelected = computed(() => {
  const count = unlinkedSelectedCount.value
  return count > 0 && count < unlinkedTasks.value.length
})
function toggleUnlinkedTasks(isSelected) {
  unlinkedTasks.value.forEach(t => updateTaskSelection(t.id, isSelected))
}

// Objective ID로 Objective명 가져오기
function getObjectiveName(objectiveId) {
  const objective = objectives.value.find(obj => obj.id === objectiveId)
  return objective ? objective.name : objectiveId
}

// 과제 ID로 과제명 가져오기
function getTaskName(taskId) {
  const task = tasks.value.find(t => t.id === taskId)
  return task ? task.name : taskId
}

function debounceSave(member, field, value) {
  const key = `${member.id}-${field}`
  clearTimeout(debounceTimers[key])
  debounceTimers[key] = setTimeout(async () => {
    member[field] = value
    try {
      await axios.put(`/api/staff/${member.id}`, { [field]: value })
      showToast('저장됨')
    } catch (e) { toastError(e, '저장 실패') }
  }, 800)
}

function openAddModal() {
  form.value = defaultForm()
  selectedMember.value = null
  openModal()
}

async function submitForm() {
  if (selectedMember.value) {
    // 수정 모드
    await submitEdit()
  } else {
    // 추가 모드
    await submitAdd()
  }
}

function deriveObjectiveIds(taskIds) {
  return [...new Set(taskIds.map(resolveTaskObjectiveId).filter(Boolean))]
}

async function submitAdd() {
  try {
    const payload = {
      ...form.value,
      okrs: deriveObjectiveIds(form.value.taskIds).join(', '),
      selected_tasks: form.value.taskIds.join(', '),
    }
    const { data } = await axios.post('/api/staff', payload)
    staff.value.push(data)
    closeModal()
    showToast('인력이 추가되었습니다')
    emit('updated')
  } catch (e) { toastError(e, '인력 추가 실패') }
}

async function submitEdit() {
  if (!selectedMember.value) return

  try {
    const payload = {
      ...form.value,
      okrs: deriveObjectiveIds(form.value.taskIds).join(', '),
      selected_tasks: form.value.taskIds.join(', '),
    }
    const { data } = await axios.put(`/api/staff/${selectedMember.value.id}`, payload)
    
    // staff 배열 업데이트
    const index = staff.value.findIndex(s => s.id === selectedMember.value.id)
    if (index !== -1) {
      staff.value[index] = data
    }
    
    closeModal()
    showToast('인력 정보가 수정되었습니다')
    emit('updated')
  } catch (e) { toastError(e, '인력 수정 실패') }
}

function openObjectiveSelect(member) {
  selectedMember.value = member
  selectedObjectiveIds.value = getObjectiveIds(member.objectives || member.okrs || '')
  openObjectiveModal()
}

async function saveObjectives() {
  if (!selectedMember.value) return
  const objectivesStr = selectedObjectiveIds.value.join(', ')
  try {
    // 백엔드는 okrs 필드를 기대하므로 필드명 변경
    await axios.put(`/api/staff/${selectedMember.value.id}`, { okrs: objectivesStr })
    
    // selectedMember 업데이트
    selectedMember.value.objectives = objectivesStr
    
    // staff.value 배열의 해당 멤버도 업데이트
    const index = staff.value.findIndex(s => s.id === selectedMember.value.id)
    if (index !== -1) {
      staff.value[index].objectives = objectivesStr
      // staff.value[index].okrs = objectivesStr  // 백엔드와 호환
    }
    
    closeObjectiveModal()
    showToast('저장됨')
  } catch (e) { toastError(e, '저장 실패') }
}

// 정렬 기능
const sortKey = ref('name')
const sortOrder = ref('asc')

const sortedStaff = computed(() => {
  const filtered = selectedStaffFilter.value.length > 0
    ? staff.value.filter(s => selectedStaffFilter.value.includes(s.id))
    : staff.value

  if (!sortKey.value) return filtered

  return [...filtered].sort((a, b) => {
    let aVal = a[sortKey.value]
    let bVal = b[sortKey.value]
    
    // objectives의 경우 ID 개수로 정렬 (okrs 필드도 지원)
    if (sortKey.value === 'objectives') {
      const aObjectives = a.objectives || a.okrs || '';
      const bObjectives = b.objectives || b.okrs || '';
      aVal = getObjectiveIds(aObjectives).length
      bVal = getObjectiveIds(bObjectives).length
    }
    
    // 문자열 비교
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    let result = 0
    if (aVal < bVal) result = -1
    else if (aVal > bVal) result = 1
    
    return sortOrder.value === 'asc' ? result : -result
  })
})

function sortBy(key) {
  if (sortKey.value === key) {
    if (sortOrder.value === 'asc') {
      sortOrder.value = 'desc'
    } else {
      sortKey.value = ''
      sortOrder.value = 'asc'
    }
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

// 수정 기능
// 과제 ID들로 초기화하는 함수
function getTaskIdsFromObjectives(objectivesStr) {
  const objIds = getObjectiveIds(objectivesStr)
  const taskIds = []
  tasks.value.forEach(task => {
    if (objIds.includes(task.objective_id)) {
      taskIds.push(task.id)
    }
  })
  return taskIds
}

// 과제 ID(소과제 포함)에서 부모 과제를 찾아 Objective ID 반환
function resolveTaskObjectiveId(id) {
  let task = tasks.value.find(t => t.id === id)
  if (!task) {
    const parentId = id.split('-').slice(0, -1).join('-')
    task = tasks.value.find(t => t.id === parentId)
  }
  return task ? task.objective_id : null
}

// selected_tasks의 Objective ID들 반환
function getSelectedTaskObjectiveIds(member) {
  const seen = new Set()
  const objIds = []
  getTaskIds(member.selected_tasks).forEach(id => {
    const objId = resolveTaskObjectiveId(id)
    if (objId && !seen.has(objId)) { seen.add(objId); objIds.push(objId) }
  })
  return objIds.filter(Boolean)
}

// selected_tasks 중 특정 Objective에 속하는 과제/소과제 반환
function getSelectedTasksForObjective(member, objId) {
  const selectedIds = new Set(getTaskIds(member.selected_tasks))
  const result = []
  tasks.value.filter(t => t.objective_id === objId).forEach(t => {
    if (selectedIds.has(t.id)) result.push({ id: t.id, name: t.name, isSub: false })
    ;(t.sub_tasks || []).forEach(st => {
      if (selectedIds.has(st.id)) result.push({ id: st.id, name: st.name, isSub: true })
    })
  })
  return result
}

function editMember(member) {
  selectedMember.value = member
  form.value = {
    name: member.name,
    role: member.role || '',
    main_skills: member.main_skills || '',
    sub_skills: member.sub_skills || '',
    taskIds: member.selected_tasks ? getTaskIds(member.selected_tasks) : []
  }
  openModal()
}

// 집계 기능
const totalStaffCount = computed(() => staff.value.length)

const objectiveStats = computed(() => {
  const stats = {}
  staff.value.forEach(member => {
    const objIds = getObjectiveIds(member.objectives || member.okrs || '')
    objIds.forEach(objId => {
      if (!stats[objId]) {
        stats[objId] = { count: 0 }
      }
      stats[objId].count++
    })
  })
  return stats
})

async function deleteMember(member) {
  if (!confirm(`"${member.name}"을(를) 삭제하시겠습니까?`)) return
  await axios.delete(`/api/staff/${member.id}`)
  staff.value = staff.value.filter(s => s.id !== member.id)
  showToast('삭제되었습니다')
  emit('updated')
}

onMounted(async () => {
  await Promise.all([fetchStaff(), fetchObjectives(), fetchTasks()])
})

defineExpose({ openAddModal })
</script>

<style scoped>
.staff-filter-bar { gap: 6px; }

.filter-label-sm {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.staff-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--outline);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  background: var(--surface);
  color: var(--text-secondary);
  transition: all 0.15s;
}
.staff-chip:hover { border-color: var(--primary); color: var(--primary); }
.staff-chip-active { background: var(--primary-light); color: var(--primary); border-color: var(--primary); font-weight: 600; }

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--gray-50);
  border-radius: 4px;
  cursor: pointer;
}
.checkbox-label input {
  margin: 0;
}

.objective-task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.objective-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.objective-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-list {
  margin-left: 24px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 2px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.4;
}

.task-name {
  font-size: 12px;
  color: var(--text-muted);
}

.objective-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #555);
}

/* 과제 그룹 스타일 */
.task-group-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.objective-group {
  border: 1px solid var(--outline);
  border-radius: 6px;
  padding: 12px;
}

.objective-group .objective-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--outline);
}

.objective-select-all {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  width: 100%;
}

.objective-select-all input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  flex-shrink: 0;
}

.objective-task-count {
  margin-left: auto;
}

.objective-name {
  font-weight: 600;
  margin-left: 8px;
}

.task-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 10px;
  background: var(--gray-50);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.task-checkbox-label:hover {
  background: var(--gray-100);
}

.task-checkbox-label input {
  margin-top: 4px;
}

.sub-task-checkbox-label {
  margin-left: 20px;
  background: transparent;
  border-left: 2px solid var(--outline);
  border-radius: 0 4px 4px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.sub-task-item {
  margin-left: 20px;
  border-left: 2px solid var(--outline);
  padding-left: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
</style>

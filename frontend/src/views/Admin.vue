<template>
  <div>
    <div class="page-header">
      <div>
        <h2>관리 도구</h2>
        <div class="subtitle">Objective · Key Result · 과제 · 인력 관리</div>
      </div>
    </div>

    <div class="page-body">
      <div class="tabs">
        <button v-for="t in tabs" :key="t.key" class="tab" :class="{ active: activeTab === t.key }" @click="activeTab = t.key">
          {{ t.label }}
        </button>
      </div>

      <!-- ── Objective Tab ── -->
      <div v-if="activeTab === 'objective'">
        <div class="flex-between" style="margin-bottom:16px">
          <button class="btn btn-ghost btn-sm" @click="exportCsv('objectives')">⬇ CSV 다운로드</button>
          <button class="btn btn-primary btn-sm" @click="openObjectiveModal()">+ Objective 추가</button>
        </div>
        <div class="card">
          <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
          <div v-else-if="objectives.length === 0" class="empty-state">
            <div class="empty-icon">📊</div><p>등록된 Objective가 없습니다.</p>
          </div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Objective명</th><th>기술 스택</th>
                  <th>Key Results</th><th>상태</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in objectives" :key="o.id">
                  <td><span class="badge badge-blue">{{ o.id }}</span></td>
                  <td style="font-weight:600">{{ o.name }}</td>
                  <td><span class="text-sm">{{ o.tech_stack }}</span></td>
                  <td>
                    <div class="flex gap-4" style="align-items:center">
                      <span class="text-sm">{{ o.key_results?.length || 0 }}개</span>
                      <button class="btn btn-ghost btn-xs" @click="openKeyResultModal(o)">+ KR</button>
                    </div>
                  </td>
                  <td><span :class="sBadge(o.status)">{{ o.status }}</span></td>
                  <td>
                    <div class="flex gap-8">
                      <button class="btn btn-ghost btn-xs" @click="openObjectiveModal(o)">수정</button>
                      <button class="btn btn-danger btn-xs" @click="deleteObjective(o)">삭제</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ── Task Tab ── -->
      <div v-if="activeTab === 'task'">
        <div class="flex-between" style="margin-bottom:16px">
          <button class="btn btn-ghost btn-sm" @click="exportCsv('tasks')">⬇ CSV 다운로드</button>
          <button class="btn btn-primary btn-sm" @click="openTaskModal()">+ 과제 추가</button>
        </div>
        <div class="card">
          <div v-if="taskLoading" class="loading-center"><div class="spinner"></div></div>
          <div v-else-if="tasks.length === 0" class="empty-state">
            <div class="empty-icon">📋</div><p>등록된 과제가 없습니다.</p>
          </div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>과제명</th><th>Objective</th><th>참여 인력</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in tasks" :key="t.id">
                  <td><span class="badge badge-blue">{{ t.id }}</span></td>
                  <td style="font-weight:600">{{ t.name }}</td>
                  <td><span class="text-sm">{{ getObjectiveName(t.objective_id) }}</span></td>
                  <td>
                    <span class="text-sm">{{ t.members?.length || 0 }}명</span>
                    <button class="btn btn-ghost btn-xs" @click="openTaskMemberModal(t)" style="margin-left:4px">인력</button>
                  </td>
                  <td>
                    <div class="flex gap-8">
                      <button class="btn btn-ghost btn-xs" @click="openTaskModal(t)">수정</button>
                      <button class="btn btn-danger btn-xs" @click="deleteTask(t)">삭제</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ── Staff Tab ── -->
      <div v-if="activeTab === 'staff'">
        <div class="flex-between" style="margin-bottom:16px">
          <button class="btn btn-ghost btn-sm" @click="exportCsv('staff')">⬇ CSV 다운로드</button>
          <button class="btn btn-primary btn-sm" @click="openStaffModal()">+ 인력 추가</button>
        </div>
        <div class="card">
          <div v-if="staffLoading" class="loading-center"><div class="spinner"></div></div>
          <div v-else-if="staffList.length === 0" class="empty-state">
            <div class="empty-icon">👥</div><p>등록된 인력이 없습니다.</p>
          </div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr><th>이름</th><th>역할</th><th>주 기술</th><th>부 기술</th><th>참여 Objective</th><th></th></tr>
              </thead>
              <tbody>
                <tr v-for="s in staffList" :key="s.id">
                  <td style="font-weight:600">{{ s.name }}</td>
                  <td>{{ s.role }}</td>
                  <td>{{ s.main_skills }}</td>
                  <td>{{ s.sub_skills }}</td>
                  <td>{{ s.objectives }}</td>
                  <td>
                    <div class="flex gap-8">
                      <button class="btn btn-ghost btn-xs" @click="openStaffModal(s)">수정</button>
                      <button class="btn btn-danger btn-xs" @click="deleteStaff(s)">삭제</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ── Reset Tab ── -->
      <div v-if="activeTab === 'reset'">
        <div class="card card-body">
          <h3 style="margin-bottom:16px;color:var(--danger)">⚠️ 데이터 초기화</h3>
          <p class="text-muted text-sm" style="margin-bottom:20px">삭제된 데이터는 복구할 수 없습니다.</p>
          <div class="flex gap-8" style="flex-wrap:wrap">
            <button class="btn btn-danger btn-sm" @click="resetData('objectives')">Objective 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('tasks')">과제 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('staff')">인력 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('progress')">진행도 전체 삭제</button>
            <button class="btn btn-danger" @click="resetData('all')">⚠️ 모든 데이터 삭제</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Objective Modal -->
    <div v-if="showObjectiveModal" class="modal-overlay" @click.self="showObjectiveModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingObjectiveId ? 'Objective 수정' : 'Objective 추가' }}</h3>
          <button class="modal-close" @click="showObjectiveModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Objective ID</label>
            <input v-model="objectiveForm.id" class="form-control" :placeholder="nextObjectiveId" disabled />
            <span class="text-sm text-muted">자동 생성</span>
          </div>
          <div class="form-group">
            <label class="form-label">Objective명 *</label>
            <input v-model="objectiveForm.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">기술 스택</label>
            <input v-model="objectiveForm.tech_stack" class="form-control" placeholder="Python, PyTorch, ..." />
          </div>
          <div class="form-group">
            <label class="form-label">상태</label>
            <select v-model="objectiveForm.status" class="form-control">
              <option>진행중</option><option>완료</option><option>위험</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showObjectiveModal = false">취소</button>
          <button class="btn btn-primary" @click="submitObjective" :disabled="!objectiveForm.name">저장</button>
        </div>
      </div>
    </div>

    <!-- Key Result Modal -->
    <div v-if="showKeyResultModal" class="modal-overlay" @click.self="showKeyResultModal = false">
      <div class="modal" style="max-width:640px">
        <div class="modal-header">
          <h3>Key Results - {{ selectedObjective?.id }}: {{ selectedObjective?.name }}</h3>
          <button class="modal-close" @click="showKeyResultModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedObjective?.key_results?.length > 0" style="margin-bottom:16px">
            <div class="text-sm text-muted" style="margin-bottom:8px">등록된 Key Results:</div>
            <div v-for="kr in selectedObjective.key_results" :key="kr.id" class="kr-edit-item">
              <div class="flex gap-8" style="align-items:center">
                <span class="badge badge-blue" style="width:50px">{{ kr.id }}</span>
                <input v-model="kr.name" class="form-control" placeholder="Key Result 내용" style="flex:1" />
                <button class="btn btn-danger btn-xs" @click="deleteKeyResult(kr.id)">✕</button>
              </div>
            </div>
          </div>
          <div class="text-sm text-muted" style="margin-bottom:8px">새 Key Result 추가:</div>
          <div class="flex gap-8" style="align-items:center">
            <input v-model="newKeyResultName" class="form-control" placeholder="Key Result 내용" style="flex:1" />
            <button class="btn btn-primary btn-xs" @click="addKeyResult" :disabled="!newKeyResultName">추가</button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showKeyResultModal = false">닫기</button>
        </div>
      </div>
    </div>

    <!-- Task Modal -->
    <div v-if="showTaskModal" class="modal-overlay" @click.self="showTaskModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingTaskId ? '과제 수정' : '과제 추가' }}</h3>
          <button class="modal-close" @click="showTaskModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">과제 ID</label>
            <input v-model="taskForm.id" class="form-control" :placeholder="nextTaskId" disabled />
            <span class="text-sm text-muted">자동 생성</span>
          </div>
          <div class="form-group">
            <label class="form-label">과제명 *</label>
            <input v-model="taskForm.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">연결 Objective</label>
            <select v-model="taskForm.objective_id" class="form-control">
              <option value="">없음</option>
              <option v-for="o in objectives" :key="o.id" :value="o.id">{{ o.id }}: {{ o.name }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showTaskModal = false">취소</button>
          <button class="btn btn-primary" @click="submitTask" :disabled="!taskForm.name">저장</button>
        </div>
      </div>
    </div>

    <!-- Task Member Modal -->
    <div v-if="showTaskMemberModal" class="modal-overlay" @click.self="showTaskMemberModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>인력 연결 - {{ selectedTask?.name }}</h3>
          <button class="modal-close" @click="showTaskMemberModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedTask?.members?.length > 0" style="margin-bottom:16px">
            <div class="text-sm text-muted" style="margin-bottom:8px">연결된 인력:</div>
            <div v-for="m in selectedTask.members" :key="m.staff_id" class="kr-edit-item">
              <div class="flex gap-8" style="align-items:center">
                <span>{{ m.name }}</span>
                <button class="btn btn-danger btn-xs" @click="removeTaskMember(m.staff_id)">✕</button>
              </div>
            </div>
          </div>
          <div class="text-sm text-muted" style="margin-bottom:8px">인력 추가:</div>
          <select v-model="selectedStaffId" class="form-control" style="margin-bottom:8px">
            <option value="">선택</option>
            <option v-for="s in availableStaff" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <button class="btn btn-primary btn-sm" @click="addTaskMember" :disabled="!selectedStaffId">추가</button>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showTaskMemberModal = false">닫기</button>
        </div>
      </div>
    </div>

    <!-- Staff Modal -->
    <div v-if="showStaffModal" class="modal-overlay" @click.self="showStaffModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingStaffId ? '인력 수정' : '인력 추가' }}</h3>
          <button class="modal-close" @click="showStaffModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">이름 *</label>
            <input v-model="staffForm.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">직책/역할</label>
            <input v-model="staffForm.role" class="form-control" />
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">주 기술</label>
              <input v-model="staffForm.main_skills" class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">부 기술</label>
              <input v-model="staffForm.sub_skills" class="form-control" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">참여 Objective</label>
            <div class="flex gap-8" style="flex-wrap:wrap">
              <label v-for="o in objectives" :key="o.id" class="checkbox-label">
                <input type="checkbox" :value="o.id" v-model="staffForm.objectiveIds" />
                {{ o.id }}
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showStaffModal = false">취소</button>
          <button class="btn btn-primary" @click="submitStaff" :disabled="!staffForm.name">저장</button>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const tabs = [
  { key: 'objective', label: '📊 Objective' },
  { key: 'task', label: '📋 과제' },
  { key: 'staff', label: '👥 인력' },
  { key: 'reset', label: '🗑 초기화' },
]
const activeTab = ref('objective')

const objectives = ref([])
const tasks = ref([])
const staffList = ref([])
const loading = ref(false)
const taskLoading = ref(false)
const staffLoading = ref(false)
const toastMsg = ref('')

const nextObjectiveId = ref('O1')
const nextTaskId = ref('T1')

// Objective
const showObjectiveModal = ref(false)
const editingObjectiveId = ref(null)
const defaultObjectiveForm = () => ({ id: '', name: '', tech_stack: '', status: '진행중' })
const objectiveForm = ref(defaultObjectiveForm())

// Key Result
const showKeyResultModal = ref(false)
const selectedObjective = ref(null)
const newKeyResultName = ref('')

// Task
const showTaskModal = ref(false)
const editingTaskId = ref(null)
const defaultTaskForm = () => ({ id: '', name: '', objective_id: '' })
const taskForm = ref(defaultTaskForm())

// Task Member
const showTaskMemberModal = ref(false)
const selectedTask = ref(null)
const selectedStaffId = ref('')

// Staff
const showStaffModal = ref(false)
const editingStaffId = ref(null)
const defaultStaffForm = () => ({ name: '', role: '', main_skills: '', sub_skills: '', objectiveIds: [] })
const staffForm = ref(defaultStaffForm())

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2500)
}

function sBadge(s) {
  return { '진행중': 'badge badge-blue', '완료': 'badge badge-green', '위험': 'badge badge-red' }[s] || 'badge badge-gray'
}

function getObjectiveName(id) {
  if (!id) return '-'
  const o = objectives.value.find(obj => obj.id === id)
  return o ? `${o.id}: ${o.name}` : id
}

const availableStaff = computed(() => {
  if (!selectedTask.value) return []
  const memberIds = selectedTask.value.members?.map(m => m.staff_id) || []
  return staffList.value.filter(s => !memberIds.includes(s.id))
})

// ── Objective ──
async function fetchObjectives() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/okrs')
    objectives.value = data
    // Get next ID
    const { data: nextId } = await axios.get('/api/okrs/next-id')
    nextObjectiveId.value = nextId.next_id
  } finally { loading.value = false }
}

function openObjectiveModal(o = null) {
  if (o) {
    objectiveForm.value = { ...o }
    editingObjectiveId.value = o.id
  } else {
    objectiveForm.value = { ...defaultObjectiveForm(), id: nextObjectiveId.value }
    editingObjectiveId.value = null
  }
  showObjectiveModal.value = true
}

async function submitObjective() {
  try {
    if (editingObjectiveId.value) {
      const { data } = await axios.put(`/api/okrs/${editingObjectiveId.value}`, objectiveForm.value)
      const idx = objectives.value.findIndex(o => o.id === editingObjectiveId.value)
      if (idx !== -1) objectives.value[idx] = data
    } else {
      const { data } = await axios.post('/api/okrs', objectiveForm.value)
      objectives.value.push(data)
      nextObjectiveId.value = `O${objectives.value.length + 1}`
    }
    showObjectiveModal.value = false
    showToast('저장되었습니다')
  } catch (e) {
    showToast(e.response?.data?.detail || '저장 실패')
  }
}

async function deleteObjective(o) {
  if (!confirm(`"${o.id}: ${o.name}"을(를) 삭제하시겠습니까?`)) return
  await axios.delete(`/api/okrs/${o.id}`)
  objectives.value = objectives.value.filter(x => x.id !== o.id)
  showToast('삭제되었습니다')
}

// ── Key Results ──
function openKeyResultModal(o) {
  selectedObjective.value = JSON.parse(JSON.stringify(o))
  newKeyResultName.value = ''
  showKeyResultModal.value = true
}

async function addKeyResult() {
  if (!newKeyResultName.value) return
  try {
    const { data } = await axios.post(`/api/okrs/${selectedObjective.value.id}/key-results`, {
      name: newKeyResultName.value
    })
    selectedObjective.value.key_results.push(data)
    newKeyResultName.value = ''
    await fetchObjectives()
    const updated = objectives.value.find(o => o.id === selectedObjective.value.id)
    if (updated) selectedObjective.value = JSON.parse(JSON.stringify(updated))
    showToast('Key Result가 추가되었습니다')
  } catch (e) {
    showToast(e.response?.data?.detail || '추가 실패')
  }
}

async function deleteKeyResult(krId) {
  try {
    await axios.delete(`/api/okrs/${selectedObjective.value.id}/key-results/${krId}`)
    selectedObjective.value.key_results = selectedObjective.value.key_results.filter(kr => kr.id !== krId)
    await fetchObjectives()
    showToast('삭제되었습니다')
  } catch (e) {
    showToast('삭제 실패')
  }
}

// ── Tasks ──
async function fetchTasks() {
  taskLoading.value = true
  try {
    const { data } = await axios.get('/api/tasks')
    tasks.value = data
    const { data: nextId } = await axios.get('/api/tasks/next-id')
    nextTaskId.value = nextId.next_id
  } finally { taskLoading.value = false }
}

function openTaskModal(t = null) {
  if (t) {
    taskForm.value = { ...t }
    editingTaskId.value = t.id
  } else {
    taskForm.value = { ...defaultTaskForm(), id: nextTaskId.value }
    editingTaskId.value = null
  }
  showTaskModal.value = true
}

async function submitTask() {
  try {
    if (editingTaskId.value) {
      const { data } = await axios.put(`/api/tasks/${editingTaskId.value}`, taskForm.value)
      const idx = tasks.value.findIndex(t => t.id === editingTaskId.value)
      if (idx !== -1) tasks.value[idx] = data
    } else {
      const { data } = await axios.post('/api/tasks', taskForm.value)
      tasks.value.push(data)
      nextTaskId.value = `T${tasks.value.length + 1}`
    }
    showTaskModal.value = false
    showToast('저장되었습니다')
  } catch (e) {
    showToast(e.response?.data?.detail || '저장 실패')
  }
}

async function deleteTask(t) {
  if (!confirm(`"${t.name}"을(를) 삭제하시겠습니까?`)) return
  await axios.delete(`/api/tasks/${t.id}`)
  tasks.value = tasks.value.filter(x => x.id !== t.id)
  showToast('삭제되었습니다')
}

// ── Task Members ──
function openTaskMemberModal(t) {
  selectedTask.value = JSON.parse(JSON.stringify(t))
  selectedStaffId.value = ''
  showTaskMemberModal.value = true
}

async function addTaskMember() {
  if (!selectedStaffId.value) return
  const staff = staffList.value.find(s => s.id === selectedStaffId.value)
  if (!staff) return
  
  selectedTask.value.members = selectedTask.value.members || []
  selectedTask.value.members.push({ staff_id: staff.id, name: staff.name })
  
  try {
    await axios.put(`/api/tasks/${selectedTask.value.id}`, { members: selectedTask.value.members })
    await fetchTasks()
    const updated = tasks.value.find(t => t.id === selectedTask.value.id)
    if (updated) selectedTask.value = JSON.parse(JSON.stringify(updated))
    selectedStaffId.value = ''
    showToast('인력이 추가되었습니다')
  } catch (e) {
    showToast('추가 실패')
  }
}

async function removeTaskMember(staffId) {
  selectedTask.value.members = selectedTask.value.members.filter(m => m.staff_id !== staffId)
  try {
    await axios.put(`/api/tasks/${selectedTask.value.id}`, { members: selectedTask.value.members })
    await fetchTasks()
    showToast('삭제되었습니다')
  } catch (e) {
    showToast('삭제 실패')
  }
}

// ── Staff ──
async function fetchStaff() {
  staffLoading.value = true
  try { const { data } = await axios.get('/api/staff'); staffList.value = data }
  finally { staffLoading.value = false }
}

function openStaffModal(s = null) {
  if (s) {
    staffForm.value = { 
      name: s.name, 
      role: s.role || '', 
      main_skills: s.main_skills || '', 
      sub_skills: s.sub_skills || '',
      objectiveIds: (s.objectives || '').split(',').map(id => id.trim()).filter(Boolean)
    }
    editingStaffId.value = s.id
  } else {
    staffForm.value = defaultStaffForm()
    editingStaffId.value = null
  }
  showStaffModal.value = true
}

async function submitStaff() {
  try {
    const payload = {
      ...staffForm.value,
      objectives: staffForm.value.objectiveIds.join(', ')
    }
    if (editingStaffId.value) {
      const { data } = await axios.put(`/api/staff/${editingStaffId.value}`, payload)
      const idx = staffList.value.findIndex(s => s.id === editingStaffId.value)
      if (idx !== -1) staffList.value[idx] = data
    } else {
      const { data } = await axios.post('/api/staff', payload)
      staffList.value.push(data)
    }
    showStaffModal.value = false
    showToast('저장되었습니다')
  } catch {
    showToast('저장 실패')
  }
}

async function deleteStaff(s) {
  if (!confirm(`"${s.name}"을(를) 삭제하시겠습니까?`)) return
  await axios.delete(`/api/staff/${s.id}`)
  staffList.value = staffList.value.filter(x => x.id !== s.id)
  showToast('삭제되었습니다')
}

// ── CSV ──
function exportCsv(type) {
  window.open(`/api/admin/export/${type}`, '_blank')
}

// ── Reset ──
async function resetData(target) {
  const labels = { objectives: 'Objective', tasks: '과제', staff: '인력', progress: '진행도', all: '모든' }
  if (!confirm(`${labels[target]} 데이터를 전부 삭제하시겠습니까?`)) return
  await axios.delete(`/api/admin/reset/${target}`)
  showToast('초기화 완료')
  fetchObjectives()
  fetchTasks()
  fetchStaff()
}

onMounted(async () => {
  await Promise.all([fetchObjectives(), fetchTasks(), fetchStaff()])
})
</script>

<style scoped>
.kr-edit-item {
  background: var(--gray-50);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 8px;
}
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
</style>
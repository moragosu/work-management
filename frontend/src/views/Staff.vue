<template>
  <div>
    <div class="page-header">
      <div>
        <h2>인력 관리</h2>
        <div class="subtitle">팀원 기술 현황 및 참여 Objective</div>
      </div>
      <button class="btn btn-primary btn-sm" @click="openAddModal">+ 인력 추가</button>
    </div>

    <div class="page-body">
      <!-- Summary cards -->
      <div class="grid-4" style="margin-bottom:24px">
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
      <div class="filter-bar">
        <div class="search-input">
          <span class="search-icon">🔍</span>
          <input v-model="search" class="form-control" placeholder="이름, 기술, Objective 검색..." @input="fetchStaff" />
        </div>
        <button class="btn btn-ghost btn-sm" @click="search = ''; fetchStaff()">초기화</button>
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
                  직책/역할 <span v-if="sortKey === 'role'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('main_skills')" style="cursor:pointer">
                  주 기술 <span v-if="sortKey === 'main_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('sub_skills')" style="cursor:pointer">
                  부 기술 <span v-if="sortKey === 'sub_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('objectives')" style="cursor:pointer">
                  참여 Objective <span v-if="sortKey === 'objectives'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th style="width:90px"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in sortedStaff" :key="member.id">
                <td style="font-weight:600;white-space:nowrap">{{ member.name }}</td>
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
                    <div v-for="objId in getObjectiveIds(member.objectives || member.okrs)" :key="objId" class="objective-item">
                      <div class="objective-header">
                        <span class="badge badge-blue" :title="getObjectiveName(objId)">{{ objId }}</span>
                        <button class="btn btn-ghost btn-xs" @click="openObjectiveSelect(member)" style="margin-left: 8px;">수정</button>
                      </div>
                      <div v-if="getObjectiveTasks(objId).length > 0" class="task-list">
                        <div v-for="task in getObjectiveTasks(objId)" :key="task.id" class="task-item">
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

    <!-- Add Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedMember ? '인력 수정' : '인력 추가' }}</h3>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">이름 *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">직책/역할</label>
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
            <label class="form-label">참여 Objective</label>
            <div class="flex gap-8" style="flex-wrap:wrap">
              <label v-for="o in objectives" :key="o.id" class="checkbox-label">
                <input type="checkbox" :value="o.id" v-model="form.objectiveIds" />
                {{ o.id }}
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showModal = false">취소</button>
          <button class="btn btn-primary" @click="submitForm" :disabled="!form.name.trim()">
            {{ selectedMember ? '수정' : '추가' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Objective Select Modal -->
    <div v-if="showObjectiveModal" class="modal-overlay" @click.self="showObjectiveModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>참여 Objective 선택 - {{ selectedMember?.name }}</h3>
          <button class="modal-close" @click="showObjectiveModal = false">✕</button>
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
          <button class="btn btn-ghost" @click="showObjectiveModal = false">취소</button>
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

const staff = ref([])
const objectives = ref([])
const tasks = ref([])  // 과제 목록 추가
const loading = ref(false)
const search = ref('')
const showModal = ref(false)
const showObjectiveModal = ref(false)
const toastMsg = ref('')
const debounceTimers = {}

const defaultForm = () => ({ name: '', role: '', main_skills: '', sub_skills: '', objectiveIds: [] })
const form = ref(defaultForm())

const selectedMember = ref(null)
const selectedObjectiveIds = ref([])

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

function getObjectiveIds(objectivesStr) {
  if (!objectivesStr) return []
  return objectivesStr.split(',').map(id => id.trim()).filter(Boolean)
}

async function fetchStaff() {
  loading.value = true
  try {
    const params = search.value ? { search: search.value } : {}
    const { data } = await axios.get('/api/staff', { params })
    staff.value = data
  } finally {
    loading.value = false
  }
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

// Objective ID로 Objective명 가져오기
function getObjectiveName(objectiveId) {
  const objective = objectives.value.find(obj => obj.id === objectiveId)
  return objective ? objective.name : objectiveId
}

function debounceSave(member, field, value) {
  const key = `${member.id}-${field}`
  clearTimeout(debounceTimers[key])
  debounceTimers[key] = setTimeout(async () => {
    member[field] = value
    try {
      await axios.put(`/api/staff/${member.id}`, { [field]: value })
      showToast('저장됨')
    } catch {
      showToast('저장 실패')
    }
  }, 800)
}

function openAddModal() {
  form.value = defaultForm()
  selectedMember.value = null
  showModal.value = true
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

async function submitAdd() {
  try {
    const payload = {
      ...form.value,
      okrs: form.value.objectiveIds.join(', ')  // 백엔드와 호환되는 필드명 사용
    }
    const { data } = await axios.post('/api/staff', payload)
    staff.value.push(data)
    showModal.value = false
    showToast('인력이 추가되었습니다')
  } catch {
    showToast('추가 실패')
  }
}

async function submitEdit() {
  if (!selectedMember.value) return
  
  try {
    const payload = {
      ...form.value,
      okrs: form.value.objectiveIds.join(', ')  // 백엔드와 호환되는 필드명 사용
    }
    const { data } = await axios.put(`/api/staff/${selectedMember.value.id}`, payload)
    
    // staff 배열 업데이트
    const index = staff.value.findIndex(s => s.id === selectedMember.value.id)
    if (index !== -1) {
      staff.value[index] = data
    }
    
    showModal.value = false
    showToast('인력 정보가 수정되었습니다')
  } catch {
    showToast('수정 실패')
  }
}

function openObjectiveSelect(member) {
  selectedMember.value = member
  selectedObjectiveIds.value = getObjectiveIds(member.objectives || member.okrs || '')
  showObjectiveModal.value = true
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
    
    showObjectiveModal.value = false
    showToast('저장됨')
  } catch {
    showToast('저장 실패')
  }
}

// 정렬 기능
const sortKey = ref('')
const sortOrder = ref('asc')

const sortedStaff = computed(() => {
  if (!sortKey.value) return staff.value
  
  return [...staff.value].sort((a, b) => {
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
function editMember(member) {
  selectedMember.value = member
  form.value = {
    name: member.name,
    role: member.role || '',
    main_skills: member.main_skills || '',
    sub_skills: member.sub_skills || '',
    objectiveIds: getObjectiveIds(member.objectives || member.okrs || '')  // okrs 필드도 지원
  }
  showModal.value = true
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
}

onMounted(async () => {
  await Promise.all([fetchStaff(), fetchObjectives(), fetchTasks()])
})
</script>

<style scoped>
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
</style>

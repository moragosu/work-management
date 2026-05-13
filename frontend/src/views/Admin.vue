<template>
  <div>
    <div class="page-header">
      <div>
        <h2>관리 도구</h2>
        <div class="subtitle">Objective · Key Result · 인력 · 진행도 관리</div>
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
          <div class="flex gap-8">
            <button class="btn btn-ghost btn-sm" @click="exportCsv('objectives')">⬇ Objective CSV 다운로드</button>
            <label class="btn btn-ghost btn-sm" style="cursor:pointer">
              ⬆ CSV 업로드
              <input type="file" accept=".csv" style="display:none" @change="importCsv('objectives', $event)" />
            </label>
          </div>
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
                  <th>ID</th><th>Objective명</th><th>PL</th><th>기술 스택</th>
                  <th>Key Results</th><th>진행률</th><th>상태</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in objectives" :key="o.id">
                  <td><span class="badge badge-blue">{{ o.id }}</span></td>
                  <td style="font-weight:600">{{ o.name }}</td>
                  <td>{{ o.pl }}</td>
                  <td><span class="text-sm">{{ o.tech_stack }}</span></td>
                  <td>
                    <div class="flex gap-4" style="align-items:center">
                      <span class="text-sm">{{ o.key_results?.length || 0 }}개</span>
                      <button class="btn btn-ghost btn-xs" @click="openKeyResultModal(o)">+ KR</button>
                    </div>
                  </td>
                  <td>
                    <span :style="{ color: pColor(calcProgress(o)), fontWeight: 600 }">{{ calcProgress(o) }}%</span>
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

      <!-- ── Staff Tab ── -->
      <div v-if="activeTab === 'staff'">
        <div class="flex-between" style="margin-bottom:16px">
          <div class="flex gap-8">
            <button class="btn btn-ghost btn-sm" @click="exportCsv('staff')">⬇ Staff CSV 다운로드</button>
            <label class="btn btn-ghost btn-sm" style="cursor:pointer">
              ⬆ CSV 업로드
              <input type="file" accept=".csv" style="display:none" @change="importCsv('staff', $event)" />
            </label>
          </div>
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
                <tr><th>이름</th><th>역할</th><th>주 기술</th><th>부 기술</th><th>학습 중</th><th>참여 Objective</th><th></th></tr>
              </thead>
              <tbody>
                <tr v-for="s in staffList" :key="s.id">
                  <td style="font-weight:600">{{ s.name }}</td>
                  <td>{{ s.role }}</td>
                  <td>{{ s.main_skills }}</td>
                  <td>{{ s.sub_skills }}</td>
                  <td>{{ s.learning }}</td>
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

      <!-- ── Progress Tab ── -->
      <div v-if="activeTab === 'progress'">
        <div class="flex gap-8" style="margin-bottom:16px">
          <button class="btn btn-ghost btn-sm" @click="exportCsv('progress')">⬇ Progress CSV 다운로드</button>
          <label class="btn btn-ghost btn-sm" style="cursor:pointer">
            ⬆ CSV 업로드
            <input type="file" accept=".csv" style="display:none" @change="importCsv('progress', $event)" />
          </label>
        </div>
        <div class="card card-body">
          <p class="text-muted text-sm">진행도 세부 내용 수정은 <strong>진행도 관리</strong> 페이지에서 하세요.</p>
        </div>
      </div>

      <!-- ── Reset Tab ── -->
      <div v-if="activeTab === 'reset'">
        <div class="card card-body">
          <h3 style="margin-bottom:16px;color:var(--danger)">⚠️ 데이터 초기화</h3>
          <p class="text-muted text-sm" style="margin-bottom:20px">삭제된 데이터는 복구할 수 없습니다. 신중하게 사용하세요.</p>
          <div class="flex gap-8" style="flex-wrap:wrap">
            <button class="btn btn-danger btn-sm" @click="resetData('objectives')">Objective 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('staff')">인력 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('progress')">진행도 전체 삭제</button>
            <button class="btn btn-danger" @click="resetData('all')">⚠️ 모든 데이터 삭제</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Objective Modal -->
    <div v-if="showObjectiveModal" class="modal-overlay" @click.self="showObjectiveModal = false">
      <div class="modal" style="max-width:640px">
        <div class="modal-header">
          <h3>{{ editingObjectiveId ? 'Objective 수정' : 'Objective 추가' }}</h3>
          <button class="modal-close" @click="showObjectiveModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">Objective ID *</label>
              <input v-model="objectiveForm.id" class="form-control" placeholder="O1, O2, ..." :disabled="!!editingObjectiveId" />
            </div>
            <div class="form-group">
              <label class="form-label">PL</label>
              <input v-model="objectiveForm.pl" class="form-control" />
            </div>
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
          <!-- Team members -->
          <div class="form-group">
            <div class="flex-between" style="margin-bottom:8px">
              <label class="form-label" style="margin-bottom:0">팀원</label>
              <button class="btn btn-ghost btn-xs" @click="addMember">+ 추가</button>
            </div>
            <div v-for="(m, idx) in objectiveForm.team_members" :key="idx" class="flex gap-8" style="margin-bottom:6px">
              <input v-model="m.name" class="form-control" placeholder="이름" style="flex:2" />
              <input v-model="m.role" class="form-control" placeholder="역할" style="flex:2" />
              <input type="number" v-model.number="m.contribution" class="form-control" placeholder="기여도%" style="flex:1;width:70px" />
              <button class="btn btn-danger btn-xs" @click="objectiveForm.team_members.splice(idx, 1)">✕</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showObjectiveModal = false">취소</button>
          <button class="btn btn-primary" @click="submitObjective" :disabled="!objectiveForm.id || !objectiveForm.name">저장</button>
        </div>
      </div>
    </div>

    <!-- Key Result Modal -->
    <div v-if="showKeyResultModal" class="modal-overlay" @click.self="showKeyResultModal = false">
      <div class="modal" style="max-width:640px">
        <div class="modal-header">
          <h3>Key Results 관리 - {{ selectedObjective?.id }}: {{ selectedObjective?.name }}</h3>
          <button class="modal-close" @click="showKeyResultModal = false">✕</button>
        </div>
        <div class="modal-body">
          <!-- Existing Key Results -->
          <div v-if="selectedObjective?.key_results?.length > 0" style="margin-bottom:16px">
            <div class="text-sm text-muted" style="margin-bottom:8px">등록된 Key Results:</div>
            <div v-for="kr in selectedObjective.key_results" :key="kr.id" class="kr-edit-item">
              <div class="flex gap-8" style="align-items:center">
                <input v-model="kr.id" class="form-control" placeholder="KR1" style="width:80px" />
                <input v-model="kr.name" class="form-control" placeholder="Key Result 내용" style="flex:1" />
                <input type="number" v-model.number="kr.progress" min="0" max="100" class="form-control" style="width:80px" />
                <span class="text-sm">%</span>
                <button class="btn btn-danger btn-xs" @click="deleteKeyResult(kr.id)">✕</button>
              </div>
            </div>
          </div>
          
          <!-- Add new Key Result -->
          <div class="text-sm text-muted" style="margin-bottom:8px">새 Key Result 추가:</div>
          <div class="flex gap-8" style="align-items:center">
            <input v-model="newKeyResult.id" class="form-control" placeholder="KR1" style="width:80px" />
            <input v-model="newKeyResult.name" class="form-control" placeholder="Key Result 내용" style="flex:1" />
            <input type="number" v-model.number="newKeyResult.progress" min="0" max="100" class="form-control" style="width:80px" />
            <span class="text-sm">%</span>
            <button class="btn btn-primary btn-xs" @click="addKeyResult" :disabled="!newKeyResult.id || !newKeyResult.name">추가</button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showKeyResultModal = false">닫기</button>
          <button class="btn btn-primary" @click="saveKeyResults">저장</button>
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
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">이름 *</label>
              <input v-model="staffForm.name" class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">직책/역할</label>
              <input v-model="staffForm.role" class="form-control" />
            </div>
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
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">학습 중</label>
              <input v-model="staffForm.learning" class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">희망 분야</label>
              <input v-model="staffForm.desired_field" class="form-control" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">참여 Objective</label>
            <input v-model="staffForm.objectives" class="form-control" placeholder="O1, O2, ..." />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showStaffModal = false">취소</button>
          <button class="btn btn-primary" @click="submitStaff" :disabled="!staffForm.name.trim()">저장</button>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tabs = [
  { key: 'objective', label: '📊 Objective 관리' },
  { key: 'staff', label: '👥 인력 관리' },
  { key: 'progress', label: '📋 진행도' },
  { key: 'reset', label: '🗑 초기화' },
]
const activeTab = ref('objective')

const objectives = ref([])
const staffList = ref([])
const loading = ref(false)
const staffLoading = ref(false)
const toastMsg = ref('')

const showObjectiveModal = ref(false)
const editingObjectiveId = ref(null)
const defaultObjectiveForm = () => ({ id: '', name: '', pl: '', tech_stack: '', status: '진행중', team_members: [] })
const objectiveForm = ref(defaultObjectiveForm())

const showKeyResultModal = ref(false)
const selectedObjective = ref(null)
const newKeyResult = ref({ id: '', name: '', progress: 0 })

const showStaffModal = ref(false)
const editingStaffId = ref(null)
const defaultStaffForm = () => ({ name: '', role: '', main_skills: '', sub_skills: '', learning: '', desired_field: '', objectives: '' })
const staffForm = ref(defaultStaffForm())

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2500)
}

function calcProgress(obj) {
  const keyResults = obj.key_results || []
  if (keyResults.length === 0) return 0
  const total = keyResults.reduce((sum, kr) => sum + (kr.progress || 0), 0)
  return Math.round(total / keyResults.length)
}

function pColor(pct) {
  if (pct >= 100) return 'var(--success)'
  if (pct < 30) return 'var(--danger)'
  return 'var(--primary)'
}
function sBadge(s) {
  return { '진행중': 'badge badge-blue', '완료': 'badge badge-green', '위험': 'badge badge-red' }[s] || 'badge badge-gray'
}

// ── Objective ──
async function fetchObjectives() {
  loading.value = true
  try { const { data } = await axios.get('/api/okrs'); objectives.value = data }
  finally { loading.value = false }
}

function openObjectiveModal(o = null) {
  if (o) {
    objectiveForm.value = JSON.parse(JSON.stringify(o))
    editingObjectiveId.value = o.id
  } else {
    objectiveForm.value = defaultObjectiveForm()
    editingObjectiveId.value = null
  }
  showObjectiveModal.value = true
}

function addMember() {
  objectiveForm.value.team_members.push({ name: '', role: '', contribution: 0 })
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
  newKeyResult.value = { id: '', name: '', progress: 0 }
  showKeyResultModal.value = true
}

async function addKeyResult() {
  if (!newKeyResult.value.id || !newKeyResult.value.name) return
  
  try {
    const { data } = await axios.post(`/api/okrs/${selectedObjective.value.id}/key-results`, {
      id: newKeyResult.value.id,
      name: newKeyResult.value.name,
      progress: Math.min(100, Math.max(0, newKeyResult.value.progress || 0))
    })
    selectedObjective.value.key_results.push(data)
    newKeyResult.value = { id: '', name: '', progress: 0 }
    // Refresh objectives list to show updated key results
    await fetchObjectives()
    // Update selectedObjective with fresh data
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
    showToast('삭제되었습니다')
  } catch (e) {
    showToast('삭제 실패')
  }
}

async function saveKeyResults() {
  try {
    // Update all key results
    for (const kr of selectedObjective.value.key_results) {
      kr.progress = Math.min(100, Math.max(0, kr.progress || 0))
    }
    await axios.put(`/api/okrs/${selectedObjective.value.id}`, {
      key_results: selectedObjective.value.key_results
    })
    // Refresh objectives
    await fetchObjectives()
    showKeyResultModal.value = false
    showToast('저장되었습니다')
  } catch (e) {
    showToast('저장 실패')
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
    staffForm.value = { ...s }
    editingStaffId.value = s.id
  } else {
    staffForm.value = defaultStaffForm()
    editingStaffId.value = null
  }
  showStaffModal.value = true
}

async function submitStaff() {
  try {
    if (editingStaffId.value) {
      const { data } = await axios.put(`/api/staff/${editingStaffId.value}`, staffForm.value)
      const idx = staffList.value.findIndex(s => s.id === editingStaffId.value)
      if (idx !== -1) staffList.value[idx] = data
    } else {
      const { data } = await axios.post('/api/staff', staffForm.value)
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

async function importCsv(type, event) {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const { data } = await axios.post(`/api/admin/import/${type}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    showToast(`${data.imported}개 항목 가져오기 완료`)
    if (type === 'objectives') fetchObjectives()
    if (type === 'staff') fetchStaff()
  } catch {
    showToast('가져오기 실패')
  }
  event.target.value = ''
}

// ── Reset ──
async function resetData(target) {
  const labels = { objectives: 'Objective', staff: '인력', progress: '진행도', all: '모든' }
  if (!confirm(`${labels[target]} 데이터를 전부 삭제하시겠습니까? 복구할 수 없습니다.`)) return
  await axios.delete(`/api/admin/reset/${target}`)
  showToast('초기화 완료')
  fetchObjectives()
  fetchStaff()
}

onMounted(async () => {
  await Promise.all([fetchObjectives(), fetchStaff()])
})
</script>

<style scoped>
.kr-edit-item {
  background: var(--gray-50);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 8px;
}
</style>
<template>
  <div>
    <div class="page-header">
      <div>
        <h2>관리 도구</h2>
        <div class="subtitle">Objective · Key Result · 과제 · 인력 관리</div>
      </div>
      <div v-if="adminMode" class="flex gap-8">
        <span class="badge badge-red">관리자 모드</span>
        <button class="btn btn-ghost btn-sm" @click="toggleAdminMode">관리자 모드 해제</button>
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
        <div class="grid-4" style="margin-bottom:20px">
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value">{{ objectiveStats.total }}</div>
            <div class="stat-label">전체 Objective</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:var(--primary)">{{ objectiveStats.inProgress }}</div>
            <div class="stat-label">진행중</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:#22c55e">{{ objectiveStats.done }}</div>
            <div class="stat-label">완료</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:var(--danger)">{{ objectiveStats.danger }}</div>
            <div class="stat-label">위험</div>
          </div></div>
        </div>
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
                <th @click="sortBy('id', 'objectives')" style="cursor:pointer">
                  ID <span v-if="sortKeys.objectives === 'id'">{{ sortOrders.objectives === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('name', 'objectives')" style="cursor:pointer">
                  Objective명 <span v-if="sortKeys.objectives === 'name'">{{ sortOrders.objectives === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('tech_stack', 'objectives')" style="cursor:pointer">
                  기술 스택 <span v-if="sortKeys.objectives === 'tech_stack'">{{ sortOrders.objectives === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('key_results.length', 'objectives')" style="cursor:pointer">
                  Key Results <span v-if="sortKeys.objectives === 'key_results.length'">{{ sortOrders.objectives === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('status', 'objectives')" style="cursor:pointer">
                  상태 <span v-if="sortKeys.objectives === 'status'">{{ sortOrders.objectives === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th></th>
              </tr>
            </thead>
              <tbody>
                <tr v-for="o in sortedObjectives" :key="o.id">
                  <td><span class="badge badge-blue">{{ o.id }}</span></td>
                  <td style="font-weight:600">{{ o.name }}</td>
                  <td><span class="text-sm">{{ o.tech_stack }}</span></td>
                  <td>
                      <div style="display:flex;align-items:center;gap:8px">
                        <div style="min-width:120px">
                          <div class="text-sm">
                            {{ o.key_results?.length || 0 }}개
                            <button class="btn btn-ghost btn-xs" @click="openKeyResultModal(o)" style="margin-left:4px">+ KR</button>
                          </div>
                          <div v-if="o.key_results && o.key_results.length > 0" class="key-result-list" style="max-height:100px;overflow-y:auto">
                            <div v-for="kr in o.key_results" :key="kr.id" class="text-xs text-muted" style="margin-top:2px;padding-left:8px;border-left:2px solid var(--outline)">
                              <span class="text-xs" style="color:var(--primary)">{{ kr.id }}</span> {{ kr.name }}
                            </div>
                          </div>
                        </div>
                      </div>
                  </td>
                  <td><span :class="sBadge(o.status)">{{ o.status }}</span></td>
                  <td>
                    <div style="display:flex;gap:8px">
                      <button class="btn btn-ghost btn-xs" @click="openObjectiveModal(o)">수정</button>
                      <button class="btn btn-danger btn-xs" @click="deleteObjective(o)">삭제</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Related Data Section -->
          <div v-if="selectedObjectiveForDetails" class="card card-body mt-16">
            <h4>관련 데이터</h4>
            <div class="grid-2">
              <div>
                <h5 class="text-sm text-muted mb-8">관련 과제 ({{ selectedObjectiveForDetails.related_tasks.length }}개)</h5>
                <div v-for="task in selectedObjectiveForDetails.related_tasks" :key="task.id" class="text-sm mb-4">
                  • {{ task.id }}: {{ task.name }}
                </div>
              </div>
              <div>
                <h5 class="text-sm text-muted mb-8">관련 인력 ({{ selectedObjectiveForDetails.related_staff.length }}명)</h5>
                <div v-for="staff in selectedObjectiveForDetails.related_staff" :key="staff.id" class="text-sm mb-4">
                  • {{ staff.name }} ({{ staff.role || '역할 없음' }})
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Task Tab ── -->
      <div v-if="activeTab === 'task'">
        <div class="grid-4" style="margin-bottom:20px">
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value">{{ taskStats.total }}</div>
            <div class="stat-label">전체 과제</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:var(--primary)">{{ taskStats.totalKR }}</div>
            <div class="stat-label">전체 KR</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:#22c55e">{{ taskStats.withMembers }}</div>
            <div class="stat-label">인력 배정 완료</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:#f59e0b">{{ taskStats.noMembers }}</div>
            <div class="stat-label">인력 미배정</div>
          </div></div>
        </div>
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
          
          <!-- Related Data Section -->
          <div v-if="selectedTaskForDetails" class="card card-body mt-16">
            <h4>관련 데이터</h4>
            <div class="grid-2">
              <div>
                <h5 class="text-sm text-muted mb-8">관련 Objective</h5>
                <div v-if="selectedTaskForDetails.related_objective" class="text-sm mb-4">
                  • {{ selectedTaskForDetails.related_objective.id }}: {{ selectedTaskForDetails.related_objective.name }}
                </div>
                <div v-else class="text-sm text-muted">연결된 Objective 없음</div>
              </div>
              <div>
                <h5 class="text-sm text-muted mb-8">관련 인력 ({{ selectedTaskForDetails.related_staff.length }}명)</h5>
                <div v-for="staff in selectedTaskForDetails.related_staff" :key="staff.id" class="text-sm mb-4">
                  • {{ staff.name }} ({{ staff.role || '역할 없음' }})
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Staff Tab ── -->
      <div v-if="activeTab === 'staff'">
        <div class="grid-4" style="margin-bottom:20px">
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value">{{ staffStats.total }}</div>
            <div class="stat-label">총 인원</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:var(--primary)">{{ staffStats.objCounts['O1'] || 0 }}</div>
            <div class="stat-label">O1 참여</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:var(--primary)">{{ staffStats.objCounts['O2'] || 0 }}</div>
            <div class="stat-label">O2 참여</div>
          </div></div>
          <div class="card"><div class="card-body stat-card">
            <div class="stat-value" style="color:var(--primary)">{{ staffStats.objCounts['O3'] || 0 }}</div>
            <div class="stat-label">O3 참여</div>
          </div></div>
        </div>
        <div class="flex-between" style="margin-bottom:16px">
          <button class="btn btn-ghost btn-sm" @click="exportCsv('staff')">⬇ CSV 다운로드</button>
          <button class="btn btn-primary btn-sm" @click="staffViewRef?.openAddModal()">+ 인력 추가</button>
        </div>
        <StaffView :embedded="true" ref="staffViewRef" />
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

      <!-- ── Settings Tab ── -->
      <div v-if="activeTab === 'settings'">
        <div class="card card-body">
          <h3 style="margin-bottom:24px">⚙️ 설정</h3>
          
          <div class="form-group" style="margin-bottom:32px">
            <label class="form-label">관리자 모드</label>
            <div v-if="!adminMode" class="mt-16">
              <div style="margin-bottom:16px">
                <input v-model="adminPassword" type="password" class="form-control" placeholder="비밀번호를 입력하세요" style="margin-bottom:8px" />
                <button class="btn btn-primary" @click="activateAdminMode">관리자 모드 활성화</button>
              </div>
              <p class="text-sm text-muted">관리자 모드를 활성화하면 초기화 기능을 사용할 수 있습니다.</p>
            </div>
            <div v-else>
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
                <span class="badge badge-red">활성화됨</span>
                <button class="btn btn-ghost btn-sm" @click="deactivateAdminMode">비활성화</button>
              </div>
              <p class="text-sm text-muted">관리자 모드가 활성화되어 초기화 기능을 사용할 수 있습니다.</p>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">정보</label>
            <div class="text-sm text-muted" style="margin-top:8px">
              <div>버전: 1.0.0</div>
              <div style="margin-top:4px">개발자: Work Management Team</div>
            </div>
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
                <input v-model="kr.name" class="form-control" placeholder="Key Result 내용" style="flex:1" @input="onKeyResultInput(kr)" />
                <button v-if="kr.isModified" class="btn btn-primary btn-xs" @click="updateKeyResult(kr)" style="min-width:60px">수정</button>
                <button v-else class="btn btn-danger btn-xs" @click="deleteKeyResult(kr.id)">✕</button>
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
                <div style="flex:1">
                  <div>{{ m.name }}</div>
                  <div class="text-xs text-muted">{{ m.role || '역할 없음' }}</div>
                </div>
                <button class="btn btn-danger btn-xs" @click="removeTaskMember(m.staff_id)">✕</button>
              </div>
            </div>
          </div>
          <div class="text-sm text-muted" style="margin-bottom:8px">인력 추가:</div>
          <select v-model="selectedStaffId" class="form-control" style="margin-bottom:8px">
            <option value="">선택</option>
            <option v-for="s in availableStaff" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <input v-model="selectedStaffRole" class="form-control" placeholder="역할을 입력하세요" style="margin-bottom:8px" />
          <button class="btn btn-primary btn-sm" @click="addTaskMember" :disabled="!selectedStaffId">추가</button>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showTaskMemberModal = false">닫기</button>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import StaffView from './Staff.vue'

const adminMode = ref(false)

const tabs = computed(() => {
  const baseTabs = [
    { key: 'objective', label: '📊 Objective' },
    { key: 'task', label: '📋 과제' },
    { key: 'staff', label: '👥 인력' },
  ]
  if (adminMode.value) {
    baseTabs.push({ key: 'reset', label: '🗑 초기화' })
  }
  baseTabs.push({ key: 'settings', label: '⚙️ 설정' })
  return baseTabs
})

const activeTab = ref('objective')

const objectives = ref([])
const tasks = ref([])
const staffList = ref([])
const loading = ref(false)
const taskLoading = ref(false)
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
const selectedStaffRole = ref('')

// Staff (staffList는 Task Member 모달의 availableStaff 계산에 필요)
const staffViewRef = ref(null)

// Admin Mode
const adminPassword = ref('')

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2500)
}

// ── 탭별 현황 통계 ──
const objectiveStats = computed(() => ({
  total: objectives.value.length,
  inProgress: objectives.value.filter(o => o.status === '진행중').length,
  done: objectives.value.filter(o => o.status === '완료').length,
  danger: objectives.value.filter(o => o.status === '위험').length,
}))

const taskStats = computed(() => ({
  total: tasks.value.length,
  totalKR: objectives.value.reduce((s, o) => s + (o.key_results?.length || 0), 0),
  withMembers: tasks.value.filter(t => t.members?.length > 0).length,
  noMembers: tasks.value.filter(t => !t.members?.length).length,
}))

const staffStats = computed(() => {
  const objCounts = {}
  staffList.value.forEach(s => {
    ;(s.okrs || '').split(',').map(id => id.trim()).filter(Boolean).forEach(id => {
      objCounts[id] = (objCounts[id] || 0) + 1
    })
  })
  return {
    total: staffList.value.length,
    withObjective: staffList.value.filter(s => s.okrs?.trim()).length,
    objCounts,
  }
})

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

// 정렬 기능
const sortKeys = ref({
  objectives: '',
  tasks: '',
  staff: ''
})

const sortOrders = ref({
  objectives: 'asc',
  tasks: 'asc',
  staff: 'asc'
})

function sortBy(key, tab) {
  if (sortKeys.value[tab] === key) {
    if (sortOrders.value[tab] === 'asc') {
      sortOrders.value[tab] = 'desc'
    } else {
      sortKeys.value[tab] = ''
      sortOrders.value[tab] = 'asc'
    }
  } else {
    sortKeys.value[tab] = key
    sortOrders.value[tab] = 'asc'
  }
}

// 정렬된 데이터 computed properties
const sortedObjectives = computed(() => {
  const key = sortKeys.value.objectives
  if (!key) return objectives.value
  
  return [...objectives.value].sort((a, b) => {
    let aVal, bVal
    
    // key_results.length의 경우 특별 처리
    if (key === 'key_results.length') {
      aVal = a.key_results?.length || 0
      bVal = b.key_results?.length || 0
    } else {
      // 점 표기법 처리 (예: 'status')
      aVal = a[key]
      bVal = b[key]
    }
    
    // 문자열 비교
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    let result = 0
    if (aVal < bVal) result = -1
    else if (aVal > bVal) result = 1
    
    return sortOrders.value.objectives === 'asc' ? result : -result
  })
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

// Related data for selected objective
const selectedObjectiveForDetails = ref(null)

async function showObjectiveDetails(objectiveId) {
  try {
    const { data } = await axios.get(`/api/okrs/${objectiveId}/related`)
    selectedObjectiveForDetails.value = data
  } catch (e) {
    showToast('관련 데이터 조회 실패')
  }
}

// Objective row click to show details
function onObjectiveRowClick(objective) {
  showObjectiveDetails(objective.id)
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
  // 원본 데이터 저장을 위해 deep copy
  selectedObjective.value = JSON.parse(JSON.stringify(o))
  // 각 Key Result에 원본 이름 저장
  if (selectedObjective.value.key_results) {
    selectedObjective.value.key_results.forEach(kr => {
      kr.originalName = kr.name
      kr.isModified = false
    })
  }
  newKeyResultName.value = ''
  showKeyResultModal.value = true
}

function onKeyResultInput(kr) {
  // 원본이 없으면 생성 (처음 로드된 경우)
  if (kr.originalName === undefined) {
    kr.originalName = kr.name
  }
  // 수정 여부 확인
  kr.isModified = kr.name !== kr.originalName
}

async function updateKeyResult(kr) {
  try {
    await axios.put(`/api/okrs/${selectedObjective.value.id}/key-results/${kr.id}`, {
      name: kr.name
    })
    // 원본 이름 업데이트
    kr.originalName = kr.name
    kr.isModified = false
    // 메인 objectives 목록도 업데이트
    const mainObj = objectives.value.find(o => o.id === selectedObjective.value.id)
    if (mainObj) {
      const mainKr = mainObj.key_results.find(k => k.id === kr.id)
      if (mainKr) {
        mainKr.name = kr.name
      }
    }
    showToast('Key Result가 수정되었습니다')
  } catch (e) {
    showToast('수정 실패')
  }
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

// Related data for selected task
const selectedTaskForDetails = ref(null)

async function showTaskDetails(taskId) {
  try {
    const { data } = await axios.get(`/api/tasks/${taskId}/related`)
    selectedTaskForDetails.value = data
  } catch (e) {
    showToast('관련 데이터 조회 실패')
  }
}

// Task row click to show details
function onTaskRowClick(task) {
  showTaskDetails(task.id)
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
  selectedTask.value.members.push({ 
    staff_id: staff.id, 
    name: staff.name, 
    role: selectedStaffRole.value 
  })
  
  try {
    await axios.put(`/api/tasks/${selectedTask.value.id}`, { members: selectedTask.value.members })
    await fetchTasks()
    const updated = tasks.value.find(t => t.id === selectedTask.value.id)
    if (updated) selectedTask.value = JSON.parse(JSON.stringify(updated))
    selectedStaffId.value = ''
    selectedStaffRole.value = ''
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
  const { data } = await axios.get('/api/staff')
  staffList.value = data
}

// ── CSV ──
function exportCsv(type) {
  window.open(`/api/admin/export/${type}`, '_blank')
}

// ── Admin Mode ──
function toggleAdminMode() {
  adminMode.value = !adminMode.value
  // localStorage에 관리자 모드 상태 저장
  if (adminMode.value) {
    localStorage.setItem('adminMode', 'true')
    showToast('관리자 모드가 활성화되었습니다')
  } else {
    localStorage.removeItem('adminMode')
    showToast('관리자 모드가 비활성화되었습니다')
  }
}

function activateAdminMode() {
  // 간단한 비밀번호 확인 (실제 프로덕션에서는 더 강력한 인증 필요)
  if (adminPassword.value === 'admin123') {
    adminMode.value = true
    localStorage.setItem('adminMode', 'true')
    showToast('관리자 모드가 활성화되었습니다')
    adminPassword.value = ''
  } else {
    showToast('비밀번호가 올바르지 않습니다')
  }
}

function deactivateAdminMode() {
  adminMode.value = false
  localStorage.removeItem('adminMode')
  showToast('관리자 모드가 비활성화되었습니다')
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
  // localStorage에서 관리자 모드 상태 복원
  adminMode.value = localStorage.getItem('adminMode') === 'true'
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

.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 6px;
}
</style>
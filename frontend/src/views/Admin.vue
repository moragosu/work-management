<template>
  <div>
    <div class="page-header">
      <div>
        <h2>관리 도구</h2>
        <div class="subtitle">목표 · Key Result · 과제 · 인력 관리</div>
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

      <ObjectiveTab
        v-if="activeTab === 'objective'"
        :objectives="objectives"
        :tasks="tasks"
        :staff-list="staffList"
        :loading="loading"
        :next-id="nextObjectiveId"
        :reusable-ids="reusableObjectiveIds"
        @refresh="fetchAll"
      />

      <TaskTab
        v-if="activeTab === 'task'"
        :tasks="tasks"
        :objectives="objectives"
        :staff-list="staffList"
        :loading="taskLoading"
        :next-id="nextTaskId"
        :reusable-ids="reusableTaskIds"
        :task-targets="taskTargets"
        @refresh="fetchAll"
      />

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
        <div class="tab-toolbar">
          <button class="btn btn-ghost btn-sm" @click="exportCsv('staff')" data-tooltip="파트원 목록을 CSV 파일로 내보내기">⬇ CSV 다운로드</button>
          <button class="btn btn-primary btn-sm" @click="staffViewRef?.openAddModal()" data-tooltip="새 파트원 추가">+ 인력 추가</button>
        </div>
        <StaffView :embedded="true" ref="staffViewRef" @updated="fetchStaff" />
      </div>

      <!-- ── Reset Tab ── -->
      <div v-if="activeTab === 'reset'">
        <div class="card card-body">
          <h3 class="reset-heading">⚠️ 데이터 초기화</h3>
          <p class="text-muted text-sm reset-desc">삭제된 데이터는 복구할 수 없습니다.</p>
          <div class="reset-actions">
            <button class="btn btn-danger btn-sm" @click="resetData('objectives')" data-tooltip="등록된 목표(OKR)를 모두 삭제 — 복구 불가">목표 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('tasks')" data-tooltip="등록된 과제를 모두 삭제 — 복구 불가">과제 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('staff')" data-tooltip="등록된 파트원 정보를 모두 삭제 — 복구 불가">인력 전체 삭제</button>
            <button class="btn btn-danger btn-sm" @click="resetData('progress')" data-tooltip="주간 진행 현황 및 이슈를 모두 삭제 — 복구 불가">진행도 전체 삭제</button>
            <button class="btn btn-danger" @click="resetData('all')" data-tooltip="⚠️ 모든 데이터 영구 삭제 — 절대 복구 불가">⚠️ 모든 데이터 삭제</button>
          </div>
        </div>
      </div>

      <!-- ── Settings Tab ── -->
      <div v-if="activeTab === 'settings'">
        <div class="card card-body">
          <h3 class="settings-heading">⚙️ 설정</h3>

          <div class="settings-group">
            <label class="form-label">관리자 모드</label>
            <div v-if="!adminMode" class="mt-16">
              <div class="password-form">
                <input v-model="adminPassword" type="password" class="form-control password-input" placeholder="비밀번호를 입력하세요" @keyup.enter="activateAdminMode" />
                <button class="btn btn-primary" @click="activateAdminMode">관리자 모드 활성화</button>
              </div>
              <p class="text-sm text-muted">관리자 모드를 활성화하면 초기화 기능을 사용할 수 있습니다.</p>
            </div>
            <div v-else>
              <div class="admin-status-row">
                <span class="badge badge-red">활성화됨</span>
                <button class="btn btn-ghost btn-sm" @click="deactivateAdminMode">비활성화</button>
              </div>
              <p class="text-sm text-muted">관리자 모드가 활성화되어 초기화 기능을 사용할 수 있습니다.</p>
            </div>
          </div>

          <div v-if="adminMode" class="settings-group">
            <label class="form-label">과제 적용 대상 관리</label>
            <div class="target-chips mt-16">
              <span v-for="t in taskTargets" :key="t" class="target-chip">
                {{ t }}
                <button class="target-chip-del" @click="removeTarget(t)" :data-tooltip="`'${t}' 삭제`">✕</button>
              </span>
            </div>
            <div class="target-add-form mt-16">
              <input v-model="newTarget" class="form-control" placeholder="새 항목 입력 (예: HA)" @keyup.enter="addTarget" />
              <button class="btn btn-primary btn-sm" @click="addTarget" :disabled="!newTarget.trim() || taskTargets.includes(newTarget.trim())">추가</button>
            </div>
          </div>

          <div class="settings-group">
            <label class="form-label">질문자 목록 관리 <span class="text-muted text-sm" style="font-weight:400">(파트장, 그룹장 등)</span></label>
            <p class="text-sm text-muted" style="margin:4px 0 12px">Q&amp;A 질문 작성 시 드롭다운으로 선택할 수 있는 질문자 목록입니다.</p>
            <div class="target-chips mt-16">
              <span v-for="q in questioners" :key="q" class="target-chip">
                {{ q }}
                <button class="target-chip-del" @click="removeQuestioner(q)" :data-tooltip="`'${q}' 삭제`">✕</button>
              </span>
              <span v-if="questioners.length === 0" class="text-sm text-muted">등록된 질문자가 없습니다.</span>
            </div>
            <div class="target-add-form mt-16">
              <input v-model="newQuestioner" class="form-control" placeholder="이름 입력 (예: 홍길동 파트장)" @keyup.enter="addQuestioner" />
              <button class="btn btn-primary btn-sm" @click="addQuestioner" :disabled="!newQuestioner.trim() || questioners.includes(newQuestioner.trim())">추가</button>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">정보</label>
            <div class="info-list text-sm text-muted">
              <div>버전: 1.0.0</div>
              <div class="info-item">개발자: Work Management Team</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import StaffView from './Staff.vue'
import ObjectiveTab from '../components/admin/ObjectiveTab.vue'
import TaskTab from '../components/admin/TaskTab.vue'
import { useToast } from '../composables/useToast.js'
import { parseIds } from '../utils/parseIds.js'
import { ADMIN_PASSWORD } from '../config.js'

const route = useRoute()
const adminMode = ref(false)

const tabs = computed(() => {
  const baseTabs = [
    { key: 'objective', label: '📊 목표' },
    { key: 'task', label: '📋 과제' },
    { key: 'staff', label: '👥 인력' },
  ]
  if (adminMode.value) baseTabs.push({ key: 'reset', label: '🗑 초기화' })
  baseTabs.push({ key: 'settings', label: '⚙️ 설정' })
  return baseTabs
})

const activeTab = ref('objective')
const objectives = ref([])
const tasks = ref([])
const staffList = ref([])
const loading = ref(false)
const taskLoading = ref(false)
const { toastMsg, showToast } = useToast(2500)
const nextObjectiveId = ref('O1')
const nextTaskId = ref('T1')
const reusableObjectiveIds = ref([])
const reusableTaskIds = ref([])
const staffViewRef = ref(null)
const taskTargets = ref(['MX', 'VD', 'DA', '공통'])
const newTarget = ref('')
const questioners = ref([])
const newQuestioner = ref('')

const staffStats = computed(() => {
  const objCounts = {}
  staffList.value.forEach(s => {
    parseIds(s.okrs).forEach(id => { objCounts[id] = (objCounts[id] || 0) + 1 })
  })
  return { total: staffList.value.length, objCounts }
})

async function fetchObjectives() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/okrs')
    objectives.value = data
    const [{ data: nextId }, { data: reusable }] = await Promise.all([
      axios.get('/api/okrs/next-id'),
      axios.get('/api/okrs/reusable-ids'),
    ])
    nextObjectiveId.value = nextId.next_id
    reusableObjectiveIds.value = reusable.reusable_ids
  } finally { loading.value = false }
}

async function fetchTasks() {
  taskLoading.value = true
  try {
    const { data } = await axios.get('/api/tasks')
    tasks.value = data
    const [{ data: nextId }, { data: reusable }] = await Promise.all([
      axios.get('/api/tasks/next-id'),
      axios.get('/api/tasks/reusable-ids'),
    ])
    nextTaskId.value = nextId.next_id
    reusableTaskIds.value = reusable.reusable_ids
  } finally { taskLoading.value = false }
}

async function fetchStaff() {
  const { data } = await axios.get('/api/staff')
  staffList.value = data
}

async function fetchSettings() {
  try {
    const { data } = await axios.get('/api/settings')
    if (Array.isArray(data.task_targets)) taskTargets.value = data.task_targets
    if (Array.isArray(data.questioners)) questioners.value = data.questioners
  } catch {
    // 기본값 유지
  }
}

async function saveSettings() {
  await axios.put('/api/settings', {
    task_targets: taskTargets.value,
    questioners: questioners.value,
  })
}

async function addTarget() {
  const val = newTarget.value.trim()
  if (!val || taskTargets.value.includes(val)) return
  taskTargets.value.push(val)
  newTarget.value = ''
  await saveSettings()
  showToast(`'${val}' 추가되었습니다`)
}

async function removeTarget(t) {
  taskTargets.value = taskTargets.value.filter(x => x !== t)
  await saveSettings()
  showToast(`'${t}' 삭제되었습니다`)
}

async function addQuestioner() {
  const val = newQuestioner.value.trim()
  if (!val || questioners.value.includes(val)) return
  questioners.value.push(val)
  newQuestioner.value = ''
  await saveSettings()
  showToast(`'${val}' 추가되었습니다`)
}

async function removeQuestioner(q) {
  questioners.value = questioners.value.filter(x => x !== q)
  await saveSettings()
  showToast(`'${q}' 삭제되었습니다`)
}

async function fetchAll() {
  await Promise.all([fetchObjectives(), fetchTasks(), fetchStaff()])
}

function exportCsv(type) { window.open(`/api/admin/export/${type}`, '_blank') }

const adminPassword = ref('')

function toggleAdminMode() {
  adminMode.value = !adminMode.value
  if (adminMode.value) {
    localStorage.setItem('adminMode', 'true')
    showToast('관리자 모드가 활성화되었습니다')
  } else {
    localStorage.removeItem('adminMode')
    showToast('관리자 모드가 비활성화되었습니다')
  }
}

function activateAdminMode() {
  if (adminPassword.value === ADMIN_PASSWORD) {
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

async function resetData(target) {
  const labels = { objectives: '목표', tasks: '과제', staff: '인력', progress: '진행도', all: '모든' }
  if (!confirm(`${labels[target]} 데이터를 전부 삭제하시겠습니까?`)) return
  await axios.delete(`/api/admin/reset/${target}`)
  showToast('초기화 완료')
  fetchAll()
}

onMounted(async () => {
  adminMode.value = localStorage.getItem('adminMode') === 'true'
  if (route.query.tab) activeTab.value = route.query.tab
  await Promise.all([fetchAll(), fetchSettings()])
})
</script>

<style scoped>
.tab-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }

.reset-heading { margin-bottom: 16px; color: var(--danger); }
.reset-desc { margin-bottom: 20px; }
.reset-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.settings-heading { margin-bottom: 24px; }
.settings-group { margin-bottom: 32px; }
.password-form { margin-bottom: 16px; display: flex; flex-direction: column; gap: 8px; }
.admin-status-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.info-list { margin-top: 8px; }
.info-item { margin-top: 4px; }

.target-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.target-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 999px;
  background: var(--primary-light); color: var(--primary);
  border: 1px solid var(--primary); font-size: 13px; font-weight: 600;
}
.target-chip-del {
  display: flex; align-items: center; justify-content: center;
  width: 16px; height: 16px; border-radius: 50%;
  border: none; background: transparent; color: var(--primary);
  cursor: pointer; font-size: 11px; padding: 0;
  transition: background 0.15s;
}
.target-chip-del:hover { background: var(--primary); color: #fff; }
.target-add-form { display: flex; gap: 8px; align-items: center; }
.target-add-form .form-control { max-width: 200px; }
</style>

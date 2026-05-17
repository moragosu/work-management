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
        @refresh="fetchAll"
      />

      <TaskTab
        v-if="activeTab === 'task'"
        :tasks="tasks"
        :objectives="objectives"
        :staff-list="staffList"
        :loading="taskLoading"
        :next-id="nextTaskId"
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
                <input v-model="adminPassword" type="password" class="form-control password-input" placeholder="비밀번호를 입력하세요" />
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

          <div class="settings-group">
            <label class="form-label">화면 설정</label>
            <div class="toggle-row mt-16">
              <label class="toggle-label">
                <input type="checkbox" v-model="showWeeklyProgress" @change="saveShowWeeklyProgress" />
                <span class="toggle-track"></span>
              </label>
              <span class="text-sm">주간 진행 현황 — <strong>이번 주 진행 내용</strong> 섹션 표시</span>
            </div>
            <p class="text-sm text-muted hint-text">비활성화 시 Q&A와 컨플루언스 링크만 표시됩니다.</p>
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
const staffViewRef = ref(null)

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
    const { data: nextId } = await axios.get('/api/okrs/next-id')
    nextObjectiveId.value = nextId.next_id
  } finally { loading.value = false }
}

async function fetchTasks() {
  taskLoading.value = true
  try {
    const { data } = await axios.get('/api/tasks')
    tasks.value = data
    const { data: nextId } = await axios.get('/api/tasks/next-id')
    nextTaskId.value = nextId.next_id
  } finally { taskLoading.value = false }
}

async function fetchStaff() {
  const { data } = await axios.get('/api/staff')
  staffList.value = data
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

const showWeeklyProgress = ref(false)
function saveShowWeeklyProgress() {
  localStorage.setItem('showWeeklyProgress', showWeeklyProgress.value ? 'true' : 'false')
  showToast(showWeeklyProgress.value ? '이번 주 진행 내용 섹션이 표시됩니다' : '이번 주 진행 내용 섹션이 숨겨집니다')
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
  showWeeklyProgress.value = localStorage.getItem('showWeeklyProgress') === 'true'
  if (route.query.tab) activeTab.value = route.query.tab
  await fetchAll()
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
.toggle-row { display: flex; align-items: center; gap: 12px; }
.hint-text { margin-top: 6px; }
.info-list { margin-top: 8px; }
.info-item { margin-top: 4px; }
</style>

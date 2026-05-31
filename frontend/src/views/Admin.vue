<template>
  <div>
    <div class="page-header">
      <div>
        <h2>관리 도구</h2>
        <div class="subtitle">목표 · Key Result · 과제 · 인력 관리</div>
      </div>
      <div v-if="auth.isAdmin" class="flex gap-8">
        <span class="badge badge-red">관리자</span>
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

      <!-- ── Reset Tab (admin only) ── -->
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

          <div class="form-group">
            <label class="form-label">정보</label>
            <div class="info-list text-sm text-muted">
              <div>버전: 1.0.0</div>
              <div class="info-item">개발자: Work Management Team</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Users Tab (admin only) ── -->
      <div v-if="activeTab === 'users'">
        <div class="card card-body">
          <h3 class="settings-heading">👤 사용자 관리</h3>
          <div v-if="usersLoading" class="text-muted text-sm">불러오는 중...</div>
          <table v-else class="users-table">
            <thead>
              <tr>
                <th>아이디</th>
                <th>이름</th>
                <th>직책</th>
                <th>관리자</th>
                <th>가입일</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in userList" :key="u.username">
                <td class="user-id">{{ u.username }}</td>
                <td>{{ u.name }}</td>
                <td>
                  <select :value="u.role" @change="changeRole(u.username, $event.target.value)" class="role-select">
                    <option value="member">파트원</option>
                    <option value="group_leader">그룹장</option>
                    <option value="part_leader">파트장</option>
                  </select>
                </td>
                <td>
                  <input
                    type="checkbox"
                    :checked="!!u.is_admin"
                    :disabled="u.username === auth.user?.username"
                    @change="toggleAdmin(u.username, $event.target.checked)"
                  />
                </td>
                <td class="text-muted text-sm">{{ u.created_at ? u.created_at.slice(0,10) : '-' }}</td>
                <td style="display:flex;gap:4px">
                  <button
                    class="btn btn-ghost btn-xs"
                    @click="resetPassword(u.username, u.name)"
                    data-tooltip="임시 비밀번호 발급"
                  >비번초기화</button>
                  <button
                    class="btn btn-danger btn-xs"
                    @click="deleteUser(u.username)"
                    :disabled="u.username === auth.user?.username"
                    data-tooltip="사용자 삭제"
                  >삭제</button>
                </td>
              </tr>
              <tr v-if="userList.length === 0">
                <td colspan="5" class="text-muted text-sm" style="text-align:center;padding:20px">등록된 사용자가 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>

    <!-- 임시 비밀번호 모달 -->
    <div v-if="tempPwModal.show" class="modal-backdrop" @click.self="tempPwModal.show = false">
      <div class="modal-card">
        <h3 style="margin:0 0 8px">임시 비밀번호 발급</h3>
        <p style="font-size:13px;color:var(--text-muted);margin:0 0 16px">
          <strong>{{ tempPwModal.name }}</strong> 님의 비밀번호가 초기화되었습니다.<br>
          아래 임시 비밀번호를 전달하세요. 로그인 후 변경이 강제됩니다.
        </p>
        <div class="temp-pw-box">{{ tempPwModal.password }}</div>
        <button class="btn btn-primary" style="width:100%;margin-top:16px" @click="copyTempPw">
          {{ copied ? '복사됨 ✓' : '클립보드에 복사' }}
        </button>
        <button class="btn btn-ghost" style="width:100%;margin-top:8px" @click="tempPwModal.show = false">닫기</button>
      </div>
    </div>
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
import { useAuthStore } from '../stores/auth.js'

const route = useRoute()
const auth = useAuthStore()

const tabs = computed(() => {
  const baseTabs = [
    { key: 'objective', label: '📊 목표' },
    { key: 'task', label: '📋 과제' },
    { key: 'staff', label: '👥 인력' },
    { key: 'settings', label: '⚙️ 설정' },
  ]
  if (auth.isAdmin) {
    baseTabs.push({ key: 'users', label: '👤 사용자 관리' })
    baseTabs.push({ key: 'reset', label: '🗑 초기화' })
  }
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

// ── 사용자 관리 ──
const userList = ref([])
const tempPwModal = ref({ show: false, name: '', password: '' })
const copied = ref(false)
const usersLoading = ref(false)

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
  } catch { /* 기본값 유지 */ }
}

async function fetchUsers() {
  usersLoading.value = true
  try {
    const { data } = await axios.get('/api/auth/users')
    userList.value = data
  } finally { usersLoading.value = false }
}

async function saveSettings() {
  await axios.put('/api/settings', { task_targets: taskTargets.value })
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

async function changeRole(username, role) {
  try {
    await axios.put(`/api/auth/users/${username}/role`, { role })
    // 역할 변경 후 재조회 (백엔드의 자동 staff 연결 결과 반영)
    await fetchUsers()
    showToast('직책이 변경되었습니다')
  } catch (e) {
    showToast('직책 변경 실패: ' + (e.response?.data?.detail || e.message))
    await fetchUsers()
  }
}

async function resetPassword(username, name) {
  if (!confirm(`'${name}' 님의 비밀번호를 초기화하시겠습니까?`)) return
  try {
    const { data } = await axios.post(`/api/auth/users/${username}/reset-password`)
    copied.value = false
    tempPwModal.value = { show: true, name, password: data.temp_password }
  } catch (e) {
    showToast('초기화 실패: ' + (e.response?.data?.detail || e.message))
  }
}

function copyTempPw() {
  navigator.clipboard.writeText(tempPwModal.value.password)
  copied.value = true
}


async function toggleAdmin(username, is_admin) {
  try {
    await axios.put(`/api/auth/users/${username}/admin`, { is_admin })
    const u = userList.value.find(x => x.username === username)
    if (u) u.is_admin = is_admin ? 1 : 0
    showToast(is_admin ? '관리자 권한이 부여되었습니다' : '관리자 권한이 해제되었습니다')
  } catch (e) {
    showToast('권한 변경 실패: ' + (e.response?.data?.detail || e.message))
    await fetchUsers()
  }
}

async function deleteUser(username) {
  if (!confirm(`'${username}' 사용자를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/auth/users/${username}`)
    userList.value = userList.value.filter(u => u.username !== username)
    showToast('삭제되었습니다')
  } catch (e) {
    showToast('삭제 실패: ' + (e.response?.data?.detail || e.message))
  }
}

async function fetchAll() {
  await Promise.all([fetchObjectives(), fetchTasks(), fetchStaff()])
}

function exportCsv(type) { window.open(`/api/admin/export/${type}`, '_blank') }

async function resetData(target) {
  const labels = { objectives: '목표', tasks: '과제', staff: '인력', progress: '진행도', all: '모든' }
  if (!confirm(`${labels[target]} 데이터를 전부 삭제하시겠습니까?`)) return
  await axios.delete(`/api/admin/reset/${target}`)
  showToast('초기화 완료')
  fetchAll()
}

onMounted(async () => {
  if (route.query.tab) activeTab.value = route.query.tab
  await Promise.all([fetchAll(), fetchSettings()])
  if (auth.isAdmin) fetchUsers()
})
</script>

<style scoped>
.tab-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }

.reset-heading { margin-bottom: 16px; color: var(--danger); }
.reset-desc { margin-bottom: 20px; }
.reset-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.settings-heading { margin-bottom: 24px; }
.settings-group { margin-bottom: 32px; }
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

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.users-table th, .users-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--outline);
  text-align: left;
}
.users-table th {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--gray-50);
}
.user-id { font-family: monospace; color: var(--text-secondary); }
.role-select {
  padding: 4px 8px;
  border: 1px solid var(--outline);
  border-radius: 6px;
  font-size: 13px;
  background: var(--background);
  color: var(--text);
  cursor: pointer;
}
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-card {
  background: var(--surface, #fff);
  border-radius: 12px;
  padding: 28px 32px;
  width: 340px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.temp-pw-box {
  background: var(--background, #f8fafc);
  border: 1px solid var(--outline, #e5e7eb);
  border-radius: 8px;
  padding: 14px 16px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 3px;
  text-align: center;
  color: var(--primary, #2563eb);
  font-family: monospace;
}
</style>

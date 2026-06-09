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

          <div class="settings-group">
            <label class="form-label">대시보드 기본 주차</label>
            <div class="week-radio-group mt-16">
              <label class="week-radio-label">
                <input type="radio" v-model="dashboardDefaultWeek" value="last" @change="saveDashboardDefaultWeek" />
                지난주
              </label>
              <label class="week-radio-label">
                <input type="radio" v-model="dashboardDefaultWeek" value="this" @change="saveDashboardDefaultWeek" />
                이번주
              </label>
            </div>
            <div class="text-sm text-muted" style="margin-top:6px">대시보드 초기 진입 시 의견/질문, 이슈, 활동 현황 패널에 표시되는 기본 주차입니다.</div>
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
          <div v-else class="users-table-wrap">
          <table class="users-table">
            <thead>
              <tr>
                <th>아이디</th>
                <th>이름</th>
                <th>직책</th>
                <th>관리자</th>
                <th>가입일</th>
                <th>최근 로그인</th>
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
                <td class="text-sm" :class="u.last_login ? '' : 'text-muted'">
                  {{ u.last_login ? u.last_login.slice(0,16).replace('T',' ') : '기록 없음' }}
                </td>
                <td style="display:flex;gap:4px">
                  <button
                    class="btn btn-ghost btn-xs"
                    @click="openHistory(u)"
                    data-tooltip="접속·사용 이력"
                  >
                    <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">history</span>이력
                  </button>
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
                <td colspan="7" class="text-muted text-sm" style="text-align:center;padding:20px">등록된 사용자가 없습니다</td>
              </tr>
            </tbody>
          </table>
          </div>
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

    <!-- 사용자 이력 모달 -->
    <div v-if="historyModal.show" class="modal-backdrop" @click.self="historyModal.show = false">
      <div class="modal-card history-modal-card">
        <div class="history-modal-header">
          <h3 class="history-modal-title">
            <span class="material-symbols-outlined">manage_accounts</span>
            {{ historyModal.name }} 활동 이력
          </h3>
          <button class="modal-close-btn" @click="historyModal.show = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div v-if="historyModal.loading" class="history-loading">
          <div class="spinner" style="margin:0 auto"></div>
        </div>
        <template v-else>
          <!-- 접속 이력 -->
          <div class="history-section">
            <div class="history-section-title">
              <span class="material-symbols-outlined">login</span>접속 이력
            </div>
            <div v-if="historyModal.data.login_log.length === 0" class="history-empty">기록 없음</div>
            <ul v-else class="login-log-list">
              <li v-for="(entry, i) in historyModal.data.login_log" :key="i" class="login-log-item">
                <span class="material-symbols-outlined login-dot">fiber_manual_record</span>
                {{ entry.logged_in_at.slice(0,16).replace('T',' ') }}
              </li>
            </ul>
          </div>

          <!-- 사용 현황 -->
          <div class="history-section">
            <div class="history-section-title">
              <span class="material-symbols-outlined">insights</span>사용 현황
            </div>
            <div class="history-stats">
              <div class="history-stat-item">
                <span class="stat-label">이슈 등록</span>
                <span class="stat-value">{{ historyModal.data.stats.issues_created }}건</span>
              </div>
              <div class="history-stat-divider"></div>
              <div class="history-stat-item">
                <span class="stat-label">댓글 작성</span>
                <span class="stat-value">{{ historyModal.data.stats.task_comments + historyModal.data.stats.issue_comments }}건</span>
              </div>
            </div>
            <div v-if="historyModal.data.stats.last_activity_at" class="history-last-activity">
              마지막 활동: {{ historyModal.data.stats.last_activity_at.slice(0,16).replace('T',' ') }}
            </div>
            <div v-else class="history-empty">활동 기록 없음</div>
          </div>
        </template>
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
const dashboardDefaultWeek = ref('last')

// ── 사용자 관리 ──
const userList = ref([])
const tempPwModal = ref({ show: false, name: '', password: '' })
const copied = ref(false)
const usersLoading = ref(false)
const historyModal = ref({
  show: false, loading: false, name: '',
  data: { login_log: [], stats: { issues_created: 0, task_comments: 0, issue_comments: 0, last_activity_at: null } },
})

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
    if (data.dashboard_default_week) dashboardDefaultWeek.value = data.dashboard_default_week
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

async function saveDashboardDefaultWeek() {
  await axios.put('/api/settings', { dashboard_default_week: dashboardDefaultWeek.value })
  showToast('저장되었습니다')
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

async function openHistory(u) {
  historyModal.value = {
    show: true, loading: true, name: u.name,
    data: { login_log: [], stats: { issues_created: 0, task_comments: 0, issue_comments: 0, last_activity_at: null } },
  }
  try {
    const { data } = await axios.get(`/api/auth/users/${u.username}/history`)
    historyModal.value.data = data
  } catch (e) {
    showToast('이력 조회 실패: ' + (e.response?.data?.detail || e.message))
    historyModal.value.show = false
  } finally {
    historyModal.value.loading = false
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

.settings-heading { margin-bottom: 24px; }
.settings-group { margin-bottom: 32px; }
.info-list { margin-top: 8px; }
.info-item { margin-top: 4px; }

.target-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.target-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 999px;
  background: var(--primary-light); color: var(--primary);
  border: 1px solid var(--primary); font-size: var(--fs-sm); font-weight: var(--fw-semibold);
}
.target-chip-del {
  display: flex; align-items: center; justify-content: center;
  width: 16px; height: 16px; border-radius: 50%;
  border: none; background: transparent; color: var(--primary);
  cursor: pointer; font-size: var(--fs-2xs); padding: 0;
  transition: background 0.15s;
}
.target-chip-del:hover { background: var(--primary); color: #fff; }
.target-add-form { display: flex; gap: 8px; align-items: center; }
.target-add-form .form-control { max-width: 200px; }

.week-radio-group { display: flex; gap: 20px; }
.week-radio-label { display: inline-flex; align-items: center; gap: 6px; font-size: var(--fs-md); cursor: pointer; }

.users-table-wrap { overflow-x: auto; }
.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--fs-md);
  white-space: nowrap;
}
.users-table th, .users-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--outline);
  text-align: left;
}
.users-table th {
  font-size: var(--fs-xs);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  background: var(--gray-50);
}
.user-id { font-family: monospace; color: var(--text-secondary); }
.role-select {
  padding: 4px 8px;
  border: 1px solid var(--outline);
  border-radius: 6px;
  font-size: var(--fs-sm);
  background: var(--bg-main);
  color: var(--text-primary);
  cursor: pointer;
}
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-card {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 28px 32px;
  width: 340px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.temp-pw-box {
  background: var(--bg-main);
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  font-size: 22px;
  font-weight: var(--fw-bold);
  letter-spacing: 3px;
  text-align: center;
  color: var(--primary);
  font-family: monospace;
}

/* 이력 모달 */
.history-modal-card {
  width: 420px;
  max-height: 80vh;
  overflow-y: auto;
  padding: 24px 28px;
}
.history-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.history-modal-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-h3);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  margin: 0;
}
.history-modal-title .material-symbols-outlined { font-size: 20px; color: var(--primary); }
.modal-close-btn {
  background: none; border: none; cursor: pointer;
  color: var(--text-muted); padding: 4px; border-radius: var(--radius-sm);
  display: flex; align-items: center;
}
.modal-close-btn:hover { background: var(--gray-100); }
.history-loading { padding: 32px 0; display: flex; justify-content: center; }
.history-section {
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-bottom: 12px;
}
.history-section:last-child { margin-bottom: 0; }
.history-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-xs);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  padding: 8px 12px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--outline);
}
.history-section-title .material-symbols-outlined { font-size: 14px; }
.history-empty {
  padding: 14px 14px;
  font-size: var(--fs-sm);
  color: var(--text-muted);
}
.login-log-list {
  list-style: none;
  margin: 0; padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 220px;
  overflow-y: auto;
}
.login-log-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-sm);
  color: var(--text-secondary);
}
.login-dot {
  font-size: 7px !important;
  color: var(--primary);
  flex-shrink: 0;
}
.history-stats {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 14px 16px;
  border-bottom: 1px solid var(--outline);
}
.history-stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  text-align: center;
}
.history-stat-divider {
  width: 1px;
  height: 32px;
  background: var(--outline);
  flex-shrink: 0;
}
.stat-label {
  font-size: var(--fs-xs);
  color: var(--text-muted);
}
.stat-value {
  font-size: var(--fs-h3);
  font-weight: var(--fw-bold);
  color: var(--primary);
}
.history-last-activity {
  padding: 8px 14px;
  font-size: var(--fs-xs);
  color: var(--text-muted);
}
</style>

<template>
  <div>
    <div class="grid-4" style="margin-bottom:20px">
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">전체 목표</div>
      </div></div>
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value" style="color:var(--primary)">{{ stats.inProgress }}</div>
        <div class="stat-label">진행중</div>
      </div></div>
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value" style="color:#22c55e">{{ stats.done }}</div>
        <div class="stat-label">완료</div>
      </div></div>
      <div class="card"><div class="card-body stat-card">
        <div class="stat-value" style="color:var(--danger)">{{ stats.danger }}</div>
        <div class="stat-label">위험</div>
      </div></div>
    </div>

    <div class="flex-between" style="margin-bottom:16px">
      <button class="btn btn-ghost btn-sm" @click="exportCsv" data-tooltip="목표 목록을 CSV 파일로 내보내기">⬇ CSV 다운로드</button>
      <button class="btn btn-primary btn-sm" @click="openModal()" data-tooltip="새 목표(Objective) 추가">+ 목표 추가</button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="objectives.length === 0" class="empty-state">
        <div class="empty-icon">📊</div><p>등록된 목표가 없습니다.</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th @click="sortBy('id')" style="cursor:pointer">ID <span v-if="sortKey === 'id'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('name')" style="cursor:pointer">목표명 <span v-if="sortKey === 'name'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('key_results.length')" style="cursor:pointer">Key Results <span v-if="sortKey === 'key_results.length'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
              <th>연결 과제</th>
              <th>참여 인력</th>
              <th @click="sortBy('status')" style="cursor:pointer">상태 <span v-if="sortKey === 'status'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in sortedObjectives" :key="o.id">
              <td><span class="badge badge-blue">{{ o.id }}</span></td>
              <td style="font-weight:600">{{ o.name }}</td>
              <td>
                <div class="text-sm">
                  {{ o.key_results?.length || 0 }}개
                  <button class="btn btn-ghost btn-xs" @click.stop="openKrModal(o)" style="margin-left:4px" data-tooltip="Key Results 관리">+ KR</button>
                </div>
                <div v-if="o.key_results?.length > 0" class="key-result-list">
                  <div v-for="kr in o.key_results" :key="kr.id" class="text-xs text-muted" style="margin-top:2px;padding-left:8px;border-left:2px solid var(--outline)">
                    <span class="text-xs" style="color:var(--primary)">{{ kr.id }}</span> {{ kr.name }}
                  </div>
                </div>
              </td>
              <td>
                <div v-if="getObjectiveTasks(o.id).length" class="task-list">
                  <div v-for="t in getObjectiveTasks(o.id)" :key="t.id" class="task-list-item">
                    <span class="badge badge-blue" style="flex-shrink:0">{{ t.id }}</span>
                    <span class="task-name">{{ t.name }}</span>
                  </div>
                </div>
                <span v-else class="text-muted text-sm">-</span>
              </td>
              <td style="max-width:200px">
                <div v-if="getObjectiveStaff(o.id).length" class="member-chips">
                  <span v-for="s in getObjectiveStaff(o.id)" :key="s.id" class="badge badge-gray" :title="s.role">{{ s.name }}</span>
                </div>
                <span v-else class="text-muted text-sm">-</span>
              </td>
              <td><span :class="sBadge(o.status)">{{ o.status }}</span></td>
              <td>
                <div style="display:flex;gap:8px">
                  <button class="btn btn-ghost btn-xs" @click="openModal(o)" data-tooltip="목표 정보 수정">수정</button>
                  <button class="btn btn-danger btn-xs" @click="deleteObjective(o)" data-tooltip="목표 삭제">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Objective Form Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingId ? 'Objective 수정' : 'Objective 추가' }}</h3>
          <button class="modal-close" @click="showModal = false" data-tooltip="닫기">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">목표 ID</label>
            <input v-model="form.id" class="form-control" :placeholder="nextId" disabled />
            <span class="text-sm text-muted">자동 생성</span>
          </div>
          <div class="form-group">
            <label class="form-label">목표명 *</label>
            <input v-model="form.name" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">기술 스택</label>
            <input v-model="form.tech_stack" class="form-control" placeholder="Python, PyTorch, ..." />
          </div>
          <div class="form-group">
            <label class="form-label">상태</label>
            <select v-model="form.status" class="form-control">
              <option>진행중</option><option>완료</option><option>위험</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showModal = false" data-tooltip="변경사항 취소">취소</button>
          <button class="btn btn-primary" @click="submitObjective" :disabled="!form.name" data-tooltip="목표 저장">저장</button>
        </div>
      </div>
    </div>

    <!-- Key Result Modal -->
    <div v-if="showKrModal" class="modal-overlay" @click.self="showKrModal = false">
      <div class="modal" style="max-width:640px">
        <div class="modal-header">
          <h3>Key Results - {{ selectedObjective?.id }}: {{ selectedObjective?.name }}</h3>
          <button class="modal-close" @click="showKrModal = false" data-tooltip="닫기">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedObjective?.key_results?.length > 0" style="margin-bottom:16px">
            <div class="text-sm text-muted" style="margin-bottom:8px">등록된 Key Results:</div>
            <div v-for="kr in selectedObjective.key_results" :key="kr.id" class="kr-edit-item">
              <div class="flex gap-8" style="align-items:center">
                <span class="badge badge-blue" style="width:50px">{{ kr.id }}</span>
                <input v-model="kr.name" class="form-control" placeholder="Key Result 내용" style="flex:1" @input="onKrInput(kr)" />
                <button v-if="kr.isModified" class="btn btn-primary btn-xs" @click="updateKr(kr)" style="min-width:60px" data-tooltip="수정 내용 저장">수정</button>
                <button v-else class="btn btn-danger btn-xs" @click="deleteKr(kr.id)" data-tooltip="Key Result 삭제">✕</button>
              </div>
            </div>
          </div>
          <div class="text-sm text-muted" style="margin-bottom:8px">새 Key Result 추가:</div>
          <div class="flex gap-8" style="align-items:center">
            <input v-model="newKrName" class="form-control" placeholder="Key Result 내용" style="flex:1" />
            <button class="btn btn-primary btn-xs" @click="addKr" :disabled="!newKrName" data-tooltip="Key Result 추가">추가</button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showKrModal = false">닫기</button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useToast } from '../../composables/useToast.js'
import { parseIds } from '../../utils/parseIds.js'

const props = defineProps({
  objectives: { type: Array, default: () => [] },
  tasks: { type: Array, default: () => [] },
  staffList: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  nextId: { type: String, default: 'O1' },
})
const emit = defineEmits(['refresh'])
const { toastMsg, showToast } = useToast()

// ── 통계 ──
const stats = computed(() => ({
  total: props.objectives.length,
  inProgress: props.objectives.filter(o => o.status === '진행중').length,
  done: props.objectives.filter(o => o.status === '완료').length,
  danger: props.objectives.filter(o => o.status === '위험').length,
}))

// ── 정렬 ──
const sortKey = ref('')
const sortOrder = ref('asc')
function sortBy(key) {
  if (sortKey.value === key) {
    if (sortOrder.value === 'asc') sortOrder.value = 'desc'
    else { sortKey.value = ''; sortOrder.value = 'asc' }
  } else {
    sortKey.value = key; sortOrder.value = 'asc'
  }
}
const sortedObjectives = computed(() => {
  if (!sortKey.value) return props.objectives
  return [...props.objectives].sort((a, b) => {
    let aVal = sortKey.value === 'key_results.length' ? (a.key_results?.length || 0) : a[sortKey.value]
    let bVal = sortKey.value === 'key_results.length' ? (b.key_results?.length || 0) : b[sortKey.value]
    if (typeof aVal === 'string') { aVal = aVal.toLowerCase(); bVal = bVal.toLowerCase() }
    const r = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
    return sortOrder.value === 'asc' ? r : -r
  })
})

// ── 헬퍼 ──
function getObjectiveTasks(id) { return props.tasks.filter(t => t.objective_id === id) }
function getObjectiveStaff(id) { return props.staffList.filter(s => parseIds(s.okrs).includes(id)) }
function sBadge(s) {
  return { '진행중': 'badge badge-blue', '완료': 'badge badge-green', '위험': 'badge badge-red' }[s] || 'badge badge-gray'
}
function exportCsv() { window.open('/api/admin/export/objectives', '_blank') }

// ── Objective Form Modal ──
const showModal = ref(false)
const editingId = ref(null)
const defaultForm = () => ({ id: '', name: '', tech_stack: '', status: '진행중' })
const form = ref(defaultForm())

function openModal(o = null) {
  if (o) {
    form.value = { ...o }
    editingId.value = o.id
  } else {
    form.value = { ...defaultForm(), id: props.nextId }
    editingId.value = null
  }
  showModal.value = true
}

async function submitObjective() {
  try {
    if (editingId.value) {
      await axios.put(`/api/okrs/${editingId.value}`, form.value)
    } else {
      await axios.post('/api/okrs', form.value)
    }
    showModal.value = false
    showToast('저장되었습니다')
    emit('refresh')
  } catch (e) {
    showToast(e.response?.data?.detail || '저장 실패')
  }
}

async function deleteObjective(o) {
  if (!confirm(`"${o.id}: ${o.name}"을(를) 삭제하시겠습니까?`)) return
  await axios.delete(`/api/okrs/${o.id}`)
  showToast('삭제되었습니다')
  emit('refresh')
}

// ── Key Result Modal ──
const showKrModal = ref(false)
const selectedObjective = ref(null)
const newKrName = ref('')

function openKrModal(o) {
  selectedObjective.value = JSON.parse(JSON.stringify(o))
  selectedObjective.value.key_results?.forEach(kr => { kr.originalName = kr.name; kr.isModified = false })
  newKrName.value = ''
  showKrModal.value = true
}

function onKrInput(kr) {
  if (kr.originalName === undefined) kr.originalName = kr.name
  kr.isModified = kr.name !== kr.originalName
}

async function updateKr(kr) {
  try {
    await axios.put(`/api/okrs/${selectedObjective.value.id}/key-results/${kr.id}`, { name: kr.name })
    kr.originalName = kr.name; kr.isModified = false
    showToast('Key Result가 수정되었습니다')
    emit('refresh')
  } catch { showToast('수정 실패') }
}

async function addKr() {
  if (!newKrName.value) return
  try {
    const { data } = await axios.post(`/api/okrs/${selectedObjective.value.id}/key-results`, { name: newKrName.value })
    selectedObjective.value.key_results.push(data)
    newKrName.value = ''
    showToast('Key Result가 추가되었습니다')
    emit('refresh')
  } catch (e) { showToast(e.response?.data?.detail || '추가 실패') }
}

async function deleteKr(krId) {
  try {
    await axios.delete(`/api/okrs/${selectedObjective.value.id}/key-results/${krId}`)
    selectedObjective.value.key_results = selectedObjective.value.key_results.filter(kr => kr.id !== krId)
    showToast('삭제되었습니다')
    emit('refresh')
  } catch { showToast('삭제 실패') }
}
</script>

<style scoped>
.kr-edit-item {
  background: var(--gray-50);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 8px;
}
.member-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.task-list { display: flex; flex-direction: column; gap: 4px; }
.task-list-item { display: flex; align-items: center; gap: 6px; }
.task-name { color: var(--text-primary); font-size: 13px; line-height: 1.4; }
</style>

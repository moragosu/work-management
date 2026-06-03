<template>
  <div class="okr-tab">

    <!-- 툴바 -->
    <div class="tab-toolbar">
      <div class="okr-stats">
        <span class="stat-chip">목표 <strong>{{ objectives.length }}</strong>개</span>
        <span class="stat-chip">과제 <strong>{{ tasks.length }}</strong>개</span>
        <span class="stat-chip">인력 <strong>{{ staffList.length }}</strong>명</span>
      </div>
      <button class="btn btn-primary btn-sm" @click="openModal('add-obj')">
        <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">add</span>
        목표 추가
      </button>
    </div>

    <div v-if="loading" class="loading-center" style="padding:48px"><div class="spinner"></div></div>

    <div v-else class="okr-body">

      <!-- ── 목표별 섹션 ── -->
      <div v-for="obj in objectives" :key="obj.id" class="obj-section card">

        <!-- 목표 헤더 -->
        <div class="obj-header">
          <span class="obj-id-badge">{{ obj.id }}</span>
          <span class="obj-name">{{ obj.name }}</span>
          <span class="badge" :class="statusBadge(obj.status)">{{ obj.status }}</span>
          <div class="obj-actions">
            <button class="btn btn-ghost btn-xs" @click="openModal('edit-obj', { obj })">
              <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">edit</span>수정
            </button>
            <button class="btn btn-danger btn-xs" @click="deleteObjective(obj)">삭제</button>
          </div>
        </div>

        <!-- KR 행 -->
        <div class="kr-row">
          <span class="kr-label">KR</span>
          <div v-for="kr in obj.key_results" :key="kr.id" class="kr-chip">
            <span @click="openModal('edit-kr', { obj, kr })" class="kr-text" data-tooltip="KR 수정">{{ kr.name }}</span>
            <button class="chip-del" @click="deleteKr(obj, kr.id)" data-tooltip="KR 삭제">✕</button>
          </div>
          <span v-if="!obj.key_results?.length" class="text-muted" style="font-size:12px">KR 없음</span>
          <button class="btn-add-action" @click="openModal('add-kr', { obj })">+ KR</button>
        </div>

        <!-- 과제 목록 -->
        <div class="task-list">
          <div v-for="task in getTasksForObj(obj.id)" :key="task.id" class="task-block">

            <!-- 과제 행 -->
            <div class="task-row">
              <span class="task-id-badge">{{ task.id }}</span>
              <span class="task-name">{{ task.name }}</span>
              <span v-if="task.target" class="badge badge-target">{{ task.target }}</span>

              <!-- 담당자 칩 -->
              <div class="member-chip-group">
                <span v-for="m in task.members" :key="m.username" class="member-chip">
                  {{ m.name }}
                  <button class="chip-del" @click="removeMember(task, m.username)">✕</button>
                </span>
                <div class="dropdown-wrapper">
                  <button class="btn-add-action" @click.stop="toggleDropdown(task.id)">+ 담당자</button>
                  <div v-if="dropdownId === task.id" class="member-dropdown">
                    <div v-if="availableStaff(task.members).length === 0" class="dropdown-empty">추가할 인력이 없습니다</div>
                    <div v-for="s in availableStaff(task.members)" :key="s.id"
                         class="dropdown-item" @click="addMember(task, s)">{{ s.name }}</div>
                  </div>
                </div>
              </div>

              <div class="task-actions">
                <button class="btn btn-ghost btn-xs" @click="openModal('edit-task', { task })">
                  <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">edit</span>수정
                </button>
                <button class="btn btn-danger btn-xs" @click="deleteTask(task)">삭제</button>
              </div>
            </div>

            <!-- 소과제 목록 -->
            <div v-if="task.sub_tasks?.length" class="subtask-list">
              <div v-for="st in task.sub_tasks" :key="st.id" class="subtask-row">
                <input type="checkbox" class="subtask-check" :checked="st.done"
                       @change="toggleSubDone(task, st)" />
                <span class="subtask-id-badge">{{ st.id }}</span>
                <span class="subtask-name" :class="{ done: st.done }">{{ st.name }}</span>
                <span v-if="st.target" class="badge badge-target" style="font-size:10px">{{ st.target }}</span>

                <!-- 소과제 담당자 칩 -->
                <div class="member-chip-group">
                  <span v-for="m in st.members" :key="m.username" class="member-chip member-chip-sm">
                    {{ m.name }}
                    <button class="chip-del" @click="removeSubMember(task, st, m.username)">✕</button>
                  </span>
                  <div class="dropdown-wrapper">
                    <button class="btn-add-action" @click.stop="toggleDropdown(st.id)">+ 담당자</button>
                    <div v-if="dropdownId === st.id" class="member-dropdown">
                      <div v-if="availableStaff(st.members).length === 0" class="dropdown-empty">추가할 인력이 없습니다</div>
                      <div v-for="s in availableStaff(st.members)" :key="s.id"
                           class="dropdown-item" @click="addSubMember(task, st, s)">{{ s.name }}</div>
                    </div>
                  </div>
                </div>

                <div class="task-actions">
                  <button class="btn btn-ghost btn-xs" @click="openModal('edit-subtask', { task, st })">
                    <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">edit</span>수정
                  </button>
                  <button class="btn btn-danger btn-xs" @click="deleteSubTask(task, st.id)">삭제</button>
                </div>
              </div>
            </div>

            <!-- 소과제 추가 -->
            <div class="add-row subtask-add-row">
              <button class="btn-add-action" @click="openModal('add-subtask', { task })">+ 소과제</button>
            </div>

          </div>

          <!-- 과제 추가 -->
          <div class="add-row task-add-row">
            <button class="btn-add-action" @click="openModal('add-task', { obj })">+ 과제</button>
          </div>
        </div>
      </div>

      <!-- 미연결 과제 섹션 -->
      <div v-if="unlinkedTasks.length > 0" class="unlinked-section card">
        <div class="unlinked-header" @click="unlinkedOpen = !unlinkedOpen">
          <span class="material-symbols-outlined unlinked-chevron" :class="{ open: unlinkedOpen }">expand_more</span>
          <span class="unlinked-title">미연결 과제</span>
          <span class="badge badge-gray">{{ unlinkedTasks.length }}개</span>
        </div>
        <div v-if="unlinkedOpen" class="task-list" style="padding:0 16px 16px">
          <div v-for="task in unlinkedTasks" :key="task.id" class="task-block">
            <div class="task-row">
              <span class="task-id-badge">{{ task.id }}</span>
              <span class="task-name">{{ task.name }}</span>
              <span v-if="task.target" class="badge badge-target">{{ task.target }}</span>
              <div class="member-chip-group">
                <span v-for="m in task.members" :key="m.username" class="member-chip">
                  {{ m.name }}<button class="chip-del" @click="removeMember(task, m.username)">✕</button>
                </span>
                <div class="dropdown-wrapper">
                  <button class="btn-add-action" @click.stop="toggleDropdown(task.id)">+ 담당자</button>
                  <div v-if="dropdownId === task.id" class="member-dropdown">
                    <div v-if="availableStaff(task.members).length === 0" class="dropdown-empty">추가할 인력이 없습니다</div>
                    <div v-for="s in availableStaff(task.members)" :key="s.id"
                         class="dropdown-item" @click="addMember(task, s)">{{ s.name }}</div>
                  </div>
                </div>
              </div>
              <div class="task-actions">
                <button class="btn btn-ghost btn-xs" @click="openModal('edit-task', { task })">
                  <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">edit</span>수정
                </button>
                <button class="btn btn-danger btn-xs" @click="deleteTask(task)">삭제</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="objectives.length === 0" class="panel-empty" style="padding:48px;text-align:center">
        등록된 목표가 없습니다. 목표 추가 버튼을 눌러 시작하세요.
      </div>
    </div>

    <!-- ── 모달 ── -->
    <div v-if="modal.show" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-card">
        <h3 class="modal-title">{{ modalTitle }}</h3>

        <!-- 목표 추가/수정 -->
        <template v-if="modal.mode === 'add-obj' || modal.mode === 'edit-obj'">
          <div class="form-group">
            <label class="form-label">목표명 <span class="required">*</span></label>
            <input class="form-control" v-model="form.name" placeholder="목표명을 입력하세요" autofocus
                   @keyup.enter="submitModal" />
          </div>
          <div class="form-group">
            <label class="form-label">상태</label>
            <select class="form-control" v-model="form.status">
              <option value="진행중">진행중</option>
              <option value="완료">완료</option>
              <option value="위험">위험</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">기술 스택</label>
            <input class="form-control" v-model="form.tech_stack" placeholder="Python, Vue, ..." />
          </div>
        </template>

        <!-- KR 추가/수정 -->
        <template v-if="modal.mode === 'add-kr' || modal.mode === 'edit-kr'">
          <div class="form-group">
            <label class="form-label">KR 내용 <span class="required">*</span></label>
            <input class="form-control" v-model="form.name" placeholder="Key Result 내용" autofocus
                   @keyup.enter="submitModal" />
          </div>
        </template>

        <!-- 과제 추가/수정 -->
        <template v-if="modal.mode === 'add-task' || modal.mode === 'edit-task'">
          <div class="form-group">
            <label class="form-label">과제명 <span class="required">*</span></label>
            <input class="form-control" v-model="form.name" placeholder="과제명을 입력하세요" autofocus
                   @keyup.enter="submitModal" />
          </div>
          <div class="form-group">
            <label class="form-label">적용 대상</label>
            <select class="form-control" v-model="form.target">
              <option value="">없음</option>
              <option v-for="t in taskTargets" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div v-if="modal.mode === 'edit-task'" class="form-group">
            <label class="form-label">목표 연결</label>
            <select class="form-control" v-model="form.objective_id">
              <option value="">미연결</option>
              <option v-for="o in objectives" :key="o.id" :value="o.id">{{ o.id }}: {{ o.name }}</option>
            </select>
          </div>
        </template>

        <!-- 소과제 추가/수정 -->
        <template v-if="modal.mode === 'add-subtask' || modal.mode === 'edit-subtask'">
          <div class="form-group">
            <label class="form-label">소과제명 <span class="required">*</span></label>
            <input class="form-control" v-model="form.name" placeholder="소과제명을 입력하세요" autofocus
                   @keyup.enter="submitModal" />
          </div>
          <div class="form-group">
            <label class="form-label">적용 대상</label>
            <select class="form-control" v-model="form.target">
              <option value="">없음</option>
              <option v-for="t in taskTargets" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </template>

        <div class="modal-footer">
          <button class="btn btn-ghost btn-sm" @click="closeModal">취소</button>
          <button class="btn btn-primary btn-sm" :disabled="!form.name?.trim()" @click="submitModal">
            {{ modal.mode.startsWith('add') ? '추가' : '저장' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from '../../composables/useToast.js'

const props = defineProps({
  objectives:  { type: Array, default: () => [] },
  tasks:       { type: Array, default: () => [] },
  staffList:   { type: Array, default: () => [] },
  taskTargets: { type: Array, default: () => [] },
  loading:     { type: Boolean, default: false },
  nextObjId:   { type: String, default: 'O1' },
  nextTaskId:  { type: String, default: 'T1' },
})
const emit = defineEmits(['refresh'])
const { toastMsg, showToast } = useToast(2000)

// ── 모달 상태 ─────────────────────────────────────────────────────────
const modal = ref({ show: false, mode: '', ctx: {} })
const form  = ref({})

const modalTitles = {
  'add-obj':     '목표 추가',
  'edit-obj':    '목표 수정',
  'add-kr':      'KR 추가',
  'edit-kr':     'KR 수정',
  'add-task':    '과제 추가',
  'edit-task':   '과제 수정',
  'add-subtask': '소과제 추가',
  'edit-subtask':'소과제 수정',
}
const modalTitle = computed(() => modalTitles[modal.value.mode] || '')

function openModal(mode, ctx = {}) {
  modal.value = { show: true, mode, ctx }
  if (mode === 'edit-obj') {
    form.value = { name: ctx.obj.name, status: ctx.obj.status, tech_stack: ctx.obj.tech_stack || '' }
  } else if (mode === 'edit-kr') {
    form.value = { name: ctx.kr.name }
  } else if (mode === 'edit-task') {
    form.value = { name: ctx.task.name, target: ctx.task.target || '', objective_id: ctx.task.objective_id || '' }
  } else if (mode === 'edit-subtask') {
    form.value = { name: ctx.st.name, target: ctx.st.target || '' }
  } else {
    form.value = { name: '', target: '', status: '진행중', tech_stack: '', objective_id: '' }
  }
}

function closeModal() {
  modal.value = { show: false, mode: '', ctx: {} }
  form.value = {}
}

async function submitModal() {
  const { mode, ctx } = modal.value
  try {
    if (mode === 'add-obj')      await addObjective()
    else if (mode === 'edit-obj')     await saveObjective(ctx.obj)
    else if (mode === 'add-kr')       await addKr(ctx.obj)
    else if (mode === 'edit-kr')      await saveKr(ctx.obj, ctx.kr)
    else if (mode === 'add-task')     await addTask(ctx.obj)
    else if (mode === 'edit-task')    await saveTask(ctx.task)
    else if (mode === 'add-subtask')  await addSubTask(ctx.task)
    else if (mode === 'edit-subtask') await saveSubTask(ctx.task, ctx.st)
    closeModal()
    emit('refresh')
  } catch { showToast('저장 실패') }
}

// ── 드롭다운 ──────────────────────────────────────────────────────────
const dropdownId = ref(null)
function toggleDropdown(id) { dropdownId.value = dropdownId.value === id ? null : id }
function closeDropdown() { dropdownId.value = null }
onMounted(() => document.addEventListener('click', closeDropdown))
onUnmounted(() => document.removeEventListener('click', closeDropdown))

// ── computed ──────────────────────────────────────────────────────────
function getTasksForObj(objId) {
  return props.tasks.filter(t => t.objective_id === objId)
}
const unlinkedTasks = computed(() => props.tasks.filter(t => !t.objective_id))
const unlinkedOpen  = ref(true)

function availableStaff(currentMembers) {
  const taken = new Set((currentMembers || []).map(m => m.username))
  return props.staffList.filter(s => !taken.has(s.username))
}

function statusBadge(status) {
  return { '진행중': 'badge-blue', '완료': 'badge-green', '위험': 'badge-red' }[status] || 'badge-gray'
}

// ── 목표 ──────────────────────────────────────────────────────────────
async function addObjective() {
  await axios.post('/api/okrs', {
    id: props.nextObjId, name: form.value.name.trim(),
    status: form.value.status || '진행중',
    tech_stack: form.value.tech_stack || '',
    key_results: [],
  })
  showToast('목표가 추가되었습니다')
}

async function saveObjective(obj) {
  await axios.put(`/api/okrs/${obj.id}`, {
    name: form.value.name.trim(),
    status: form.value.status,
    tech_stack: form.value.tech_stack,
  })
}

async function deleteObjective(obj) {
  if (!confirm(`'${obj.name}' 목표를 삭제하시겠습니까?\n연결된 과제의 목표 연결이 해제됩니다.`)) return
  await axios.delete(`/api/okrs/${obj.id}`)
  emit('refresh')
  showToast('삭제되었습니다')
}

// ── KR ────────────────────────────────────────────────────────────────
async function addKr(obj) {
  await axios.post(`/api/okrs/${obj.id}/key-results`, { name: form.value.name.trim() })
  showToast('KR이 추가되었습니다')
}

async function saveKr(obj, kr) {
  await axios.put(`/api/okrs/${obj.id}/key-results/${kr.id}`, { name: form.value.name.trim() })
}

async function deleteKr(obj, krId) {
  if (!confirm('KR을 삭제하시겠습니까?')) return
  await axios.delete(`/api/okrs/${obj.id}/key-results/${krId}`)
  emit('refresh')
}

// ── 과제 ──────────────────────────────────────────────────────────────
async function addTask(obj) {
  await axios.post('/api/tasks', {
    id: props.nextTaskId, name: form.value.name.trim(),
    objective_id: obj.id, target: form.value.target || '',
    members: [], sub_tasks: [],
  })
  showToast('과제가 추가되었습니다')
}

async function saveTask(task) {
  await axios.put(`/api/tasks/${task.id}`, {
    name: form.value.name.trim(),
    target: form.value.target,
    objective_id: form.value.objective_id,
  })
}

async function deleteTask(task) {
  if (!confirm(`'${task.name}' 과제를 삭제하시겠습니까?`)) return
  await axios.delete(`/api/tasks/${task.id}`)
  emit('refresh')
  showToast('삭제되었습니다')
}

// ── 담당자 ────────────────────────────────────────────────────────────
async function addMember(task, staff) {
  dropdownId.value = null
  const members = [...(task.members || []), { username: staff.username, name: staff.name, role: '' }]
  await axios.put(`/api/tasks/${task.id}`, { members })
  emit('refresh')
}

async function removeMember(task, username) {
  const members = (task.members || []).filter(m => m.username !== username)
  await axios.put(`/api/tasks/${task.id}`, { members })
  emit('refresh')
}

// ── 소과제 ────────────────────────────────────────────────────────────
async function addSubTask(task) {
  const existing = task.sub_tasks || []
  const maxNum = existing.reduce((m, st) => Math.max(m, parseInt(st.id.split('-')[1]) || 0), 0)
  const newId = `${task.id}-${maxNum + 1}`
  const sub_tasks = [...existing, { id: newId, name: form.value.name.trim(), done: false, members: [], target: form.value.target || '' }]
  await axios.put(`/api/tasks/${task.id}`, { sub_tasks })
  showToast('소과제가 추가되었습니다')
}

async function saveSubTask(task, st) {
  await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, {
    name: form.value.name.trim(),
    target: form.value.target,
  })
}

async function toggleSubDone(task, st) {
  await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { done: !st.done })
  emit('refresh')
}

async function deleteSubTask(task, stId) {
  if (!confirm('소과제를 삭제하시겠습니까?')) return
  await axios.delete(`/api/tasks/${task.id}/sub-tasks/${stId}`)
  emit('refresh')
  showToast('삭제되었습니다')
}

// ── 소과제 담당자 ──────────────────────────────────────────────────────
async function addSubMember(task, st, staff) {
  dropdownId.value = null
  const members = [...(st.members || []), { username: staff.username, name: staff.name, role: '' }]
  await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { members })
  emit('refresh')
}

async function removeSubMember(task, st, username) {
  const members = (st.members || []).filter(m => m.username !== username)
  await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { members })
  emit('refresh')
}
</script>

<style scoped>
.okr-tab { display: flex; flex-direction: column; gap: 16px; }

/* ── 툴바 ── */
.tab-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.okr-stats { display: flex; gap: 12px; }
.stat-chip { font-size: 13px; color: var(--text-secondary); }
.stat-chip strong { color: var(--text-primary); }

/* ── 목표 섹션 ── */
.obj-section { margin-bottom: 12px; overflow: visible; }

.obj-header {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  padding: 14px 16px;
  border-bottom: 1px solid var(--outline);
  background: var(--gray-50, #f8fafc);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.obj-id-badge {
  font-size: 12px; font-weight: 700;
  background: var(--primary); color: #fff;
  padding: 2px 8px; border-radius: 999px; flex-shrink: 0;
}
.obj-name { font-size: 15px; font-weight: 600; flex: 1; }
.obj-actions { margin-left: auto; display: flex; gap: 6px; }

/* ── KR ── */
.kr-row {
  display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
  padding: 10px 16px; border-bottom: 1px solid var(--outline);
}
.kr-label { font-size: 11px; font-weight: 600; color: var(--text-muted); margin-right: 2px; flex-shrink: 0; }
.kr-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 8px; border-radius: 999px;
  background: var(--primary-light, #eff6ff); color: var(--primary);
  border: 1px solid var(--primary); font-size: 12px; font-weight: 500;
}
.kr-text { cursor: pointer; }
.kr-text:hover { text-decoration: underline; }

/* ── 과제 ── */
.task-list { padding: 8px 16px; display: flex; flex-direction: column; gap: 6px; }
.task-block { border: 1px solid var(--outline); border-radius: var(--radius-sm); overflow: visible; }

.task-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 8px 12px;
}
.task-id-badge {
  font-size: 11px; font-weight: 700; color: var(--text-muted);
  background: var(--gray-100); padding: 1px 6px;
  border-radius: 4px; flex-shrink: 0; font-family: monospace;
}
.task-name { font-size: 13px; font-weight: 500; flex: 1; min-width: 80px; }
.task-actions { margin-left: auto; display: flex; gap: 4px; flex-shrink: 0; }

/* ── 소과제 ── */
.subtask-list {
  border-top: 1px solid var(--outline);
  background: var(--gray-50, #f8fafc);
}
.subtask-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 6px 12px 6px 28px;
  border-bottom: 1px solid var(--outline);
}
.subtask-row:last-child { border-bottom: none; }
.subtask-check { width: 14px; height: 14px; cursor: pointer; flex-shrink: 0; }
.subtask-id-badge {
  font-size: 10px; font-weight: 600; color: var(--text-muted);
  background: var(--gray-200, #e5e7eb); padding: 1px 5px;
  border-radius: 3px; flex-shrink: 0; font-family: monospace;
}
.subtask-name { font-size: 12px; flex: 1; min-width: 80px; }
.subtask-name.done { text-decoration: line-through; color: var(--text-muted); }

/* ── 추가 행 ── */
.add-row { display: flex; align-items: center; gap: 6px; }
.subtask-add-row { background: var(--gray-50); padding: 6px 12px 6px 28px; border-top: 1px dashed var(--outline); }
.task-add-row { padding: 6px 0 2px; }

/* ── 담당자 칩 ── */
.member-chip-group { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
.member-chip {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 6px; font-size: 12px; font-weight: 500;
  background: var(--gray-100); color: var(--text-primary);
  border: 1px solid var(--outline-strong); border-radius: 999px;
}
.member-chip-sm { font-size: 11px; padding: 1px 5px; }
.chip-del {
  display: inline-flex; align-items: center; justify-content: center;
  width: 14px; height: 14px; border-radius: 50%;
  border: none; background: transparent; color: var(--text-muted);
  cursor: pointer; font-size: 10px; padding: 0; transition: background 0.12s, color 0.12s;
}
.chip-del:hover { background: var(--danger); color: #fff; }

/* ── 드롭다운 ── */
.dropdown-wrapper { position: relative; }
.member-dropdown {
  position: absolute; top: calc(100% + 4px); left: 0; z-index: 200;
  background: var(--surface); border: 1px solid var(--outline-strong);
  border-radius: var(--radius-sm); box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  padding: 8px; display: flex; flex-wrap: wrap; gap: 6px; max-width: 280px;
}
.dropdown-item {
  display: inline-flex; align-items: center;
  padding: 4px 10px; font-size: 12px; cursor: pointer;
  border: 1px solid var(--outline); border-radius: 999px;
  background: var(--surface); color: var(--text-secondary);
  transition: all 0.12s; white-space: nowrap;
}
.dropdown-item:hover { background: var(--primary-light); color: var(--primary); border-color: var(--primary); }
.dropdown-empty { padding: 10px 12px; font-size: 12px; color: var(--text-muted); }

/* ── 미연결 섹션 ── */
.unlinked-section { margin-top: 4px; }
.unlinked-header {
  display: flex; align-items: center; gap: 8px; padding: 12px 16px;
  cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text-secondary);
  border-radius: var(--radius-md);
}
.unlinked-header:hover { background: var(--gray-50); }
.unlinked-chevron { font-size: 18px; transition: transform 0.2s; transform: rotate(-90deg); }
.unlinked-chevron.open { transform: rotate(0deg); }

/* ── 모달 ── */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal-card {
  background: var(--surface); border-radius: var(--radius-lg);
  padding: 28px 32px; width: 440px; max-width: 95vw;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.modal-title { margin: 0 0 20px; font-size: 16px; font-weight: 700; }
.modal-footer { display: flex; justify-content: flex-end; gap: 8px; margin-top: 24px; }
.required { color: var(--danger); }
</style>

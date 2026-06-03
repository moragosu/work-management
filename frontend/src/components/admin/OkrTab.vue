<template>
  <div class="okr-tab">
    <!-- 툴바 -->
    <div class="tab-toolbar">
      <div class="okr-stats">
        <span class="stat-chip">목표 <strong>{{ objectives.length }}</strong>개</span>
        <span class="stat-chip">과제 <strong>{{ tasks.length }}</strong>개</span>
        <span class="stat-chip">인력 <strong>{{ staffList.length }}</strong>명</span>
      </div>
      <button class="btn btn-primary btn-sm" @click="startAddObjective">
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

          <span v-if="editingId !== obj.id + '_name'" class="obj-name editable"
                @click="startInline(obj.id + '_name', obj.name)">
            {{ obj.name }}
          </span>
          <input v-else class="inline-input inline-input-lg" v-model="inlineValue"
                 @keyup.enter="saveObjName(obj)" @keyup.escape="cancelInline"
                 @blur="saveObjName(obj)" v-autofocus />

          <select class="status-select" :value="obj.status"
                  @change="saveObjStatus(obj, $event.target.value)">
            <option value="진행중">진행중</option>
            <option value="완료">완료</option>
            <option value="위험">위험</option>
          </select>

          <div class="obj-header-right">
            <button class="btn btn-danger btn-xs" @click="deleteObjective(obj)">삭제</button>
          </div>
        </div>

        <!-- KR 행 -->
        <div class="kr-row">
          <span class="kr-label">KR</span>
          <div v-for="kr in obj.key_results" :key="kr.id" class="kr-chip">
            <span v-if="editingId !== obj.id + '_kr_' + kr.id" class="editable"
                  @click="startInline(obj.id + '_kr_' + kr.id, kr.name)">
              {{ kr.name }}
            </span>
            <input v-else class="inline-input inline-input-sm" v-model="inlineValue"
                   @keyup.enter="saveKrName(obj, kr)" @keyup.escape="cancelInline"
                   @blur="saveKrName(obj, kr)" v-autofocus />
            <button class="chip-del" @click="deleteKr(obj, kr.id)" data-tooltip="KR 삭제">✕</button>
          </div>
          <template v-if="addingKrObjId === obj.id">
            <input class="inline-input inline-input-sm" v-model="newKrName"
                   placeholder="KR 내용 입력"
                   @keyup.enter="saveNewKr(obj)" @keyup.escape="addingKrObjId = null"
                   @blur="saveNewKr(obj)" v-autofocus />
          </template>
          <button v-else class="btn-add-action" @click="startAddKr(obj.id)">+ KR</button>
        </div>

        <!-- 과제 목록 -->
        <div class="task-list">
          <div v-for="task in getTasksForObj(obj.id)" :key="task.id" class="task-block">

            <!-- 과제 행 -->
            <div class="task-row">
              <span class="task-id-badge">{{ task.id }}</span>

              <span v-if="editingId !== task.id + '_name'" class="task-name editable"
                    @click="startInline(task.id + '_name', task.name)">
                {{ task.name }}
              </span>
              <input v-else class="inline-input" v-model="inlineValue"
                     @keyup.enter="saveTaskName(task)" @keyup.escape="cancelInline"
                     @blur="saveTaskName(task)" v-autofocus />

              <select class="target-select" :value="task.target"
                      @change="saveTaskTarget(task, $event.target.value)">
                <option value="">-</option>
                <option v-for="t in taskTargets" :key="t" :value="t">{{ t }}</option>
              </select>

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
                         class="dropdown-item" @click="addMember(task, s)">
                      {{ s.name }}
                      <span class="text-muted" style="font-size:11px">{{ s.job_title }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <button class="btn btn-danger btn-xs task-del-btn" @click="deleteTask(task)">삭제</button>
            </div>

            <!-- 소과제 목록 -->
            <div v-if="task.sub_tasks && task.sub_tasks.length" class="subtask-list">
              <div v-for="st in task.sub_tasks" :key="st.id" class="subtask-row">
                <input type="checkbox" class="subtask-check" :checked="st.done"
                       @change="toggleSubDone(task, st)" />
                <span class="subtask-id-badge">{{ st.id }}</span>

                <span v-if="editingId !== st.id + '_name'"
                      class="subtask-name editable" :class="{ done: st.done }"
                      @click="startInline(st.id + '_name', st.name)">
                  {{ st.name }}
                </span>
                <input v-else class="inline-input" v-model="inlineValue"
                       @keyup.enter="saveSubName(task, st)" @keyup.escape="cancelInline"
                       @blur="saveSubName(task, st)" v-autofocus />

                <select class="target-select target-select-sm" :value="st.target"
                        @change="saveSubTarget(task, st, $event.target.value)">
                  <option value="">-</option>
                  <option v-for="t in taskTargets" :key="t" :value="t">{{ t }}</option>
                </select>

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
                           class="dropdown-item" @click="addSubMember(task, st, s)">
                        {{ s.name }}
                        <span class="text-muted" style="font-size:11px">{{ s.job_title }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <button class="btn btn-danger btn-xs task-del-btn" @click="deleteSubTask(task, st.id)">삭제</button>
              </div>
            </div>

            <!-- 소과제 추가 -->
            <div class="add-row subtask-add-row">
              <template v-if="addingSubTaskId === task.id">
                <input class="inline-input" v-model="newSubName" placeholder="소과제명"
                       @keyup.enter="saveNewSubTask(task)" @keyup.escape="addingSubTaskId = null"
                       v-autofocus />
                <button class="btn btn-ghost btn-xs" @click="addingSubTaskId = null">취소</button>
                <button class="btn btn-primary btn-xs" :disabled="!newSubName.trim()"
                        @click="saveNewSubTask(task)">추가</button>
              </template>
              <button v-else class="btn-add-action" @click="startAddSubTask(task.id)">+ 소과제</button>
            </div>

          </div>

          <!-- 과제 추가 -->
          <div class="add-row task-add-row">
            <template v-if="addingTaskObjId === obj.id">
              <input class="inline-input" v-model="newTaskName" placeholder="과제명"
                     @keyup.enter="saveNewTask(obj.id)" @keyup.escape="addingTaskObjId = null"
                     v-autofocus />
              <button class="btn btn-ghost btn-xs" @click="addingTaskObjId = null">취소</button>
              <button class="btn btn-primary btn-xs" :disabled="!newTaskName.trim()"
                      @click="saveNewTask(obj.id)">추가</button>
            </template>
            <button v-else class="btn-add-action" @click="startAddTask(obj.id)">+ 과제</button>
          </div>
        </div>
      </div>

      <!-- 목표 추가 폼 -->
      <div v-if="addingObjective" class="obj-add-card card card-body">
        <div class="flex gap-8" style="align-items:center">
          <input class="form-control" style="flex:1" v-model="newObjName" placeholder="목표명을 입력하세요"
                 @keyup.enter="saveNewObjective" @keyup.escape="addingObjective = false" v-autofocus />
          <button class="btn btn-ghost btn-sm" @click="addingObjective = false">취소</button>
          <button class="btn btn-primary btn-sm" :disabled="!newObjName.trim()" @click="saveNewObjective">추가</button>
        </div>
      </div>

      <!-- 미연결 과제 섹션 -->
      <div v-if="unlinkedTasks.length > 0" class="unlinked-section card">
        <div class="unlinked-header" @click="unlinkedOpen = !unlinkedOpen">
          <span class="material-symbols-outlined unlinked-chevron"
                :class="{ open: unlinkedOpen }">expand_more</span>
          <span class="unlinked-title">미연결 과제</span>
          <span class="badge badge-gray">{{ unlinkedTasks.length }}개</span>
        </div>
        <div v-if="unlinkedOpen" class="task-list" style="padding:0 16px 16px">
          <div v-for="task in unlinkedTasks" :key="task.id" class="task-block">
            <div class="task-row">
              <span class="task-id-badge">{{ task.id }}</span>
              <span v-if="editingId !== task.id + '_name'" class="task-name editable"
                    @click="startInline(task.id + '_name', task.name)">{{ task.name }}</span>
              <input v-else class="inline-input" v-model="inlineValue"
                     @keyup.enter="saveTaskName(task)" @keyup.escape="cancelInline"
                     @blur="saveTaskName(task)" v-autofocus />
              <select class="target-select" :value="task.target"
                      @change="saveTaskTarget(task, $event.target.value)">
                <option value="">-</option>
                <option v-for="t in taskTargets" :key="t" :value="t">{{ t }}</option>
              </select>
              <div class="member-chip-group">
                <span v-for="m in task.members" :key="m.username" class="member-chip">
                  {{ m.name }}<button class="chip-del" @click="removeMember(task, m.username)">✕</button>
                </span>
                <div class="dropdown-wrapper">
                  <button class="btn-add-action" @click.stop="toggleDropdown(task.id)">+ 담당자</button>
                  <div v-if="dropdownId === task.id" class="member-dropdown">
                    <div v-if="availableStaff(task.members).length === 0" class="dropdown-empty">추가할 인력이 없습니다</div>
                    <div v-for="s in availableStaff(task.members)" :key="s.id"
                         class="dropdown-item" @click="addMember(task, s)">
                      {{ s.name }}<span class="text-muted" style="font-size:11px">{{ s.job_title }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <button class="btn btn-danger btn-xs task-del-btn" @click="deleteTask(task)">삭제</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="objectives.length === 0 && !addingObjective" class="panel-empty" style="padding:48px;text-align:center">
        등록된 목표가 없습니다. 목표를 추가해주세요.
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
  objectives: { type: Array, default: () => [] },
  tasks:      { type: Array, default: () => [] },
  staffList:  { type: Array, default: () => [] },
  taskTargets:{ type: Array, default: () => [] },
  loading:    { type: Boolean, default: false },
  nextObjId:  { type: String, default: 'O1' },
  nextTaskId: { type: String, default: 'T1' },
})
const emit = defineEmits(['refresh'])
const { toastMsg, showToast } = useToast(2000)

// ── 인라인 편집 ──────────────────────────────────────────────────────
const editingId   = ref(null)
const inlineValue = ref('')

function startInline(id, value) {
  editingId.value = id
  inlineValue.value = value
}
function cancelInline() {
  editingId.value = null
  inlineValue.value = ''
}

// ── 드롭다운 ──────────────────────────────────────────────────────────
const dropdownId = ref(null)
function toggleDropdown(id) {
  dropdownId.value = dropdownId.value === id ? null : id
}
function closeDropdown() { dropdownId.value = null }
onMounted(() => document.addEventListener('click', closeDropdown))
onUnmounted(() => document.removeEventListener('click', closeDropdown))

// ── computed ──────────────────────────────────────────────────────────
function getTasksForObj(objId) {
  return props.tasks.filter(t => t.objective_id === objId)
}
const unlinkedTasks = computed(() =>
  props.tasks.filter(t => !t.objective_id)
)
const unlinkedOpen = ref(true)

function availableStaff(currentMembers) {
  const taken = new Set((currentMembers || []).map(m => m.username))
  return props.staffList.filter(s => !taken.has(s.username))
}

// ── 목표 CRUD ─────────────────────────────────────────────────────────
const addingObjective = ref(false)
const newObjName = ref('')

function startAddObjective() {
  addingObjective.value = true
  newObjName.value = ''
}

async function saveNewObjective() {
  if (!newObjName.value.trim()) return
  try {
    await axios.post('/api/okrs', { id: props.nextObjId, name: newObjName.value.trim(), key_results: [], status: '진행중' })
    addingObjective.value = false
    newObjName.value = ''
    emit('refresh')
    showToast('목표가 추가되었습니다')
  } catch { showToast('추가 실패') }
}

async function saveObjName(obj) {
  const val = inlineValue.value.trim()
  cancelInline()
  if (!val || val === obj.name) return
  try {
    await axios.put(`/api/okrs/${obj.id}`, { name: val })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function saveObjStatus(obj, status) {
  try {
    await axios.put(`/api/okrs/${obj.id}`, { status })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function deleteObjective(obj) {
  if (!confirm(`'${obj.name}' 목표를 삭제하시겠습니까?\n연결된 과제의 목표 연결이 해제됩니다.`)) return
  try {
    await axios.delete(`/api/okrs/${obj.id}`)
    emit('refresh')
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}

// ── KR CRUD ───────────────────────────────────────────────────────────
const addingKrObjId = ref(null)
const newKrName = ref('')

function startAddKr(objId) {
  addingKrObjId.value = objId
  newKrName.value = ''
}

async function saveNewKr(obj) {
  if (!newKrName.value.trim()) { addingKrObjId.value = null; return }
  const maxNum = (obj.key_results || []).reduce((m, kr) => {
    const n = parseInt(kr.id.replace('KR', '')) || 0
    return Math.max(m, n)
  }, 0)
  const newId = `KR${maxNum + 1}`
  try {
    await axios.post(`/api/okrs/${obj.id}/key-results`, { name: newKrName.value.trim(), id: newId })
    addingKrObjId.value = null
    newKrName.value = ''
    emit('refresh')
  } catch { showToast('추가 실패') }
}

async function saveKrName(obj, kr) {
  const val = inlineValue.value.trim()
  cancelInline()
  if (!val || val === kr.name) return
  try {
    await axios.put(`/api/okrs/${obj.id}/key-results/${kr.id}`, { name: val })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function deleteKr(obj, krId) {
  try {
    await axios.delete(`/api/okrs/${obj.id}/key-results/${krId}`)
    emit('refresh')
  } catch { showToast('삭제 실패') }
}

// ── 과제 CRUD ─────────────────────────────────────────────────────────
const addingTaskObjId = ref(null)
const newTaskName = ref('')

function startAddTask(objId) {
  addingTaskObjId.value = objId
  newTaskName.value = ''
}

async function saveNewTask(objId) {
  if (!newTaskName.value.trim()) return
  try {
    await axios.post('/api/tasks', {
      id: props.nextTaskId,
      name: newTaskName.value.trim(),
      objective_id: objId,
      target: '',
      members: [],
      sub_tasks: [],
    })
    addingTaskObjId.value = null
    newTaskName.value = ''
    emit('refresh')
    showToast('과제가 추가되었습니다')
  } catch { showToast('추가 실패') }
}

async function saveTaskName(task) {
  const val = inlineValue.value.trim()
  cancelInline()
  if (!val || val === task.name) return
  try {
    await axios.put(`/api/tasks/${task.id}`, { name: val })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function saveTaskTarget(task, target) {
  try {
    await axios.put(`/api/tasks/${task.id}`, { target })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function deleteTask(task) {
  if (!confirm(`'${task.name}' 과제를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/tasks/${task.id}`)
    emit('refresh')
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}

// ── 담당자 ────────────────────────────────────────────────────────────
async function addMember(task, staff) {
  dropdownId.value = null
  const newMember = { username: staff.username, name: staff.name, role: '' }
  const members = [...(task.members || []), newMember]
  try {
    await axios.put(`/api/tasks/${task.id}`, { members })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function removeMember(task, username) {
  const members = (task.members || []).filter(m => m.username !== username)
  try {
    await axios.put(`/api/tasks/${task.id}`, { members })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

// ── 소과제 CRUD ───────────────────────────────────────────────────────
const addingSubTaskId = ref(null)
const newSubName = ref('')

function startAddSubTask(taskId) {
  addingSubTaskId.value = taskId
  newSubName.value = ''
}

async function saveNewSubTask(task) {
  if (!newSubName.value.trim()) return
  const existing = (task.sub_tasks || [])
  const maxNum = existing.reduce((m, st) => {
    const n = parseInt(st.id.split('-')[1]) || 0
    return Math.max(m, n)
  }, 0)
  const newId = `${task.id}-${maxNum + 1}`
  const newSubs = [...existing, { id: newId, name: newSubName.value.trim(), done: false, members: [], target: '' }]
  try {
    await axios.put(`/api/tasks/${task.id}`, { sub_tasks: newSubs })
    addingSubTaskId.value = null
    newSubName.value = ''
    emit('refresh')
  } catch { showToast('추가 실패') }
}

async function saveSubName(task, st) {
  const val = inlineValue.value.trim()
  cancelInline()
  if (!val || val === st.name) return
  try {
    await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { name: val })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function saveSubTarget(task, st, target) {
  try {
    await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { target })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function toggleSubDone(task, st) {
  try {
    await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { done: !st.done })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function deleteSubTask(task, stId) {
  if (!confirm('소과제를 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/tasks/${task.id}/sub-tasks/${stId}`)
    emit('refresh')
    showToast('삭제되었습니다')
  } catch { showToast('삭제 실패') }
}

// ── 소과제 담당자 ──────────────────────────────────────────────────────
async function addSubMember(task, st, staff) {
  dropdownId.value = null
  const newMember = { username: staff.username, name: staff.name, role: '' }
  const members = [...(st.members || []), newMember]
  try {
    await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { members })
    emit('refresh')
  } catch { showToast('저장 실패') }
}

async function removeSubMember(task, st, username) {
  const members = (st.members || []).filter(m => m.username !== username)
  try {
    await axios.put(`/api/tasks/${task.id}/sub-tasks/${st.id}`, { members })
    emit('refresh')
  } catch { showToast('저장 실패') }
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
.obj-add-card { margin-bottom: 12px; }

.obj-header {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 16px; flex-wrap: wrap;
  border-bottom: 1px solid var(--outline);
  background: var(--gray-50, #f8fafc);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.obj-id-badge {
  font-size: 12px; font-weight: 700;
  background: var(--primary); color: #fff;
  padding: 2px 8px; border-radius: 999px;
  flex-shrink: 0;
}
.obj-name {
  font-size: 15px; font-weight: 600; color: var(--text-primary); flex: 1;
}
.obj-header-right { margin-left: auto; display: flex; gap: 6px; }

.status-select {
  padding: 3px 8px; border: 1px solid var(--outline-strong);
  border-radius: var(--radius-sm); font-size: 12px; font-weight: 500;
  background: var(--surface); color: var(--text-secondary); cursor: pointer;
}

/* ── KR ── */
.kr-row {
  display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
  padding: 10px 16px; border-bottom: 1px solid var(--outline);
  background: var(--surface);
}
.kr-label { font-size: 11px; font-weight: 600; color: var(--text-muted); margin-right: 2px; }
.kr-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 8px; border-radius: 999px;
  background: var(--primary-light, #eff6ff); color: var(--primary);
  border: 1px solid var(--primary); font-size: 12px; font-weight: 500;
}

/* ── 과제 ── */
.task-list { padding: 8px 16px 8px; display: flex; flex-direction: column; gap: 4px; }
.task-block { border: 1px solid var(--outline); border-radius: var(--radius-sm); overflow: visible; }

.task-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 8px 12px; background: var(--surface);
  border-radius: var(--radius-sm);
}
.task-id-badge {
  font-size: 11px; font-weight: 700; color: var(--text-muted);
  background: var(--gray-100); padding: 1px 6px;
  border-radius: 4px; flex-shrink: 0; font-family: monospace;
}
.task-name { font-size: 13px; font-weight: 500; flex: 1; min-width: 100px; }
.task-del-btn { margin-left: auto; flex-shrink: 0; }

/* ── 소과제 ── */
.subtask-list {
  border-top: 1px solid var(--outline);
  background: var(--gray-50, #f8fafc);
  padding: 4px 0;
}
.subtask-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 6px 12px 6px 28px;
}
.subtask-check { width: 14px; height: 14px; cursor: pointer; flex-shrink: 0; }
.subtask-id-badge {
  font-size: 10px; font-weight: 600; color: var(--text-muted);
  background: var(--gray-200, #e5e7eb); padding: 1px 5px;
  border-radius: 3px; flex-shrink: 0; font-family: monospace;
}
.subtask-name { font-size: 12px; flex: 1; min-width: 80px; }
.subtask-name.done { text-decoration: line-through; color: var(--text-muted); }

/* ── 추가 행 ── */
.add-row { padding: 6px 12px; }
.subtask-add-row { background: var(--gray-50); padding: 6px 12px 6px 28px; display: flex; align-items: center; gap: 6px; }
.task-add-row { padding: 8px 0 4px; display: flex; align-items: center; gap: 6px; }

/* ── 담당자 칩 ── */
.member-chip-group { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
.member-chip {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 6px; font-size: 12px; font-weight: 500;
  background: var(--gray-100); color: var(--text-primary);
  border: 1px solid var(--outline-strong); border-radius: 999px;
}
.member-chip-sm { font-size: 11px; padding: 1px 5px; }

/* ── 공통 삭제 버튼 ── */
.chip-del {
  display: inline-flex; align-items: center; justify-content: center;
  width: 14px; height: 14px; border-radius: 50%;
  border: none; background: transparent;
  color: var(--text-muted); cursor: pointer; font-size: 10px; padding: 0;
  transition: background 0.12s, color 0.12s;
}
.chip-del:hover { background: var(--danger); color: #fff; }

/* ── 드롭다운 ── */
.dropdown-wrapper { position: relative; }
.member-dropdown {
  position: absolute; top: calc(100% + 4px); left: 0; z-index: 100;
  background: var(--surface); border: 1px solid var(--outline-strong);
  border-radius: var(--radius-sm); box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  min-width: 140px; max-height: 200px; overflow-y: auto;
}
.dropdown-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 12px; font-size: 13px; cursor: pointer; gap: 8px;
  transition: background 0.1s;
}
.dropdown-item:hover { background: var(--gray-50); }
.dropdown-empty { padding: 10px 12px; font-size: 12px; color: var(--text-muted); }

/* ── 인라인 편집 ── */
.editable { cursor: pointer; border-radius: 3px; padding: 1px 3px; }
.editable:hover { background: var(--primary-light, #eff6ff); }
.inline-input {
  border: 1px solid var(--primary); border-radius: var(--radius-sm);
  padding: 3px 8px; font-size: 13px; outline: none;
  background: var(--surface); color: var(--text-primary);
  min-width: 120px;
}
.inline-input-lg { font-size: 15px; font-weight: 600; min-width: 200px; }
.inline-input-sm { min-width: 100px; font-size: 12px; }

/* ── target select ── */
.target-select {
  padding: 2px 6px; border: 1px solid var(--outline-strong);
  border-radius: var(--radius-xs); font-size: 11px; font-weight: 600;
  background: var(--surface); color: var(--text-secondary);
  cursor: pointer; flex-shrink: 0;
}
.target-select-sm { font-size: 10px; }

/* ── 미연결 섹션 ── */
.unlinked-section { margin-top: 8px; }
.unlinked-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px; cursor: pointer;
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
}
.unlinked-header:hover { background: var(--gray-50); border-radius: var(--radius-md); }
.unlinked-title { color: var(--text-secondary); }
.unlinked-chevron { font-size: 18px; transition: transform 0.2s; }
.unlinked-chevron.open { transform: rotate(0deg); }
.unlinked-chevron:not(.open) { transform: rotate(-90deg); }
</style>

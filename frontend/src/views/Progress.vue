<template>
  <div>
    <div class="page-header">
      <div>
        <h2>진행도 관리</h2>
        <div class="subtitle">주차별 세부 진행 상황</div>
      </div>
      <div class="flex gap-8">
        <button class="btn btn-primary btn-sm" @click="openAddModal()">+ 항목 추가</button>
      </div>
    </div>

    <div class="page-body">
      <!-- Filter bar -->
      <div class="filter-bar">
        <div class="search-input">
          <span class="search-icon">🔍</span>
          <input v-model="search" class="form-control" placeholder="담당자, 과제, 이슈 검색..." />
        </div>
        <select v-model="filterObjective" class="form-control">
          <option value="">전체 Objective</option>
          <option v-for="o in objectiveOptions" :key="o" :value="o">{{ o }}</option>
        </select>
        <select v-model="filterAssignee" class="form-control">
          <option value="">전체 담당자</option>
          <option v-for="s in staffOptions" :key="s" :value="s">{{ s }}</option>
        </select>
        <button class="btn btn-ghost btn-sm" @click="clearFilters">초기화</button>
      </div>

      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="weekGroups.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>등록된 항목이 없습니다.</p>
      </div>

      <!-- Week accordions -->
      <div v-for="group in weekGroups" :key="group.week" style="margin-bottom:12px">
        <div class="accordion-header" @click="toggleWeek(group.week)">
          <span class="badge badge-blue">{{ group.week }}</span>
          <span style="margin-left:4px">{{ group.items.length }}개 항목</span>
          <div class="flex gap-8" style="margin-left:12px" @click.stop>
            <button class="btn btn-ghost btn-xs" @click="openAddModal(group.week)">+ 추가</button>
          </div>
          <span class="accordion-chevron" :class="{ open: openWeeks.has(group.week) }">▼</span>
        </div>

        <div v-if="openWeeks.has(group.week)" class="accordion-body">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Objective</th>
                  <th>과제</th>
                  <th>세부항목</th>
                  <th>예정</th>
                  <th>결과</th>
                  <th style="width:80px">진행도(%)</th>
                  <th>이슈</th>
                  <th>담당자</th>
                  <th>해결방안</th>
                  <th style="width:60px"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in group.items" :key="item.id">
                  <td>
                    <span class="badge badge-blue">{{ item.objective }}</span>
                  </td>
                  <td>
                    <select
                      class="form-control inline"
                      :value="item.task"
                      @change="autoSave(item, 'task', $event.target.value)"
                    >
                      <option v-for="o in objectives" :key="o.id" :value="o.name">{{ o.id }}: {{ o.name }}</option>
                    </select>
                  </td>
                  <td>
                    <input
                      class="form-control inline"
                      :value="item.subtask"
                      @input="debounceSave(item, 'subtask', $event.target.value)"
                    />
                  </td>
                  <td>
                    <textarea
                      class="form-control inline"
                      rows="2"
                      style="resize:vertical;min-width:120px"
                      :value="item.planned"
                      @input="debounceSave(item, 'planned', $event.target.value)"
                    ></textarea>
                  </td>
                  <td>
                    <textarea
                      class="form-control inline"
                      rows="2"
                      style="resize:vertical;min-width:120px"
                      :value="item.result"
                      @input="debounceSave(item, 'result', $event.target.value)"
                    ></textarea>
                  </td>
                  <td>
                    <input
                      type="number" min="0" max="100"
                      class="form-control inline"
                      style="width:70px"
                      :value="item.progress_percent"
                      @change="autoSave(item, 'progress_percent', Number($event.target.value))"
                    />
                  </td>
                  <td>
                    <textarea
                      class="form-control inline"
                      rows="2"
                      style="resize:vertical;min-width:100px"
                      :value="item.issue"
                      @input="debounceSave(item, 'issue', $event.target.value)"
                    ></textarea>
                  </td>
                  <td>
                    <select
                      class="form-control inline"
                      style="min-width:80px"
                      :value="item.assignee"
                      @change="autoSave(item, 'assignee', $event.target.value)"
                    >
                      <option value="">-</option>
                      <option v-for="s in staffOptions" :key="s" :value="s">{{ s }}</option>
                    </select>
                  </td>
                  <td>
                    <textarea
                      class="form-control inline"
                      rows="2"
                      style="resize:vertical;min-width:100px"
                      :value="item.solution"
                      @input="debounceSave(item, 'solution', $event.target.value)"
                    ></textarea>
                  </td>
                  <td>
                    <button class="btn btn-danger btn-xs" @click="deleteItem(item)">삭제</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>진행 항목 추가</h3>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">주차 *</label>
              <input v-model="form.week" class="form-control" placeholder="W1, W2, ..." />
            </div>
            <div class="form-group">
              <label class="form-label">Objective *</label>
              <select v-model="form.objective" class="form-control">
                <option value="">선택</option>
                <option v-for="o in objectives" :key="o.id" :value="o.id">{{ o.id }}: {{ o.name }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">과제</label>
            <select v-model="form.task" class="form-control">
              <option value="">선택</option>
              <option v-for="o in objectives" :key="o.id" :value="o.name">{{ o.id }}: {{ o.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">세부항목</label>
            <input v-model="form.subtask" class="form-control" />
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">예정</label>
              <textarea v-model="form.planned" class="form-control" rows="2"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">결과</label>
              <textarea v-model="form.result" class="form-control" rows="2"></textarea>
            </div>
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">진행도 (%)</label>
              <input type="number" v-model.number="form.progress_percent" min="0" max="100" class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">담당자</label>
              <select v-model="form.assignee" class="form-control">
                <option value="">선택</option>
                <option v-for="s in staffOptions" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">이슈</label>
            <textarea v-model="form.issue" class="form-control" rows="2"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">해결방안</label>
            <textarea v-model="form.solution" class="form-control" rows="2"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showModal = false">취소</button>
          <button class="btn btn-primary" @click="submitAdd" :disabled="!form.week || !form.objective">추가</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const items = ref([])
const objectives = ref([])
const staffOptions = ref([])
const loading = ref(false)
const search = ref('')
const filterObjective = ref('')
const filterAssignee = ref('')
const openWeeks = ref(new Set())
const showModal = ref(false)
const toastMsg = ref('')
const debounceTimers = {}

const defaultForm = () => ({
  week: currentWeek(),
  objective: '',
  task: '',
  subtask: '',
  planned: '',
  result: '',
  progress_percent: 0,
  issue: '',
  assignee: '',
  solution: '',
})
const form = ref(defaultForm())

const objectiveOptions = computed(() => [...new Set(items.value.map(i => i.objective).filter(Boolean))])

const filteredItems = computed(() => {
  let result = items.value
  if (search.value) {
    const q = search.value.toLowerCase()
    result = result.filter(i =>
      i.assignee?.toLowerCase().includes(q) ||
      i.task?.toLowerCase().includes(q) ||
      i.issue?.toLowerCase().includes(q) ||
      i.subtask?.toLowerCase().includes(q)
    )
  }
  if (filterObjective.value) result = result.filter(i => i.objective === filterObjective.value)
  if (filterAssignee.value) result = result.filter(i => i.assignee === filterAssignee.value)
  return result
})

const weekGroups = computed(() => {
  const map = new Map()
  for (const item of filteredItems.value) {
    const w = item.week || '미지정'
    if (!map.has(w)) map.set(w, [])
    map.get(w).push(item)
  }
  return [...map.entries()]
    .sort(([a], [b]) => (parseInt(a.slice(1)) || 0) - (parseInt(b.slice(1)) || 0))
    .map(([week, items]) => ({ week, items }))
})

function currentWeek() {
  const jan1 = new Date(new Date().getFullYear(), 0, 1)
  const weekNum = Math.ceil(((new Date() - jan1) / 86400000 + jan1.getDay() + 1) / 7)
  return `W${weekNum}`
}

function toggleWeek(week) {
  if (openWeeks.value.has(week)) openWeeks.value.delete(week)
  else openWeeks.value.add(week)
  openWeeks.value = new Set(openWeeks.value)
}

function clearFilters() {
  search.value = ''
  filterObjective.value = ''
  filterAssignee.value = ''
}

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

function debounceSave(item, field, value) {
  const key = `${item.id}-${field}`
  clearTimeout(debounceTimers[key])
  debounceTimers[key] = setTimeout(() => autoSave(item, field, value), 800)
}

async function autoSave(item, field, value) {
  item[field] = value
  try {
    await axios.put(`/api/progress/${item.id}`, { [field]: value })
    showToast('저장됨')
  } catch {
    showToast('저장 실패')
  }
}

function openAddModal(week = null) {
  form.value = defaultForm()
  if (week) form.value.week = week
  showModal.value = true
}

async function submitAdd() {
  try {
    const { data } = await axios.post('/api/progress', form.value)
    items.value.push(data)
    openWeeks.value.add(data.week)
    openWeeks.value = new Set(openWeeks.value)
    showModal.value = false
    showToast('항목이 추가되었습니다')
  } catch {
    showToast('추가 실패')
  }
}

async function deleteItem(item) {
  if (!confirm(`"${item.subtask || item.task}" 항목을 삭제하시겠습니까?`)) return
  await axios.delete(`/api/progress/${item.id}`)
  items.value = items.value.filter(i => i.id !== item.id)
  showToast('삭제되었습니다')
}

async function fetchAll() {
  loading.value = true
  try {
    const [pRes, oRes, sRes] = await Promise.all([
      axios.get('/api/progress'),
      axios.get('/api/okrs'),
      axios.get('/api/staff'),
    ])
    items.value = pRes.data
    objectives.value = oRes.data
    staffOptions.value = sRes.data.map(s => s.name)
    // open current week by default
    const cw = currentWeek()
    if (items.value.some(i => i.week === cw)) {
      openWeeks.value.add(cw)
    } else if (weekGroups.value.length > 0) {
      openWeeks.value.add(weekGroups.value[weekGroups.value.length - 1].week)
    }
    openWeeks.value = new Set(openWeeks.value)
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
</script>
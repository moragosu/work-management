<template>
  <div>
    <div v-if="!embedded" class="page-header">
      <div>
        <h2>인력 관리</h2>
        <div class="subtitle">팀원 기술 현황</div>
      </div>
      <button class="btn btn-primary btn-sm" @click="openAddModal">+ 인력 추가</button>
    </div>

    <div :class="{ 'page-body': !embedded }">
      <div v-if="!embedded" class="grid-4" style="margin-bottom:24px">
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--primary)">{{ staff.length }}</div>
            <div class="text-muted text-sm mt-8">총 인원</div>
          </div>
        </div>
      </div>

      <!-- 인력 필터 칩 -->
      <div v-if="staff.length > 0" class="filter-bar staff-filter-bar">
        <span class="filter-label-sm">인력</span>
        <button
          v-for="s in staff"
          :key="s.username"
          class="staff-chip"
          :class="{ 'staff-chip-active': selectedStaffFilter.includes(s.username) }"
          @click="toggleStaffFilter(s.username)"
        >{{ s.name }}</button>
        <button v-if="selectedStaffFilter.length > 0" class="btn btn-ghost btn-xs" @click="selectedStaffFilter = []">전체 보기</button>
      </div>

      <div class="card">
        <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
        <div v-else-if="staff.length === 0" class="empty-state">
          <div class="empty-icon">👥</div>
          <p>등록된 인력이 없습니다.</p>
        </div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th @click="sortBy('name')" style="cursor:pointer">
                  이름 <span v-if="sortKey === 'name'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('job_title')" style="cursor:pointer">
                  직책 <span v-if="sortKey === 'job_title'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('main_skills')" style="cursor:pointer">
                  주 기술 <span v-if="sortKey === 'main_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('sub_skills')" style="cursor:pointer">
                  부 기술 <span v-if="sortKey === 'sub_skills'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th style="width:90px"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in sortedStaff" :key="member.username">
                <td style="white-space:nowrap">
                  <div style="font-weight:600">{{ member.name }}</div>
                  <div style="font-size:11px;color:var(--text-muted);margin-top:2px">{{ member.username }}</div>
                </td>
                <td>
                  <input
                    class="form-control inline"
                    :value="member.job_title"
                    @input="debounceSave(member, 'job_title', $event.target.value)"
                  />
                </td>
                <td>
                  <input
                    class="form-control inline"
                    style="min-width:120px"
                    :value="member.main_skills"
                    @input="debounceSave(member, 'main_skills', $event.target.value)"
                  />
                </td>
                <td>
                  <input
                    class="form-control inline"
                    style="min-width:100px"
                    :value="member.sub_skills"
                    @input="debounceSave(member, 'sub_skills', $event.target.value)"
                  />
                </td>
                <td>
                  <button class="btn btn-ghost btn-xs" @click="editMember(member)">수정</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 추가/수정 모달 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedMember ? '인력 수정' : '인력 추가' }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="!selectedMember" class="form-group">
            <label class="form-label">아이디 (username) *</label>
            <input v-model="form.username" class="form-control" placeholder="예: gildong.hong" />
          </div>
          <div class="form-group">
            <label class="form-label">이름 *</label>
            <input v-model="form.name" class="form-control" :disabled="!!selectedMember" />
          </div>
          <div class="form-group">
            <label class="form-label">직책</label>
            <input v-model="form.job_title" class="form-control" />
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">주 기술</label>
              <input v-model="form.main_skills" class="form-control" placeholder="Python, PyTorch, ..." />
            </div>
            <div class="form-group">
              <label class="form-label">부 기술</label>
              <input v-model="form.sub_skills" class="form-control" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="closeModal">취소</button>
          <button class="btn btn-primary" @click="submitForm" :disabled="!form.name.trim() || (!selectedMember && !form.username.trim())">
            {{ selectedMember ? '수정' : '추가' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from '../composables/useToast.js'
import { useModal } from '../composables/useModal.js'

const props = defineProps({ embedded: { type: Boolean, default: false } })
const emit = defineEmits(['updated'])

const staff = ref([])
const loading = ref(false)
const selectedStaffFilter = ref([])
const { show: showModal, open: openModal, close: closeModal } = useModal()
const { toastMsg, showToast, toastError } = useToast()
const debounceTimers = {}

const defaultForm = () => ({ username: '', name: '', job_title: '', main_skills: '', sub_skills: '' })
const form = ref(defaultForm())
const selectedMember = ref(null)

async function fetchStaff() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/staff')
    staff.value = data
  } finally { loading.value = false }
}

function toggleStaffFilter(username) {
  const idx = selectedStaffFilter.value.indexOf(username)
  if (idx === -1) selectedStaffFilter.value.push(username)
  else selectedStaffFilter.value.splice(idx, 1)
}

function debounceSave(member, field, value) {
  const key = `${member.username}-${field}`
  clearTimeout(debounceTimers[key])
  debounceTimers[key] = setTimeout(async () => {
    member[field] = value
    try {
      await axios.put(`/api/staff/${member.username}`, { [field]: value })
      showToast('저장됨')
    } catch (e) { toastError(e, '저장 실패') }
  }, 800)
}

function openAddModal() {
  form.value = defaultForm()
  selectedMember.value = null
  openModal()
}

function editMember(member) {
  selectedMember.value = member
  form.value = {
    name: member.name,
    job_title: member.job_title || '',
    main_skills: member.main_skills || '',
    sub_skills: member.sub_skills || '',
  }
  openModal()
}

async function submitForm() {
  try {
    if (selectedMember.value) {
      const { data } = await axios.put(`/api/staff/${selectedMember.value.username}`, form.value)
      const idx = staff.value.findIndex(s => s.username === selectedMember.value.username)
      if (idx !== -1) staff.value[idx] = data
      showToast('인력 정보가 수정되었습니다')
    } else {
      const { data } = await axios.post('/api/staff', form.value)
      staff.value.push(data)
      showToast('인력이 추가되었습니다 (임시 비밀번호로 계정 생성됨)')
    }
    closeModal()
    emit('updated')
  } catch (e) { toastError(e, selectedMember.value ? '수정 실패' : '추가 실패') }
}

const sortKey = ref('name')
const sortOrder = ref('asc')

const sortedStaff = computed(() => {
  const filtered = selectedStaffFilter.value.length > 0
    ? staff.value.filter(s => selectedStaffFilter.value.includes(s.username))
    : staff.value
  return [...filtered].sort((a, b) => {
    let aV = a[sortKey.value] || ''
    let bV = b[sortKey.value] || ''
    if (typeof aV === 'string') { aV = aV.toLowerCase(); bV = bV.toLowerCase() }
    const r = aV < bV ? -1 : aV > bV ? 1 : 0
    return sortOrder.value === 'asc' ? r : -r
  })
})

function sortBy(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

onMounted(fetchStaff)

defineExpose({ openAddModal })
</script>

<style scoped>
.staff-filter-bar { gap: 6px; }
.filter-label-sm { font-size: var(--fs-xs); font-weight: var(--fw-semibold); color: var(--text-muted); white-space: nowrap; }
.staff-chip {
  display: inline-flex; align-items: center; padding: 3px 10px;
  border-radius: 999px; border: 1px solid var(--outline); font-size: var(--fs-xs);
  font-family: inherit; cursor: pointer; background: var(--surface); color: var(--text-secondary);
  transition: all 0.15s;
}
.staff-chip:hover { border-color: var(--primary); color: var(--primary); }
.staff-chip-active { background: var(--primary-light); color: var(--primary); border-color: var(--primary); font-weight: var(--fw-semibold); }
</style>

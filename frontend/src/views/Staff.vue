<template>
  <div>
    <div class="page-header">
      <div>
        <h2>인력 관리</h2>
        <div class="subtitle">팀원 기술 현황 및 OKR 참여 현황</div>
      </div>
      <button class="btn btn-primary btn-sm" @click="openAddModal">+ 인력 추가</button>
    </div>

    <div class="page-body">
      <!-- Filter bar -->
      <div class="filter-bar">
        <div class="search-input">
          <span class="search-icon">🔍</span>
          <input v-model="search" class="form-control" placeholder="이름, 기술, OKR 검색..." @input="fetchStaff" />
        </div>
        <button class="btn btn-ghost btn-sm" @click="search = ''; fetchStaff()">초기화</button>
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
                <th>이름</th>
                <th>직책/역할</th>
                <th>주 기술</th>
                <th>부 기술</th>
                <th>학습 중</th>
                <th>희망 분야</th>
                <th>참여 OKR</th>
                <th style="width:60px"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in staff" :key="member.id">
                <td style="font-weight:600;white-space:nowrap">{{ member.name }}</td>
                <td>
                  <input
                    class="form-control inline"
                    :value="member.role"
                    @input="debounceSave(member, 'role', $event.target.value)"
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
                  <input
                    class="form-control inline"
                    style="min-width:100px"
                    :value="member.learning"
                    @input="debounceSave(member, 'learning', $event.target.value)"
                  />
                </td>
                <td>
                  <input
                    class="form-control inline"
                    style="min-width:100px"
                    :value="member.desired_field"
                    @input="debounceSave(member, 'desired_field', $event.target.value)"
                  />
                </td>
                <td>
                  <input
                    class="form-control inline"
                    style="min-width:80px"
                    :value="member.okrs"
                    @input="debounceSave(member, 'okrs', $event.target.value)"
                  />
                </td>
                <td>
                  <button class="btn btn-danger btn-xs" @click="deleteMember(member)">삭제</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>인력 추가</h3>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">이름 *</label>
              <input v-model="form.name" class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">직책/역할</label>
              <input v-model="form.role" class="form-control" />
            </div>
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
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">학습 중</label>
              <input v-model="form.learning" class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">희망 분야</label>
              <input v-model="form.desired_field" class="form-control" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">참여 OKR</label>
            <input v-model="form.okrs" class="form-control" placeholder="O1, O2, ..." />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showModal = false">취소</button>
          <button class="btn btn-primary" @click="submitAdd" :disabled="!form.name.trim()">추가</button>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const staff = ref([])
const loading = ref(false)
const search = ref('')
const showModal = ref(false)
const toastMsg = ref('')
const debounceTimers = {}

const defaultForm = () => ({ name: '', role: '', main_skills: '', sub_skills: '', learning: '', desired_field: '', okrs: '' })
const form = ref(defaultForm())

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

async function fetchStaff() {
  loading.value = true
  try {
    const params = search.value ? { search: search.value } : {}
    const { data } = await axios.get('/api/staff', { params })
    staff.value = data
  } finally {
    loading.value = false
  }
}

function debounceSave(member, field, value) {
  const key = `${member.id}-${field}`
  clearTimeout(debounceTimers[key])
  debounceTimers[key] = setTimeout(async () => {
    member[field] = value
    try {
      await axios.put(`/api/staff/${member.id}`, { [field]: value })
      showToast('저장됨')
    } catch {
      showToast('저장 실패')
    }
  }, 800)
}

function openAddModal() {
  form.value = defaultForm()
  showModal.value = true
}

async function submitAdd() {
  try {
    const { data } = await axios.post('/api/staff', form.value)
    staff.value.push(data)
    showModal.value = false
    showToast('인력이 추가되었습니다')
  } catch {
    showToast('추가 실패')
  }
}

async function deleteMember(member) {
  if (!confirm(`"${member.name}"을(를) 삭제하시겠습니까?`)) return
  await axios.delete(`/api/staff/${member.id}`)
  staff.value = staff.value.filter(s => s.id !== member.id)
  showToast('삭제되었습니다')
}

onMounted(fetchStaff)
</script>

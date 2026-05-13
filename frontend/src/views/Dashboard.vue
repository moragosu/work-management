<template>
  <div>
    <div class="page-header">
      <div>
        <h2>대시보드</h2>
        <div class="subtitle">Objective 전체 현황</div>
      </div>
      <div class="flex gap-8">
        <span class="text-sm text-muted">{{ today }}</span>
        <button class="btn btn-ghost btn-sm" @click="refresh">🔄 새로고침</button>
      </div>
    </div>

    <div class="page-body">
      <!-- Summary cards -->
      <div class="grid-4" style="margin-bottom:24px">
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--primary)">{{ objectives.length }}</div>
            <div class="text-muted text-sm mt-8">전체 Objective</div>
          </div>
        </div>
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--primary)">{{ inProgressCount }}</div>
            <div class="text-muted text-sm mt-8">진행중</div>
          </div>
        </div>
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--success)">{{ completedCount }}</div>
            <div class="text-muted text-sm mt-8">완료</div>
          </div>
        </div>
        <div class="card">
          <div class="card-body" style="text-align:center">
            <div style="font-size:28px;font-weight:700;color:var(--danger)">{{ dangerCount }}</div>
            <div class="text-muted text-sm mt-8">위험</div>
          </div>
        </div>
      </div>

      <!-- Objective cards -->
      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="objectives.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>등록된 Objective가 없습니다. 관리 도구에서 Objective를 추가하세요.</p>
      </div>
      <div v-else class="grid-2" style="gap:16px">
        <div v-for="obj in objectives" :key="obj.id" class="card objective-card">
          <div class="card-header">
            <div class="flex-center gap-8">
              <span class="objective-id-badge">{{ obj.id }}</span>
              <div>
                <div style="font-weight:600;font-size:15px">{{ obj.name }}</div>
                <div v-if="obj.tech_stack" class="text-sm text-muted">{{ obj.tech_stack }}</div>
              </div>
            </div>
            <span :class="statusBadgeClass(obj.status)">{{ obj.status }}</span>
          </div>
          <div class="card-body">
            <!-- Key Results -->
            <div v-if="obj.key_results && obj.key_results.length > 0" style="margin-bottom:16px">
              <div class="text-sm text-muted" style="margin-bottom:8px">Key Results ({{ obj.key_results.length }}개):</div>
              <div v-for="kr in obj.key_results" :key="kr.id" class="kr-item">
                <span class="badge badge-blue" style="width:40px">{{ kr.id }}</span>
                <span class="text-sm" style="margin-left:8px">{{ kr.name }}</span>
              </div>
            </div>
            <div v-else class="text-sm text-muted">Key Results 없음</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const objectives = ref([])
const loading = ref(false)
const today = new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

const inProgressCount = computed(() => objectives.value.filter(o => o.status === '진행중').length)
const completedCount = computed(() => objectives.value.filter(o => o.status === '완료').length)
const dangerCount = computed(() => objectives.value.filter(o => o.status === '위험').length)

async function refresh() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/okrs')
    objectives.value = data
  } finally {
    loading.value = false
  }
}

function statusBadgeClass(status) {
  return {
    '진행중': 'badge badge-blue',
    '완료': 'badge badge-green',
    '위험': 'badge badge-red',
  }[status] || 'badge badge-gray'
}

onMounted(refresh)
</script>

<style scoped>
.objective-card { transition: box-shadow .2s; }
.objective-card:hover { box-shadow: var(--shadow-md); }
.objective-id-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 36px; height: 36px;
  background: var(--primary-light); color: var(--primary);
  border-radius: 8px; font-weight: 700; font-size: 14px;
  flex-shrink: 0;
}
.kr-item {
  background: var(--gray-50);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
}
</style>
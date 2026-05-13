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
                <div class="text-sm text-muted">PL: {{ obj.pl }}</div>
              </div>
            </div>
            <span :class="statusBadgeClass(obj.status)">{{ obj.status }}</span>
          </div>
          <div class="card-body">
            <!-- Overall Progress -->
            <div class="flex-between" style="margin-bottom:8px">
              <span class="text-sm text-muted">전체 진행률</span>
              <span style="font-weight:700;font-size:16px" :style="{ color: progressColor(calcProgress(obj)) }">
                {{ calcProgress(obj) }}%
              </span>
            </div>
            <div class="progress-bar" style="margin-bottom:16px">
              <div
                class="progress-fill"
                :class="progressClass(calcProgress(obj))"
                :style="{ width: calcProgress(obj) + '%' }"
              ></div>
            </div>

            <!-- Key Results -->
            <div v-if="obj.key_results && obj.key_results.length > 0" style="margin-bottom:16px">
              <div class="text-sm text-muted" style="margin-bottom:8px">Key Results:</div>
              <div v-for="kr in obj.key_results" :key="kr.id" class="kr-item">
                <div class="flex-between" style="margin-bottom:4px">
                  <span class="text-sm">{{ kr.id }}: {{ kr.name }}</span>
                  <span class="text-sm" :style="{ color: progressColor(kr.progress), fontWeight:600 }">{{ kr.progress }}%</span>
                </div>
                <div class="progress-bar-sm">
                  <div
                    class="progress-fill-sm"
                    :class="progressClass(kr.progress)"
                    :style="{ width: kr.progress + '%' }"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Tech stack & members -->
            <div v-if="obj.tech_stack" style="margin-bottom:10px">
              <span class="text-sm text-muted">기술 스택: </span>
              <span class="text-sm">{{ obj.tech_stack }}</span>
            </div>
            <div>
              <span class="text-sm text-muted">팀원: </span>
              <span
                v-for="m in obj.team_members" :key="m.name"
                class="badge badge-gray"
                style="margin-right:4px"
              >{{ m.name }} ({{ m.role }})</span>
            </div>
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

function calcProgress(obj) {
  const keyResults = obj.key_results || []
  if (keyResults.length === 0) return 0
  const total = keyResults.reduce((sum, kr) => sum + (kr.progress || 0), 0)
  return Math.round(total / keyResults.length)
}

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

function progressColor(pct) {
  if (pct >= 100) return 'var(--success)'
  if (pct < 30) return 'var(--danger)'
  return 'var(--primary)'
}

function progressClass(pct) {
  if (pct >= 100) return 'green'
  if (pct < 30) return 'red'
  return 'blue'
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
}
.progress-bar-sm {
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill-sm {
  height: 100%;
  transition: width .3s;
}
.progress-fill-sm.blue { background: var(--primary); }
.progress-fill-sm.green { background: var(--success); }
.progress-fill-sm.red { background: var(--danger); }
</style>
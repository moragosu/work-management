<template>
  <div>
    <div class="page-header">
      <div>
        <h2>대시보드</h2>
        <div class="subtitle">목표 전체 현황</div>
      </div>
      <div class="flex gap-8" style="align-items:center">
        <span class="text-sm text-muted">{{ today }}</span>
        <button class="btn btn-ghost btn-sm" @click="refresh">🔄 새로고침</button>
      </div>
    </div>

    <div class="page-body">
      <!-- 요약 카드 -->
      <div class="grid-4" style="margin-bottom:24px">
        <div class="card stat-accent stat-accent-blue">
          <div class="card-body stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-value">{{ objectives.length }}</div>
            <div class="stat-label">전체 목표</div>
          </div>
        </div>
        <div class="card stat-accent stat-accent-primary">
          <div class="card-body stat-card">
            <div class="stat-icon">🔄</div>
            <div class="stat-value" style="color:var(--primary)">{{ inProgressCount }}</div>
            <div class="stat-label">진행중</div>
          </div>
        </div>
        <div class="card stat-accent stat-accent-green">
          <div class="card-body stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value" style="color:var(--success)">{{ completedCount }}</div>
            <div class="stat-label">완료</div>
          </div>
        </div>
        <div class="card stat-accent stat-accent-red">
          <div class="card-body stat-card">
            <div class="stat-icon">⚠️</div>
            <div class="stat-value" style="color:var(--danger)">{{ dangerCount }}</div>
            <div class="stat-label">위험</div>
          </div>
        </div>
      </div>

      <!-- 목표 카드 목록 -->
      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="objectives.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>등록된 목표가 없습니다. 관리 도구에서 목표를 추가하세요.</p>
      </div>
      <div v-else class="grid-2" style="gap:16px">
        <div v-for="obj in objectives" :key="obj.id" class="card obj-card">
          <div class="card-header">
            <div class="flex-center gap-8" style="min-width:0;flex:1">
              <span class="obj-id-badge">{{ obj.id }}</span>
              <span class="obj-name">{{ obj.name }}</span>
            </div>
            <span :class="statusBadgeClass(obj.status)" style="flex-shrink:0">{{ obj.status }}</span>
          </div>
          <div class="card-body" style="padding:12px 16px">
            <div v-if="obj.key_results && obj.key_results.length > 0">
              <div class="section-title">Key Results <span class="text-muted">({{ obj.key_results.length }})</span></div>
              <div class="kr-list">
                <div v-for="kr in obj.key_results" :key="kr.id" class="kr-item">
                  <span class="badge badge-blue" style="width:36px;justify-content:center">{{ kr.id }}</span>
                  <span class="text-sm">{{ kr.name }}</span>
                </div>
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
const completedCount  = computed(() => objectives.value.filter(o => o.status === '완료').length)
const dangerCount     = computed(() => objectives.value.filter(o => o.status === '위험').length)

async function refresh() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/okrs')
    objectives.value = data
  } finally { loading.value = false }
}

function statusBadgeClass(status) {
  return { '진행중': 'badge badge-blue', '완료': 'badge badge-green', '위험': 'badge badge-red' }[status] || 'badge badge-gray'
}

onMounted(refresh)
</script>

<style scoped>
/* 목표 카드 */
.obj-card { transition: box-shadow .2s, transform .15s; }
.obj-card:hover { box-shadow: var(--shadow-l2); transform: translateY(-1px); }

.obj-id-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px;
  background: var(--primary-light); color: var(--primary);
  border-radius: var(--radius-md);
  font-weight: 700; font-size: 13px;
  flex-shrink: 0;
}

.obj-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* KR */
.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}
.kr-list { display: flex; flex-direction: column; gap: 4px; }
.kr-item {
  display: flex; align-items: center; gap: 8px;
  background: var(--gray-50);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
}

/* 통계 카드 색상 강조 */
.stat-accent { border-top: 3px solid var(--outline); }
.stat-accent-blue    { border-top-color: var(--primary); }
.stat-accent-primary { border-top-color: #6366f1; }
.stat-accent-green   { border-top-color: var(--success); }
.stat-accent-red     { border-top-color: var(--danger); }

.stat-icon { font-size: 20px; margin-bottom: 6px; line-height: 1; }
</style>

<template>
  <div class="page-wrap">
    <div class="page-header">
      <h2 class="page-title-text">보고서 내보내기</h2>
      <p class="page-desc">주간 이슈 내용을 텍스트 보고서로 추출합니다.</p>
    </div>

    <!-- 설정 패널 -->
    <div class="config-panel">
      <div class="config-row">
        <div class="config-field">
          <label class="config-label">파트명</label>
          <input
            v-model="partName"
            class="form-control config-input"
            placeholder="예: 설비혁신파트"
            @blur="savePartName"
          />
        </div>
      </div>

      <div class="config-field">
        <div class="config-label-row">
          <label class="config-label">주차 선택</label>
          <div class="week-actions">
            <button class="btn btn-ghost btn-xs" @click="selectAll">전체 선택</button>
            <button class="btn btn-ghost btn-xs" @click="clearAll">전체 해제</button>
          </div>
        </div>
        <div v-if="loadingWeeks" class="weeks-placeholder">
          <div class="spinner" style="margin:0 auto"></div>
        </div>
        <div v-else-if="availableWeeks.length === 0" class="weeks-empty">
          등록된 이슈가 없습니다.
        </div>
        <div v-else class="week-grid">
          <label
            v-for="w in availableWeeks"
            :key="w"
            class="week-chip"
            :class="{ selected: selectedWeeks.includes(w) }"
          >
            <input type="checkbox" :value="w" v-model="selectedWeeks" class="week-checkbox" />
            {{ weekLabel(w) }}
          </label>
        </div>
      </div>

      <div class="config-actions">
        <button
          class="btn btn-primary"
          :disabled="selectedWeeks.length === 0 || generating"
          @click="generate"
        >
          <span v-if="generating" class="spinner-sm"></span>
          <span v-else class="material-symbols-outlined">preview</span>
          미리보기 생성
        </button>
      </div>
    </div>

    <!-- 결과 영역 -->
    <div v-if="result !== null" class="result-panel">
      <div class="result-header">
        <span class="result-title">
          <span class="material-symbols-outlined">article</span>
          생성된 보고서
        </span>
        <div class="result-actions">
          <button class="btn btn-ghost btn-sm" @click="copyToClipboard">
            <span class="material-symbols-outlined">content_copy</span>
            {{ copied ? '복사됨!' : '클립보드 복사' }}
          </button>
          <button class="btn btn-ghost btn-sm" @click="downloadFile">
            <span class="material-symbols-outlined">download</span>
            파일 다운로드
          </button>
        </div>
      </div>
      <div v-if="result.trim() === ''" class="result-empty">
        선택한 주차에 이슈 데이터가 없습니다.
      </div>
      <textarea v-else class="result-textarea" readonly :value="result"></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const PART_NAME_KEY = 'export_part_name'

const partName       = ref(localStorage.getItem(PART_NAME_KEY) || '설비혁신파트')
const availableWeeks = ref([])
const selectedWeeks  = ref([])
const loadingWeeks   = ref(false)
const generating     = ref(false)
const result         = ref(null)
const copied         = ref(false)

function weekLabel(w) {
  const m = w.match(/(\d{4})-W(\d+)/)
  return m ? `${m[1].slice(2)}년 ${parseInt(m[2])}주차` : w
}

function savePartName() {
  localStorage.setItem(PART_NAME_KEY, partName.value)
}

function selectAll() {
  selectedWeeks.value = [...availableWeeks.value]
}

function clearAll() {
  selectedWeeks.value = []
}

async function generate() {
  if (selectedWeeks.value.length === 0) return
  generating.value = true
  result.value = null
  try {
    const { data } = await axios.get('/api/export/weekly-issues', {
      params: {
        weeks: selectedWeeks.value.join(','),
        part_name: partName.value.trim(),
      },
      responseType: 'text',
    })
    result.value = data
    savePartName()
  } catch (e) {
    alert(e.response?.data?.detail || '생성 중 오류가 발생했습니다.')
  } finally {
    generating.value = false
  }
}

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(result.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback
    const ta = document.createElement('textarea')
    ta.value = result.value
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

function downloadFile() {
  const blob = new Blob([result.value], { type: 'text/plain;charset=utf-8' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  const firstWeek = [...selectedWeeks.value].sort().reverse()[0] || ''
  const m = firstWeek.match(/(\d{4})-W(\d+)/)
  const label = m ? `${m[1]}W${m[2].padStart(2, '0')}` : firstWeek
  a.href = url
  a.download = `${label}_이슈보고서.txt`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  loadingWeeks.value = true
  try {
    const { data } = await axios.get('/api/export/available-weeks')
    availableWeeks.value = data
    // 기본값: 최근 4주 선택
    selectedWeeks.value = data.slice(0, 4)
  } catch (e) {
    console.error(e)
  } finally {
    loadingWeeks.value = false
  }
})
</script>

<style scoped>
.page-wrap {
  max-width: 860px;
  margin: 0 auto;
  padding: 28px 24px;
}
.page-header { margin-bottom: 24px; }
.page-title-text {
  font-size: var(--fs-h2);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  margin: 0 0 4px;
}
.page-desc { font-size: var(--fs-sm); color: var(--text-muted); margin: 0; }

/* 설정 패널 */
.config-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  background: var(--gray-50);
  margin-bottom: 24px;
}
.config-row { display: flex; gap: 16px; flex-wrap: wrap; }
.config-field { display: flex; flex-direction: column; gap: 8px; }
.config-label {
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-primary);
}
.config-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.week-actions { display: flex; gap: 4px; }
.config-input { min-width: 220px; }

/* 주차 그리드 */
.weeks-placeholder,
.weeks-empty {
  padding: 16px 0;
  color: var(--text-muted);
  font-size: var(--fs-sm);
  text-align: center;
}
.week-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.week-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid var(--outline);
  border-radius: 20px;
  background: var(--surface);
  color: var(--text-secondary);
  font-size: var(--fs-sm);
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}
.week-chip:hover { border-color: var(--primary); color: var(--primary); }
.week-chip.selected {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
  font-weight: var(--fw-semibold);
}
.week-checkbox { display: none; }

.config-actions { display: flex; gap: 8px; }
.spinner-sm {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
  margin-right: 2px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 결과 패널 */
.result-panel {
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--outline);
  flex-wrap: wrap;
  gap: 8px;
}
.result-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-primary);
}
.result-title .material-symbols-outlined { font-size: 18px; color: var(--primary); }
.result-actions { display: flex; gap: 6px; }
.result-actions .material-symbols-outlined { font-size: 16px; }
.result-empty {
  padding: 32px;
  text-align: center;
  color: var(--text-muted);
  font-size: var(--fs-sm);
}
.result-textarea {
  width: 100%;
  min-height: 480px;
  padding: 16px;
  font-family: 'Pretendard', monospace;
  font-size: 13px;
  line-height: 1.7;
  border: none;
  resize: vertical;
  background: var(--surface);
  color: var(--text-primary);
  box-sizing: border-box;
  outline: none;
}
</style>

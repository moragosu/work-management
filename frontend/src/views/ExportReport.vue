<template>
  <div class="page-wrap">
    <div class="er-page-header">
      <h2 class="page-title-text">보고서 내보내기</h2>
      <p class="page-desc">주간 이슈 내용을 텍스트 보고서로 추출합니다.</p>
    </div>

    <!-- 설정 패널 -->
    <div class="config-panel">
      <div class="config-top-row">
        <div class="config-field">
          <label class="config-label">파트명</label>
          <input
            v-model="partName"
            class="form-control config-input"
            placeholder="예: 설비혁신파트"
            @blur="savePartName"
          />
        </div>
        <div class="config-field">
          <label class="config-label">형식</label>
          <div class="format-toggle">
            <button
              class="fmt-btn"
              :class="{ active: format === 'text' }"
              @click="format = 'text'"
            >
              <span class="material-symbols-outlined">article</span>텍스트
            </button>
            <button
              class="fmt-btn"
              :class="{ active: format === 'markdown' }"
              @click="format = 'markdown'"
            >
              <span class="material-symbols-outlined">code</span>마크다운
            </button>
          </div>
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
          <span class="result-fmt-badge">{{ format === 'markdown' ? 'Markdown' : '텍스트' }}</span>
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
      <template v-else>
        <div v-if="format === 'markdown'" class="result-md-preview" v-html="renderedMarkdown"></div>
        <textarea v-else class="result-textarea" readonly :value="result"></textarea>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const PART_NAME_KEY = 'export_part_name'

const partName       = ref(localStorage.getItem(PART_NAME_KEY) || '설비혁신파트')
const availableWeeks = ref([])
const selectedWeeks  = ref([])
const loadingWeeks   = ref(false)
const generating     = ref(false)
const result         = ref(null)
const copied         = ref(false)
const format         = ref('text')

const renderedMarkdown = computed(() => {
  if (!result.value || format.value !== 'markdown') return ''
  return marked(result.value, { breaks: true, gfm: true })
})

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
        fmt: format.value,
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
  const ext = format.value === 'markdown' ? 'md' : 'txt'
  const blob = new Blob([result.value], { type: 'text/plain;charset=utf-8' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  const firstWeek = [...selectedWeeks.value].sort().reverse()[0] || ''
  const m = firstWeek.match(/(\d{4})-W(\d+)/)
  const label = m ? `${m[1]}W${m[2].padStart(2, '0')}` : firstWeek
  a.href = url
  a.download = `${label}_이슈보고서.${ext}`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  loadingWeeks.value = true
  try {
    const { data } = await axios.get('/api/export/available-weeks')
    availableWeeks.value = data
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
  max-width: none;
  padding: 28px 24px;
}
.er-page-header { margin-bottom: 24px; }
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
.config-top-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  align-items: flex-end;
}
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

/* 형식 토글 */
.format-toggle {
  display: flex;
  border: 1px solid var(--outline);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--surface);
}
.fmt-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 16px;
  font-size: var(--fs-sm);
  font-weight: var(--fw-medium);
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}
.fmt-btn .material-symbols-outlined { font-size: 15px; }
.fmt-btn + .fmt-btn { border-left: 1px solid var(--outline); }
.fmt-btn.active {
  background: var(--primary);
  color: white;
  font-weight: var(--fw-semibold);
}

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
.result-fmt-badge {
  font-size: var(--fs-2xs);
  font-weight: var(--fw-semibold);
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--primary-light);
  color: var(--primary);
}
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
  min-height: 600px;
  padding: 20px 24px;
  font-family: 'Pretendard', 'D2Coding', monospace;
  font-size: 13px;
  line-height: 1.75;
  border: none;
  resize: vertical;
  background: var(--surface);
  color: var(--text-primary);
  box-sizing: border-box;
  outline: none;
}
.result-md-preview {
  min-height: 600px;
  padding: 24px 32px;
  background: var(--surface);
  color: var(--text-primary);
  font-size: var(--fs-md);
  line-height: 1.8;
  overflow-x: auto;
}
.result-md-preview :deep(h1),
.result-md-preview :deep(h2),
.result-md-preview :deep(h3) {
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  margin: 1.4em 0 0.5em;
  line-height: 1.4;
}
.result-md-preview :deep(h2) { font-size: 1.15em; }
.result-md-preview :deep(h3) { font-size: 1.05em; }
.result-md-preview :deep(strong) { font-weight: var(--fw-semibold); color: var(--text-primary); }
.result-md-preview :deep(ul),
.result-md-preview :deep(ol) {
  padding-left: 1.5em;
  margin: 0.4em 0;
}
.result-md-preview :deep(li) { margin: 0.2em 0; }
.result-md-preview :deep(a) {
  color: var(--primary);
  text-decoration: underline;
  word-break: break-all;
}
.result-md-preview :deep(code) {
  background: var(--gray-100);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: 'D2Coding', monospace;
  font-size: 0.9em;
}
.result-md-preview :deep(p) { margin: 0.3em 0; }
</style>

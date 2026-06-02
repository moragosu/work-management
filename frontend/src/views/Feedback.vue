<template>
  <div>
    <div class="page-header">
      <div>
        <h2>피드백</h2>
        <div class="subtitle">버그 리포트 · 기능 요청 · 기타 의견을 자유롭게 남겨주세요</div>
      </div>
      <button class="btn btn-primary btn-sm" @click="openAdd" data-tooltip="새 피드백 작성">
        <span class="material-symbols-outlined" style="font-size:16px;vertical-align:-3px">add</span>
        새 피드백
      </button>
    </div>

    <div class="page-body">
      <!-- 카테고리 필터 -->
      <div class="filter-bar">
        <button
          v-for="c in categoryOptions" :key="c.value"
          class="filter-chip"
          :class="{ active: selectedCategory === c.value }"
          @click="selectedCategory = c.value"
        >
          <span class="filter-chip-dot" :class="'dot-' + c.value"></span>
          {{ c.label }}
          <span class="filter-chip-count">{{ countByCategory(c.value) }}</span>
        </button>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="loading-center" style="padding:48px"><div class="spinner"></div></div>

      <!-- 목록 비어있음 -->
      <div v-else-if="filteredFeedbacks.length === 0" class="empty-state">
        <span class="material-symbols-outlined empty-icon">inbox</span>
        <div>등록된 피드백이 없습니다.</div>
      </div>

      <!-- 목록 -->
      <div v-else class="feedback-list">
        <div v-for="fb in filteredFeedbacks" :key="fb.id" class="feedback-card">
          <div class="feedback-card-header">
            <span class="category-badge" :class="'cat-' + fb.category">{{ CATEGORY_LABEL[fb.category] }}</span>
            <span class="feedback-title">{{ fb.title }}</span>
            <div class="feedback-meta">
              <span class="badge badge-gray">{{ fb.author }}</span>
              <span class="meta-date">{{ fb.updated_at ?? fb.created_at }}</span>
              <span v-if="fb.updated_at" class="meta-edited">수정됨</span>
              <button class="btn btn-ghost btn-xs" @click="startEdit(fb)" data-tooltip="수정">수정</button>
              <button class="btn btn-danger btn-xs" @click="deleteFeedback(fb.id)" data-tooltip="삭제">삭제</button>
            </div>
          </div>
          <div class="feedback-card-body">
            <TiptapPreview :modelValue="fb.content" />
          </div>
        </div>
      </div>
    </div>

    <!-- 작성/수정 모달 -->
    <Teleport to="body">
      <div v-if="form.open" class="fb-modal-overlay" @click.self="closeForm">
        <div class="fb-modal">
          <div class="fb-modal-header">
            <span>{{ form.id ? '피드백 수정' : '새 피드백' }}</span>
            <button class="dash-modal-close" @click="closeForm">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div class="fb-modal-body">
            <div class="form-group">
              <label class="form-label">카테고리 <span style="color:var(--danger)">*</span></label>
              <div class="cat-radio-group">
                <label v-for="c in categoryOptions.slice(1)" :key="c.value" class="cat-radio" :class="{ active: form.category === c.value }">
                  <input type="radio" v-model="form.category" :value="c.value" style="display:none" />
                  <span class="category-badge" :class="'cat-' + c.value">{{ c.label }}</span>
                </label>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">작성자 <span style="color:var(--danger)">*</span></label>
              <select v-model="form.author" class="form-control" style="max-width:200px">
                <option value="">선택</option>
                <option v-for="s in staffList" :key="s.username" :value="s.name">{{ s.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">제목 <span style="color:var(--danger)">*</span></label>
              <input v-model="form.title" class="form-control" placeholder="간단한 제목을 입력하세요" maxlength="100" />
            </div>
            <div class="form-group">
              <label class="form-label">내용</label>
              <TiptapEditor v-model="form.content" height="200px" @image-uploaded="url => sessionUploads.push(url)" />
            </div>
          </div>
          <div class="fb-modal-footer">
            <button class="btn btn-ghost btn-sm" @click="closeForm">취소</button>
            <button class="btn btn-primary btn-sm" @click="submitForm" :disabled="!form.category || !form.author || !form.title.trim()">
              {{ form.id ? '저장' : '등록' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import axios from 'axios'
import TiptapPreview from '../components/TiptapPreview.vue'
import TiptapEditor from '../components/TiptapEditor.vue'
import { useToast } from '../composables/useToast.js'
import { deleteOrphanedImages, deleteAllImages, deleteUrls } from '../composables/useImageCleanup.js'

const { toastMsg, showToast, toastError } = useToast()

const CATEGORY_LABEL = { bug: '버그', feature: '기능요청', other: '기타' }
const categoryOptions = [
  { value: 'all',     label: '전체' },
  { value: 'bug',     label: '버그' },
  { value: 'feature', label: '기능요청' },
  { value: 'other',   label: '기타' },
]

const feedbacks = ref([])
const staffList = ref([])
const loading = ref(false)
const selectedCategory = ref('all')

const filteredFeedbacks = computed(() =>
  selectedCategory.value === 'all'
    ? feedbacks.value
    : feedbacks.value.filter(f => f.category === selectedCategory.value)
)

function countByCategory(cat) {
  if (cat === 'all') return feedbacks.value.length
  return feedbacks.value.filter(f => f.category === cat).length
}

// ── 폼 상태 ──
const form = reactive({ open: false, id: '', category: 'bug', title: '', content: '', author: '' })
const sessionUploads = ref([])

function openAdd() {
  form.id = ''; form.category = 'bug'; form.title = ''; form.content = ''; form.author = ''
  sessionUploads.value = []
  form.open = true
}
function startEdit(fb) {
  form.id = fb.id; form.category = fb.category; form.title = fb.title
  form.content = fb.content; form.author = fb.author
  sessionUploads.value = []
  form.open = true
}
function closeForm() {
  // 취소 시 이번 세션에서 업로드했으나 저장되지 않은 파일 삭제
  deleteUrls(sessionUploads.value)
  sessionUploads.value = []
  form.open = false
}

async function submitForm() {
  if (!form.category || !form.author || !form.title.trim()) return
  try {
    if (form.id) {
      const oldContent = feedbacks.value.find(f => f.id === form.id)?.content
      const { data } = await axios.put(`/api/feedback/${form.id}`, {
        category: form.category, title: form.title, content: form.content, author: form.author,
      })
      await deleteOrphanedImages(oldContent, form.content)
      await deleteUrls(sessionUploads.value.filter(u => !form.content.includes(u)))
      feedbacks.value = feedbacks.value.map(f => f.id === form.id ? data : f)
      showToast('수정되었습니다')
    } else {
      const { data } = await axios.post('/api/feedback', {
        category: form.category, title: form.title, content: form.content, author: form.author,
      })
      await deleteUrls(sessionUploads.value.filter(u => !form.content.includes(u)))
      feedbacks.value = [data, ...feedbacks.value]
      showToast('등록되었습니다')
    }
    sessionUploads.value = []
    closeForm()
  } catch (e) { toastError(e, '저장 실패') }
}

async function deleteFeedback(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try {
    const target = feedbacks.value.find(f => f.id === id)
    await axios.delete(`/api/feedback/${id}`)
    await deleteAllImages(target?.content)
    feedbacks.value = feedbacks.value.filter(f => f.id !== id)
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '삭제 실패') }
}

async function fetchAll() {
  loading.value = true
  try {
    const [fbRes, sRes] = await Promise.all([axios.get('/api/feedback'), axios.get('/api/staff')])
    feedbacks.value = fbRes.data
    staffList.value = sRes.data
  } finally { loading.value = false }
}

onMounted(fetchAll)
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 20px;
  border: 1px solid var(--outline);
  background: var(--surface);
  font-size: var(--fs-sm);
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.15s;
}
.filter-chip.active { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }
.filter-chip-dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-all { background: var(--gray-400); }
.dot-bug { background: var(--danger); }
.dot-feature { background: var(--primary); }
.dot-other { background: var(--text-muted); }
.filter-chip-count { font-size: var(--fs-2xs); background: var(--gray-100); border-radius: 10px; padding: 1px 6px; color: var(--text-muted); }
.filter-chip.active .filter-chip-count { background: var(--primary-light); color: var(--primary); }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--text-muted);
  font-size: var(--fs-md);
}
.empty-icon { font-size: 40px; color: var(--gray-300); }

.feedback-list { display: flex; flex-direction: column; gap: 12px; }

.feedback-card {
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: var(--radius);
  overflow: hidden;
}
.feedback-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--outline);
  flex-wrap: wrap;
}
.feedback-title {
  font-size: var(--fs-md);
  font-weight: var(--fw-semibold);
  color: var(--text-primary);
  flex: 1;
  min-width: 0;
}
.feedback-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.feedback-card-body { padding: 12px 16px; }

.category-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-2xs);
  font-weight: var(--fw-semibold);
  white-space: nowrap;
}
.cat-bug     { background: var(--danger-light);   color: var(--danger); }
.cat-feature { background: var(--primary-light);  color: var(--primary); }
.cat-other   { background: var(--gray-100);       color: var(--gray-600); }

/* 모달 */
.fb-modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 1000;
  display: flex; align-items: center; justify-content: center;
}
.fb-modal {
  background: var(--surface);
  border-radius: var(--radius-lg);
  width: 600px;
  max-width: 92vw;
  max-height: 85vh;
  display: flex; flex-direction: column;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  animation: modal-in 0.15s ease;
}
@keyframes modal-in {
  from { opacity:0; transform: translateY(8px); }
  to   { opacity:1; transform: translateY(0); }
}
.fb-modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--outline);
  font-weight: var(--fw-semibold); font-size: var(--fs-base);
  flex-shrink: 0;
}
.fb-modal-body { flex: 1; overflow-y: auto; padding: 16px 20px; display: flex; flex-direction: column; gap: 14px; }
.fb-modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--outline);
  flex-shrink: 0;
}

.cat-radio-group { display: flex; gap: 8px; flex-wrap: wrap; }
.cat-radio { cursor: pointer; }
.cat-radio .category-badge { padding: 5px 14px; font-size: var(--fs-sm); border: 2px solid transparent; transition: border-color 0.15s; }
.cat-radio.active .category-badge { border-color: currentColor; }
</style>

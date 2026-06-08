<template>
  <div class="page-wrap">
    <div class="ih-page-header">
      <h2 class="page-title-text">삭제된 이슈 히스토리</h2>
      <p class="page-desc">삭제된 이슈와 댓글 내역을 조회합니다. 파트장·관리자만 접근 가능합니다.</p>
    </div>

    <!-- 필터 -->
    <div class="filter-bar">
      <div class="filter-row">
        <div class="filter-group">
          <span class="filter-label">주차</span>
          <select v-model="filterWeek" class="form-control filter-select" @change="load">
            <option value="">전체</option>
            <option v-for="w in weeks" :key="w" :value="w">{{ weekLabel(w) }}</option>
          </select>
        </div>
        <div class="filter-divider"></div>
        <div class="filter-group">
          <span class="filter-label">과제</span>
          <select v-model="filterTask" class="form-control filter-select" @change="load">
            <option value="">전체</option>
            <option v-for="t in tasks" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>
        <span class="filter-count">{{ items.length }}건</span>
      </div>
    </div>

    <!-- 목록 -->
    <div v-if="loading" class="empty-state">불러오는 중...</div>
    <div v-else-if="items.length === 0" class="empty-state">
      <span class="material-symbols-outlined empty-icon">history</span>
      <p>삭제된 이슈가 없습니다.</p>
    </div>

    <div v-else class="history-list">
      <div v-for="item in items" :key="item.id" class="history-card">
        <!-- 카드 헤더 -->
        <div class="card-header" @click="toggle(item.id)">
          <div class="card-meta">
            <span class="badge badge-gray">{{ weekLabel(item.week) }}</span>
            <span class="task-name">{{ taskName(item.task_id) }}</span>
            <span v-if="item.assignee" class="badge" style="background:var(--primary-light);color:var(--primary)">{{ item.assignee }}</span>
            <span v-if="item.comments_snapshot?.length" class="comment-count">
              <span class="material-symbols-outlined" style="font-size:13px;vertical-align:-2px">chat_bubble_outline</span>
              {{ item.comments_snapshot.length }}개
            </span>
          </div>
          <div class="card-right">
            <span class="del-info">{{ item.deleted_by }} 삭제 · {{ formatDate(item.deleted_at) }}</span>
            <span class="material-symbols-outlined expand-icon" :class="{ open: expanded.has(item.id) }">
              expand_more
            </span>
          </div>
        </div>

        <!-- 카드 본문 (펼쳐졌을 때) -->
        <div v-if="expanded.has(item.id)" class="card-body">
          <!-- 이슈 내용 -->
          <div class="issue-box">
            <TiptapPreview :modelValue="item.issue" />
          </div>

          <!-- 댓글 목록 -->
          <div v-if="item.comments_snapshot?.length" class="comment-section">
            <div class="comment-section-label">
              <span class="material-symbols-outlined">chat_bubble_outline</span>
              댓글 {{ item.comments_snapshot.length }}개
            </div>
            <div v-for="c in item.comments_snapshot" :key="c.id" class="comment-item">
              <div class="comment-meta-row">
                <span class="badge badge-gray">{{ c.comment_by }}</span>
                <template v-if="c.tagged_users?.length">
                  <span class="material-symbols-outlined" style="font-size:12px;color:var(--text-muted)">arrow_forward</span>
                  <span v-for="t in c.tagged_users" :key="t" class="badge" style="font-size:11px;padding:1px 6px;background:var(--primary-light);color:var(--primary);border:1px solid var(--primary);border-radius:99px">{{ t }}</span>
                </template>
                <span v-if="c.requires_answer" class="badge-requires">
                  <span class="material-symbols-outlined" style="font-size:11px;vertical-align:-2px">{{ c.is_answered ? 'check_circle' : 'hourglass_empty' }}</span>
                  {{ c.is_answered ? '답변됨' : '답변 대기' }}
                </span>
                <span class="meta-date">{{ c.created_at?.slice(0, 19) }}</span>
              </div>
              <div class="comment-body">
                <TiptapPreview :modelValue="c.comment" />
              </div>
              <!-- 대댓글 -->
              <div v-for="r in (c.replies || [])" :key="r.id" class="reply-item">
                <div class="reply-line"></div>
                <div class="reply-body">
                  <div class="comment-meta-row">
                    <span class="badge badge-gray">{{ r.comment_by }}</span>
                    <span class="meta-date">{{ r.created_at?.slice(0, 19) }}</span>
                  </div>
                  <div class="comment-body">
                    <TiptapPreview :modelValue="r.comment" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 영구 삭제 (관리자만) -->
          <div v-if="auth.isAdmin" class="card-footer">
            <button class="btn btn-danger btn-xs" @click="permanentDelete(item.id)">영구 삭제</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import TiptapPreview from '../components/TiptapPreview.vue'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()

const items    = ref([])
const tasks    = ref([])
const weeks    = ref([])
const loading  = ref(false)
const expanded = ref(new Set())
const filterWeek = ref('')
const filterTask = ref('')

function weekLabel(w) {
  if (!w) return ''
  const m = w.match(/(\d{4})-W(\d+)/)
  return m ? `${m[1].slice(2)}년 ${parseInt(m[2])}주차` : w
}

function taskName(id) {
  const t = tasks.value.find(t => t.id === id)
  return t ? t.name : id
}

function formatDate(dt) {
  if (!dt) return ''
  return dt.slice(0, 16).replace('T', ' ')
}

function toggle(id) {
  if (expanded.value.has(id)) {
    expanded.value.delete(id)
  } else {
    expanded.value.add(id)
  }
}

async function load() {
  loading.value = true
  try {
    const params = {}
    if (filterWeek.value) params.week = filterWeek.value
    if (filterTask.value) params.task_id = filterTask.value
    const { data } = await axios.get('/api/deleted-issues', { params })
    items.value = data
    // 주차 목록 추출
    const ws = [...new Set(data.map(i => i.week).filter(Boolean))].sort().reverse()
    weeks.value = ws
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function permanentDelete(id) {
  if (!confirm('히스토리에서 영구 삭제하시겠습니까? 복구할 수 없습니다.')) return
  try {
    await axios.delete(`/api/deleted-issues/${id}`)
    items.value = items.value.filter(i => i.id !== id)
    expanded.value.delete(id)
  } catch (e) {
    alert(e.response?.data?.detail || '삭제 실패')
  }
}

onMounted(async () => {
  const [, tasksRes] = await Promise.all([
    load(),
    axios.get('/api/tasks').catch(() => ({ data: [] })),
  ])
  tasks.value = tasksRes.data || []
})
</script>

<style scoped>
.page-wrap {
  max-width: none;
  padding: 28px 24px;
}
.ih-page-header { margin-bottom: 20px; }
.page-title-text {
  font-size: var(--fs-h2);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  margin: 0 0 4px;
}
.page-desc {
  font-size: var(--fs-sm);
  color: var(--text-muted);
  margin: 0;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 20px;
  padding: 10px 16px;
  background: var(--gray-50);
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
}
.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  flex: 1;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 6px;
}
.filter-label {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  font-weight: var(--fw-semibold);
  flex-shrink: 0;
}
.filter-divider {
  width: 1px;
  height: 18px;
  background: var(--outline);
  flex-shrink: 0;
}
.filter-select { width: auto; min-width: 130px; font-size: var(--fs-sm); }
.filter-count {
  font-size: var(--fs-sm);
  color: var(--text-muted);
  margin-left: auto;
  font-weight: var(--fw-medium);
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 56px 0;
  color: var(--text-muted);
  font-size: var(--fs-sm);
}
.empty-icon {
  font-size: 40px;
  display: block;
  margin: 0 auto 10px;
  color: var(--gray-300);
}

.history-list { display: flex; flex-direction: column; gap: 10px; }

.history-card {
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  background: var(--surface);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
  gap: 12px;
  transition: background 0.12s;
}
.card-header:hover { background: var(--gray-50); }

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}
.task-name {
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-primary);
}
.comment-count {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 2px;
}

.card-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.del-info {
  font-size: var(--fs-xs);
  color: var(--text-muted);
}
.expand-icon {
  font-size: 20px;
  color: var(--text-muted);
  transition: transform 0.2s;
}
.expand-icon.open { transform: rotate(180deg); }

.card-body {
  border-top: 1px solid var(--outline);
  padding: 14px 16px;
}

.issue-box {
  background: #fff7ed;
  border-left: 3px solid #f59e0b;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
  margin-bottom: 12px;
}

.comment-section {
  background: var(--gray-50);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  margin-bottom: 12px;
}
.comment-section-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--fs-xs);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  margin-bottom: 8px;
}
.comment-section-label .material-symbols-outlined { font-size: 14px; }

.comment-item {
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  margin-bottom: 6px;
}
.comment-item:last-child { margin-bottom: 0; }

.comment-meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 4px;
  font-size: var(--fs-xs);
}
.comment-body { font-size: var(--fs-sm); }

.badge-requires {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 99px;
  background: var(--warning-light);
  color: var(--warning);
  border: 1px solid var(--warning);
  font-weight: var(--fw-semibold);
}

.reply-item {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}
.reply-line {
  width: 2px;
  flex-shrink: 0;
  background: var(--outline);
  border-radius: 1px;
  align-self: stretch;
  min-height: 20px;
}
.reply-body {
  flex: 1;
  min-width: 0;
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
}

.card-footer {
  padding-top: 10px;
  border-top: 1px solid var(--outline);
  display: flex;
  justify-content: flex-end;
}

.meta-date {
  font-size: var(--fs-2xs);
  color: var(--text-muted);
}
</style>

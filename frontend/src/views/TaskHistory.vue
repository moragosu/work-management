<template>
  <div class="page-container">
    <div v-if="loading" class="loading-state">
      <span class="material-symbols-outlined spin">progress_activity</span>
      불러오는 중…
    </div>

    <template v-else-if="task">
      <!-- 헤더 -->
      <div class="page-header">
        <button class="back-btn" @click="route.query.back ? $router.push(decodeURIComponent(String(route.query.back))) : $router.back()">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <div class="header-content">
          <div class="header-top">
            <span v-if="task.objective_id" class="obj-badge">{{ task.objective_id }}</span>
            <h2 class="page-title">{{ task.id }} · {{ task.name }}</h2>
          </div>
          <div class="header-meta">
            <span v-if="task.target" class="meta-chip">{{ task.target }}</span>
            <span v-for="m in task.members" :key="m.username || m.name" class="meta-chip member-chip">
              <span class="material-symbols-outlined" style="font-size:12px">person</span>
              {{ m.name }}
            </span>
            <span class="meta-chip week-count-chip">{{ weeks.length }}개 주차 이력</span>
          </div>
        </div>
      </div>

      <!-- 소과제 탭 (있는 경우) -->
      <div v-if="task.sub_tasks?.length" class="subtask-tabs card">
        <div class="card-body tab-body">
          <button
            class="tab-btn"
            :class="{ active: activeSubTask === null }"
            @click="activeSubTask = null"
          >전체</button>
          <button
            v-for="st in task.sub_tasks"
            :key="st.id"
            class="tab-btn"
            :class="{ active: activeSubTask === st.id, done: st.done }"
            @click="activeSubTask = st.id"
          >
            <span v-if="st.done" class="material-symbols-outlined" style="font-size:13px;color:var(--success)">check_circle</span>
            {{ st.id }} · {{ st.name }}
          </button>
        </div>
      </div>

      <!-- 데이터 없음 -->
      <div v-if="filteredWeeks.length === 0" class="empty-state card">
        <div class="card-body">
          <span class="material-symbols-outlined empty-icon">history</span>
          <p>등록된 이력이 없습니다.</p>
        </div>
      </div>

      <!-- 주차별 타임라인 -->
      <div v-for="(entry, idx) in filteredWeeks" :key="entry.week" class="week-card card">
        <div class="week-header" @click="toggleWeek(entry.week)">
          <div class="week-header-left">
            <span class="material-symbols-outlined week-chevron" :class="{ open: isOpen(entry.week) }">expand_more</span>
            <span class="week-label">{{ formatWeekLabel(entry.week) }}</span>
            <span class="week-range">{{ getWeekDateRange(entry.week) }}</span>
          </div>
          <div class="week-badges">
            <span v-if="visibleIssues(entry).length" class="w-badge badge-issue">
              <span class="material-symbols-outlined" style="font-size:12px">warning</span>
              이슈 {{ visibleIssues(entry).length }}
            </span>
            <span v-if="visibleQuestions(entry).length" class="w-badge badge-qa">
              <span class="material-symbols-outlined" style="font-size:12px">forum</span>
              Q&A {{ visibleQuestions(entry).length }}
            </span>
            <span v-if="visibleLinks(entry).length" class="w-badge badge-link">
              <span class="material-symbols-outlined" style="font-size:12px">link</span>
              링크 {{ visibleLinks(entry).length }}
            </span>
          </div>
        </div>

        <div v-if="isOpen(entry.week)" class="week-body">

          <!-- 컨플루언스 링크 -->
          <div v-if="visibleLinks(entry).length" class="history-block">
            <div class="block-title">
              <span class="material-symbols-outlined block-icon icon-link">link</span>
              컨플루언스
            </div>
            <div class="link-list">
              <a
                v-for="lnk in visibleLinks(entry)"
                :key="lnk.id"
                :href="lnk.url"
                target="_blank"
                rel="noopener"
                class="confluence-link"
              >
                <span class="material-symbols-outlined" style="font-size:14px">open_in_new</span>
                <span class="link-tid">{{ subTaskLabel(lnk.task_id) }}</span>
                <span class="link-url">{{ lnk.url }}</span>
              </a>
            </div>
          </div>

          <!-- 이슈 목록 -->
          <div v-if="visibleIssues(entry).length" class="history-block">
            <div class="block-title">
              <span class="material-symbols-outlined block-icon icon-issue">warning</span>
              이슈
            </div>
            <div v-for="iss in visibleIssues(entry)" :key="iss.id" class="history-item issue-item clickable" @click="goToIssue(entry.week, iss.id)">
              <div class="item-meta">
                <span class="meta-tid">{{ subTaskLabel(iss.task_id) }}</span>
                <span class="badge badge-gray">{{ iss.assignee }}</span>
                <span class="meta-date">{{ iss.created_at }}</span>
                <span class="goto-hint"><span class="material-symbols-outlined">open_in_new</span></span>
              </div>
              <TiptapPreview :modelValue="iss.issue" />

              <!-- 이슈 댓글 -->
              <div v-if="iss.comments?.length" class="comments-section">
                <div v-for="c in iss.comments" :key="c.id" class="comment">
                  <div class="comment-meta">
                    <span class="material-symbols-outlined" style="font-size:12px;color:var(--text-muted)">subdirectory_arrow_right</span>
                    <span class="badge badge-gray">{{ c.comment_by }}</span>
                    <span class="meta-date">{{ c.created_at?.slice(0, 19) }}</span>
                  </div>
                  <TiptapPreview :modelValue="c.comment" />
                  <div v-for="r in c.replies" :key="r.id" class="reply">
                    <span class="material-symbols-outlined" style="font-size:11px;color:var(--text-muted)">subdirectory_arrow_right</span>
                    <span class="badge badge-gray">{{ r.comment_by }}</span>
                    <span class="meta-date">{{ r.created_at?.slice(0, 19) }}</span>
                    <TiptapPreview :modelValue="r.comment" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Q&A 목록 -->
          <div v-if="visibleQuestions(entry).length" class="history-block">
            <div class="block-title">
              <span class="material-symbols-outlined block-icon icon-qa">forum</span>
              의견/질문
            </div>
            <div v-for="q in visibleQuestions(entry)" :key="q.id" class="history-item qa-item clickable" @click="goToQuestion(entry.week, q.id)">
              <div class="item-meta">
                <span class="meta-tid">{{ subTaskLabel(q.task_id) }}</span>
                <span class="badge badge-gray">{{ q.questioner }}</span>
                <span v-if="q.targets?.length" class="meta-targets">
                  → {{ q.targets.join(', ') }}
                </span>
                <span class="meta-date">{{ q.created_at?.slice(0, 19) }}</span>
                <span class="goto-hint"><span class="material-symbols-outlined">open_in_new</span></span>
              </div>
              <TiptapPreview :modelValue="q.question" />

              <!-- 답변 없음 -->
              <div v-if="!q.answers?.length" class="no-answer">
                <span class="inline-badge badge-unanswered">미답변</span>
              </div>

              <!-- 답변 목록 -->
              <div v-for="a in q.answers" :key="a.id" class="answer">
                <div class="answer-meta">
                  <span class="inline-badge badge-answered">A</span>
                  <span class="badge badge-gray">{{ a.answer_by }}</span>
                  <span class="meta-date">{{ a.created_at?.slice(0, 19) }}</span>
                </div>
                <TiptapPreview :modelValue="a.answer" />
                <div v-for="r in a.replies" :key="r.id" class="reply">
                  <span class="material-symbols-outlined" style="font-size:11px;color:var(--text-muted)">subdirectory_arrow_right</span>
                  <span class="badge badge-gray">{{ r.reply_by }}</span>
                  <span class="meta-date">{{ r.created_at?.slice(0, 19) }}</span>
                  <TiptapPreview :modelValue="r.reply" />
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </template>

    <div v-else class="empty-state card">
      <div class="card-body">
        <span class="material-symbols-outlined empty-icon">error_outline</span>
        <p>과제를 찾을 수 없습니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { formatWeekLabel, getWeekDateRange } from '../utils/week.js'
import TiptapPreview from '../components/TiptapPreview.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const task = ref(null)
const weeks = ref([])
const activeSubTask = ref(null)
const openWeeks = ref(new Set())

function goToIssue(week, issueId) {
  router.push({ path: '/progress', query: { week, focusIssueId: issueId } })
}

function goToQuestion(week, questionId) {
  router.push({ path: '/progress', query: { week, focusQuestion: questionId } })
}

async function fetchHistory() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/tasks/${route.params.id}/history`)
    task.value = data.task
    weeks.value = data.weeks
    // 최근 2개 주차 기본 펼침
    data.weeks.slice(0, 2).forEach(w => openWeeks.value.add(w.week))
    // URL ?sub=T1-1 이 있으면 해당 소과제 칩 자동 활성화
    if (route.query.sub) {
      const subId = String(route.query.sub)
      const exists = data.task?.sub_tasks?.some(s => s.id === subId)
      if (exists) activeSubTask.value = subId
    }
  } finally {
    loading.value = false
  }
}

function toggleWeek(week) {
  if (openWeeks.value.has(week)) openWeeks.value.delete(week)
  else openWeeks.value.add(week)
}
function isOpen(week) { return openWeeks.value.has(week) }

const subTaskNameMap = computed(() => {
  const map = {}
  for (const st of task.value?.sub_tasks ?? []) map[st.id] = st.name
  return map
})

function subTaskLabel(taskId) {
  const name = subTaskNameMap.value[taskId]
  return name ? `${taskId} · ${name}` : taskId
}

const filteredWeeks = computed(() => {
  if (!activeSubTask.value) return weeks.value
  return weeks.value.filter(entry =>
    visibleIssues(entry).length ||
    visibleQuestions(entry).length ||
    visibleLinks(entry).length
  )
})

function visibleIssues(entry) {
  if (!activeSubTask.value) return entry.issues
  return entry.issues.filter(i => i.task_id === activeSubTask.value)
}
function visibleQuestions(entry) {
  if (!activeSubTask.value) return entry.questions
  return entry.questions.filter(q => q.task_id === activeSubTask.value)
}
function visibleLinks(entry) {
  if (!activeSubTask.value) return entry.confluence_links
  return entry.confluence_links.filter(l => l.task_id === activeSubTask.value)
}

onMounted(fetchHistory)
</script>

<style scoped>
/* 로딩 */
.loading-state {
  display: flex; align-items: center; gap: 8px;
  color: var(--text-muted); font-size: var(--fs-sm); padding: 40px 0;
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 헤더 */
.page-header {
  display: flex; align-items: flex-start; gap: 12px;
  margin-bottom: 16px;
}
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; flex-shrink: 0;
  background: var(--gray-50); border: 1px solid var(--outline);
  border-radius: var(--radius-md); cursor: pointer; color: var(--text-secondary);
  transition: background 0.15s;
}
.back-btn:hover { background: var(--primary-light); color: var(--primary); }
.header-content { flex: 1; min-width: 0; }
.header-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
.obj-badge {
  padding: 2px 8px; border-radius: 10px;
  background: var(--primary-light); color: var(--primary);
  font-size: var(--fs-2xs); font-weight: var(--fw-bold); flex-shrink: 0;
}
.page-title { font-size: var(--fs-h2); font-weight: var(--fw-bold); color: var(--text-primary); margin: 0; }
.header-meta { display: flex; flex-wrap: wrap; gap: 6px; }
.meta-chip {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 8px; border-radius: 10px;
  background: var(--gray-100); color: var(--text-secondary);
  font-size: var(--fs-2xs);
}
.member-chip { background: #f0fdf4; color: #15803d; }
.week-count-chip { background: #eff6ff; color: var(--primary); }

/* 소과제 탭 */
.subtask-tabs { margin-bottom: 12px; }
.tab-body { display: flex; flex-wrap: wrap; gap: 6px; }
.tab-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 5px 12px; border-radius: 16px;
  border: 1px solid var(--outline); background: var(--gray-50);
  font-size: var(--fs-xs); font-weight: var(--fw-medium); color: var(--text-secondary);
  cursor: pointer; transition: all 0.15s;
}
.tab-btn:hover { border-color: var(--primary); color: var(--primary); }
.tab-btn.active { background: var(--primary); border-color: var(--primary); color: #fff; }
.tab-btn.done { opacity: 0.6; }

/* 빈 상태 */
.empty-state .card-body {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; padding: 40px 0; color: var(--text-muted);
}
.empty-icon { font-size: 36px; }

/* 주차 카드 */
.week-card { margin-bottom: 12px; overflow: hidden; }
.week-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; cursor: pointer; user-select: none;
  gap: 8px;
  transition: background 0.15s;
}
.week-header:hover { background: var(--gray-50); }
.week-header-left { display: flex; align-items: center; gap: 8px; }
.week-chevron {
  font-size: var(--fs-h2); color: var(--text-muted);
  transition: transform 0.2s; flex-shrink: 0;
}
.week-chevron.open { transform: rotate(180deg); }
.week-label { font-size: var(--fs-md); font-weight: var(--fw-bold); color: var(--text-primary); }
.week-range { font-size: var(--fs-xs); color: var(--text-muted); }
.week-badges { display: flex; gap: 6px; flex-wrap: wrap; }
.w-badge {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 8px; border-radius: 10px; font-size: var(--fs-2xs); font-weight: var(--fw-semibold);
}
.badge-issue { background: #fff7ed; color: #c2410c; }
.badge-qa { background: #eff6ff; color: var(--primary); }
.badge-link { background: #f0fdf4; color: #15803d; }

/* 주차 본문 */
.week-body {
  padding: 0 16px 16px;
  display: flex; flex-direction: column; gap: 16px;
  border-top: 1px solid var(--outline);
}

/* 블록 */
.history-block { display: flex; flex-direction: column; gap: 8px; }
.block-title {
  display: flex; align-items: center; gap: 6px;
  font-size: var(--fs-xs); font-weight: var(--fw-bold);
  padding-top: 12px;
}
.block-icon { font-size: var(--fs-base); }
.icon-issue { color: var(--warning); }
.icon-qa { color: var(--primary); }
.icon-link { color: var(--success); }

/* 컨플루언스 링크 */
.link-list { display: flex; flex-direction: column; gap: 4px; }
.confluence-link {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 10px; border-radius: 6px;
  background: #f0fdf4; border: 1px solid #bbf7d0;
  color: #15803d; text-decoration: none; font-size: var(--fs-xs);
  transition: background 0.15s;
}
.confluence-link:hover { background: var(--success-light); }
.link-tid { font-weight: var(--fw-semibold); flex-shrink: 0; }
.link-url { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; opacity: 0.8; }

/* 이슈 / QA 아이템 */
.history-item {
  border-radius: var(--radius-md);
  border: 1px solid var(--outline);
  padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.issue-item { border-left: 3px solid var(--warning); }
.qa-item { border-left: 3px solid var(--primary); }
.clickable {
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
}
.clickable:hover { background: var(--gray-50); box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
.goto-hint {
  margin-left: auto;
  display: flex;
  align-items: center;
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.15s;
  font-size: var(--fs-h3);
}
.clickable:hover .goto-hint { opacity: 1; }

.item-meta {
  display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
}
.meta-tid {
  font-size: var(--fs-3xs); font-weight: var(--fw-bold);
  padding: 1px 6px; border-radius: var(--radius-sm);
  background: var(--gray-100); color: var(--text-muted);
}
.meta-targets { font-size: var(--fs-xs); color: var(--primary); }
.meta-date { font-size: var(--fs-2xs); color: var(--text-muted); margin-left: auto; }

/* 이슈 댓글 */
.comments-section {
  display: flex; flex-direction: column; gap: 6px;
  padding-top: 8px;
  border-top: 1px solid var(--outline);
}
.comment { display: flex; flex-direction: column; gap: 2px; }
.comment-meta {
  display: flex; align-items: center; gap: 5px;
  font-size: var(--fs-xs); color: var(--text-secondary);
}
.comment-body { font-size: var(--fs-xs); color: var(--text-secondary); padding-left: 18px; line-height: 1.6; }

/* 답변 */
.no-answer { padding-top: 4px; }
.answer {
  display: flex; flex-direction: column; gap: 4px;
  padding: 8px 10px;
  background: #f8fafc;
  border-radius: 6px;
}
.answer-meta {
  display: flex; align-items: center; gap: 6px;
  font-size: var(--fs-xs); color: var(--text-secondary);
}
/* 대댓글 */
.reply {
  display: flex; align-items: baseline; gap: 5px;
  padding-left: 12px;
  font-size: var(--fs-xs); color: var(--text-secondary);
}
/* 뱃지 */
.inline-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px; border-radius: var(--radius-sm);
  font-size: var(--fs-3xs); font-weight: var(--fw-bold); flex-shrink: 0;
}
.badge-answered { background: var(--success-light); color: var(--success); }
.badge-unanswered { width: auto; padding: 0 6px; background: #fff7ed; color: #c2410c; font-size: var(--fs-3xs); border-radius: var(--radius-sm); }

</style>

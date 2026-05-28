<template>
  <div class="page-wrap">
    <div class="page-header">
      <h1>알림</h1>
      <button v-if="notifications.length > 0" class="btn btn-ghost btn-sm" @click="markAllRead">
        전체 읽음 처리
      </button>
    </div>

    <div v-if="loading" class="empty-state">불러오는 중...</div>
    <div v-else-if="notifications.length === 0" class="empty-state">알림이 없습니다</div>
    <div v-else class="notif-list">
      <div
        v-for="n in notifications"
        :key="n.id"
        class="notif-item"
        :class="{ unread: !n.is_read }"
        @click="handleClick(n)"
      >
        <span class="notif-icon material-symbols-outlined">{{ typeIcon(n.type) }}</span>
        <div class="notif-body">
          <div class="notif-title">{{ n.title }}</div>
          <div class="notif-msg">{{ n.message }}</div>
          <div class="notif-time">{{ formatTime(n.created_at) }}</div>
        </div>
        <button class="notif-del" @click.stop="remove(n.id)" data-tooltip="삭제">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const notifications = ref([])
const loading = ref(true)

const TYPE_ICONS = {
  question_tagged: 'forum',
  answer_received: 'chat_bubble',
  issue_assigned: 'warning',
  notice_updated: 'campaign',
}

function typeIcon(type) {
  return TYPE_ICONS[type] || 'notifications'
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  return d.toLocaleDateString('ko-KR')
}

async function load() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/notifications')
    notifications.value = data
  } finally {
    loading.value = false
  }
}

async function markAllRead() {
  await axios.patch('/api/notifications/read-all')
  notifications.value.forEach(n => { n.is_read = 1 })
}

async function handleClick(n) {
  if (!n.is_read) {
    await axios.patch(`/api/notifications/${n.id}/read`)
    n.is_read = 1
  }
  if (n.link) router.push(n.link)
}

async function remove(id) {
  await axios.delete(`/api/notifications/${id}`)
  notifications.value = notifications.value.filter(n => n.id !== id)
}

onMounted(load)
</script>

<style scoped>
.page-wrap {
  max-width: 640px;
  margin: 0 auto;
  padding: 32px 24px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
}
.empty-state {
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
  padding: 40px 0;
}
.notif-list { display: flex; flex-direction: column; gap: 8px; }
.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.notif-item:hover { background: var(--gray-50, #f9fafb); }
.notif-item.unread {
  border-left: 3px solid var(--primary, #2563eb);
  background: var(--primary-light, #eff6ff);
}
.notif-icon {
  font-size: 20px;
  color: var(--primary, #2563eb);
  flex-shrink: 0;
  margin-top: 2px;
}
.notif-body { flex: 1; min-width: 0; }
.notif-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.notif-msg { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.notif-time { font-size: 11px; color: var(--text-muted); }
.notif-del {
  flex-shrink: 0;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  padding: 2px;
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.15s;
}
.notif-item:hover .notif-del { opacity: 1; }
.notif-del .material-symbols-outlined { font-size: 16px; }
</style>

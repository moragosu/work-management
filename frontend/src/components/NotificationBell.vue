<template>
  <div class="bell-wrap" ref="wrapRef">
    <button class="bell-btn" @click="toggle" data-tooltip="알림">
      <span class="material-symbols-outlined">notifications</span>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>

    <Teleport to="body">
      <div v-if="open" class="bell-dropdown" :style="dropdownStyle" ref="dropRef">
        <div class="bell-header">
          <span class="bell-title">알림 <span v-if="unreadCount > 0" class="bell-unread-label">{{ unreadCount }}개 안읽음</span></span>
          <button v-if="items.length > 0" class="btn btn-ghost btn-xs" @click="markAllRead">전체 읽음</button>
        </div>
        <div v-if="items.length === 0" class="bell-empty">새 알림이 없습니다</div>
        <div v-else class="bell-list">
          <div
            v-for="n in items"
            :key="n.id"
            class="bell-item"
            :class="{ unread: !n.is_read }"
            @click="handleClick(n)"
          >
            <span class="bell-item-icon material-symbols-outlined" :style="{ color: typeColor(n.type) }">{{ typeIcon(n.type) }}</span>
            <div class="bell-item-body">
              <div class="bell-item-title">
                {{ n.title }}
                <span v-if="weekLabel(n.link)" class="bell-item-week">{{ weekLabel(n.link) }}</span>
                <span v-if="n.is_pending" class="bell-item-pending">답변 대기</span>
              </div>
              <div class="bell-item-msg">{{ n.message }}</div>
              <div class="bell-item-time">{{ formatTime(n.created_at) }}</div>
            </div>
            <button class="bell-item-del" @click.stop="remove(n.id)" data-tooltip="삭제">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const open = ref(false)
const items = ref([])
const wrapRef = ref(null)
const dropRef = ref(null)
const dropdownStyle = ref({})

const unreadCount = computed(() => items.value.filter(n => !n.is_read).length)

const TYPE_ICONS = {
  question_tagged: 'forum',
  answer_received: 'chat_bubble',
  issue_assigned: 'warning',
  notice_updated: 'campaign',
}
const TYPE_COLORS = {
  question_tagged: '#2563eb',
  answer_received: '#16a34a',
  issue_assigned:  '#d97706',
  notice_updated:  '#7c3aed',
}
function typeIcon(type)  { return TYPE_ICONS[type]  || 'notifications' }
function typeColor(type) { return TYPE_COLORS[type] || '#6b7280' }

function weekLabel(link) {
  if (!link) return ''
  const m = link.match(/[?&]week=([^&]+)/)
  if (!m) return ''
  // 예: 2025-W21 → 21주차
  const w = m[1].match(/(\d{4})-W(\d+)/)
  return w ? `${w[1].slice(2)}년 ${parseInt(w[2])}주차` : m[1]
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const diff = Math.floor((Date.now() - d) / 1000)
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  return d.toLocaleDateString('ko-KR')
}

async function load() {
  try {
    const { data } = await axios.get('/api/notifications')
    items.value = data
  } catch { /* 미인증 시 무시 */ }
}

async function remove(id) {
  try {
    await axios.delete(`/api/notifications/${id}`)
    items.value = items.value.filter(n => n.id !== id)
  } catch (e) {
    alert(e.response?.data?.detail || '삭제할 수 없습니다')
  }
}

async function markAllRead() {
  await axios.patch('/api/notifications/read-all')
  items.value.forEach(n => { n.is_read = 1 })
}

async function handleClick(n) {
  if (!n.is_read) {
    await axios.patch(`/api/notifications/${n.id}/read`)
    n.is_read = 1
  }
  open.value = false
  if (n.link) router.push(n.link)
}

function toggle() {
  open.value = !open.value
  if (open.value) {
    load()
    nextTick(() => positionDropdown())
  }
}

import { nextTick } from 'vue'

function positionDropdown() {
  if (!wrapRef.value) return
  const rect = wrapRef.value.getBoundingClientRect()
  const dropW = 320
  const vw = window.innerWidth
  // 버튼 오른쪽 정렬, 화면 밖이면 왼쪽으로
  let left = rect.right - dropW
  if (left < 0) left = rect.left
  dropdownStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 6}px`,
    left: `${left}px`,
    zIndex: 9000,
  }
}

function onOutside(e) {
  if (!open.value) return
  if (wrapRef.value?.contains(e.target)) return
  if (dropRef.value?.contains(e.target)) return
  open.value = false
}

let pollInterval = null

onMounted(() => {
  load()
  pollInterval = setInterval(load, 5 * 60 * 1000)
  document.addEventListener('click', onOutside, true)
  window.addEventListener('refresh-notifications', load)
})
onUnmounted(() => {
  clearInterval(pollInterval)
  document.removeEventListener('click', onOutside, true)
  window.removeEventListener('refresh-notifications', load)
})
</script>

<style scoped>
.bell-wrap { position: relative; }
.bell-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--outline, #e5e7eb);
  background: var(--surface, #fff);
  cursor: pointer;
  border-radius: 8px;
  color: var(--text-secondary, #555);
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  transition: background 0.15s, color 0.15s, box-shadow 0.15s;
}
.bell-btn:hover {
  background: var(--primary-light, #eff6ff);
  color: var(--primary, #2563eb);
  border-color: var(--primary, #2563eb);
  box-shadow: 0 2px 6px rgba(37,99,235,0.15);
}
.bell-btn .material-symbols-outlined { font-size: 22px; }
.badge {
  position: absolute;
  top: 3px;
  right: 3px;
  background: #ef4444;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 3px;
  line-height: 1;
}

.bell-dropdown {
  width: 340px;
  background: var(--surface, #fff);
  border: 1px solid var(--outline, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.13);
  overflow: hidden;
}
.bell-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 16px 11px;
  border-bottom: 1px solid var(--outline, #e5e7eb);
}
.bell-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
}
.bell-unread-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--primary, #2563eb);
  background: var(--primary-light, #eff6ff);
  padding: 2px 7px;
  border-radius: 10px;
}
.bell-empty {
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  padding: 28px 16px;
}
.bell-list { max-height: 420px; overflow-y: auto; }
.bell-item {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  padding: 12px 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--outline, #e5e7eb);
  transition: background 0.12s;
  position: relative;
}
.bell-item:last-child { border-bottom: none; }
.bell-item:hover { background: var(--gray-50, #f9fafb); }
.bell-item.unread {
  border-left: 3px solid var(--primary, #2563eb);
  background: var(--primary-light, #eff6ff);
}
.bell-item-icon { font-size: 20px; flex-shrink: 0; margin-top: 1px; }
.bell-item-body { flex: 1; min-width: 0; }
.bell-item-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.bell-item-week {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-muted);
  background: var(--gray-100, #f3f4f6);
  padding: 1px 6px;
  border-radius: 8px;
}
.bell-item-pending {
  font-size: 10px;
  font-weight: 600;
  color: #d97706;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  padding: 1px 6px;
  border-radius: 8px;
}
.bell-item-msg { font-size: 12px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 3px; }
.bell-item-time { font-size: 11px; color: var(--text-muted); }
.bell-item-del {
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
  border-radius: 4px;
}
.bell-item:hover .bell-item-del { opacity: 1; }
.bell-item-del:hover { background: var(--gray-100, #f3f4f6); color: var(--text); }
.bell-item-del .material-symbols-outlined { font-size: 15px; }
</style>

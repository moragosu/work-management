<template>
  <div class="layout" @mousemove="onMouseMove" @mouseover="onMouseOver" @mouseout="onMouseOut" @click="tooltip.visible = false" @mouseleave="tooltip.visible = false">
    <aside class="sidebar">
      <RouterLink to="/dashboard" class="sidebar-logo">
        <div class="logo-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="5"/>
            <circle cx="12" cy="12" r="1.5" fill="white" stroke="none"/>
          </svg>
        </div>
        <div class="logo-text">
          <h1>설비혁신파트</h1>
          <span>협업 시스템</span>
        </div>
      </RouterLink>
      <nav class="sidebar-nav">
        <RouterLink to="/dashboard" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">dashboard</span>
          <span class="nav-text">대시보드</span>
        </RouterLink>
        <RouterLink to="/progress" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">assignment</span>
          <span class="nav-text">주간 진행 현황</span>
        </RouterLink>
        <RouterLink to="/admin" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">settings</span>
          <span class="nav-text">관리 도구</span>
        </RouterLink>
        <RouterLink to="/feedback" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">feedback</span>
          <span class="nav-text">피드백</span>
        </RouterLink>
        <RouterLink v-if="auth.isLeader || auth.isAdmin" to="/issue-history" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">manage_search</span>
          <span class="nav-text">이슈 히스토리</span>
        </RouterLink>
        <RouterLink v-if="auth.isLeader || auth.isAdmin" to="/export" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">summarize</span>
          <span class="nav-text">보고서 내보내기</span>
        </RouterLink>
        <RouterLink to="/help" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">help</span>
          <span class="nav-text">도움말</span>
        </RouterLink>
      </nav>
    </aside>
    <div class="main-wrap">
      <header v-if="auth.isLoggedIn" class="top-header">
        <span class="page-title">{{ pageTitle }}</span>
        <div class="header-right">
          <NotificationBell />
          <div class="header-divider"></div>
          <div class="user-info">
            <div class="user-avatar">{{ auth.user?.name?.charAt(0) }}</div>
            <span class="user-name">{{ auth.user?.name }}</span>
            <button class="logout-btn" @click="doLogout" data-tooltip="로그아웃">
              <span class="material-symbols-outlined">logout</span>
            </button>
          </div>
        </div>
      </header>
      <main class="main-content">
        <RouterView />
      </main>
    </div>
  </div>

  <!-- 전역 마우스 추적 툴팁 -->
  <Teleport to="body">
    <div v-if="tooltip.visible" class="global-tooltip" :style="tooltipStyle">
      {{ tooltip.text }}
    </div>
  </Teleport>

  <!-- 전역 이미지 라이트박스 -->
  <Teleport to="body">
    <div v-if="lightbox.visible" class="lightbox-overlay" @click="lightbox.visible = false">
      <button class="lightbox-close" @click="lightbox.visible = false">
        <span class="material-symbols-outlined">close</span>
      </button>
      <img :src="lightbox.src" class="lightbox-img" @click.stop />
    </div>
  </Teleport>
</template>

<script setup>
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'
import { reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from './stores/auth.js'
import NotificationBell from './components/NotificationBell.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const pageTitle = computed(() => route.meta?.title || '')

function doLogout() {
  auth.logout()
  router.push('/login')
}

const tooltip = reactive({ visible: false, text: '', x: 0, y: 0 })
const lightbox = reactive({ visible: false, src: '' })

function handleImgClick(e) {
  if (e.target.tagName !== 'IMG') return
  const inPreview = e.target.closest('.md-preview-inline, .dash-modal-md')
  if (!inPreview) return
  lightbox.src = e.target.src
  lightbox.visible = true
}

onMounted(() => document.addEventListener('click', handleImgClick))
onUnmounted(() => document.removeEventListener('click', handleImgClick))

const tooltipStyle = computed(() => {
  const ox = 14
  const oy = 20
  const vw = window.innerWidth
  const vh = window.innerHeight
  const estW = tooltip.text.length * 7 + 20
  const estH = 28
  const x = tooltip.x + ox + estW > vw ? tooltip.x - estW - 4 : tooltip.x + ox
  const y = tooltip.y + oy + estH > vh ? tooltip.y - estH - 8 : tooltip.y + oy
  return { left: x + 'px', top: y + 'px' }
})

function onMouseMove(e) {
  if (tooltip.visible) {
    tooltip.x = e.clientX
    tooltip.y = e.clientY
  }
}

function onMouseOver(e) {
  const el = e.target.closest('[data-tooltip]')
  if (el) {
    tooltip.text = el.getAttribute('data-tooltip')
    tooltip.x = e.clientX
    tooltip.y = e.clientY
    tooltip.visible = true
  }
}

function onMouseOut(e) {
  const el = e.target.closest('[data-tooltip]')
  if (el && !el.contains(e.relatedTarget)) {
    tooltip.visible = false
  }
}
</script>

<style scoped>
.global-tooltip {
  position: fixed;
  z-index: 9999;
  background: var(--text-primary);
  color: #fff;
  font-size: var(--fs-2xs);
  line-height: 1.4;
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  white-space: nowrap;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.22);
  animation: tooltip-in 0.1s ease;
}
@keyframes tooltip-in {
  from { opacity: 0; transform: translateY(2px); }
  to   { opacity: 1; transform: translateY(0); }
}

.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
  animation: tooltip-in 0.15s ease;
}
.lightbox-img {
  max-width: 92vw;
  max-height: 92vh;
  object-fit: contain;
  border-radius: var(--radius-sm);
  cursor: default;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5);
}
.lightbox-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: rgba(255,255,255,0.15);
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  transition: background 0.15s;
}
.lightbox-close:hover { background: rgba(255,255,255,0.28); }
</style>

<style>
.main-wrap {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: var(--topbar-h);
  background: var(--surface);
  border-bottom: 1px solid var(--outline);
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.page-title {
  font-size: var(--fs-h3);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  letter-spacing: -0.2px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-divider {
  width: 1px;
  height: 24px;
  background: var(--outline);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: #fff;
  font-size: var(--fs-sm);
  font-weight: var(--fw-bold);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-name {
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-secondary);
}
.logout-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  padding: 6px;
  border-radius: var(--radius-md);
  transition: background 0.15s, color 0.15s;
}
.logout-btn:hover { background: var(--gray-100); color: var(--text-primary); }
.logout-btn .material-symbols-outlined { font-size: var(--fs-h2); }
</style>

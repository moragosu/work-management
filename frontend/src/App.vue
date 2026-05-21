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
        <RouterLink to="/help" class="nav-item" active-class="active">
          <span class="nav-icon material-symbols-outlined">help</span>
          <span class="nav-text">도움말</span>
        </RouterLink>
      </nav>
    </aside>
    <main class="main-content">
      <RouterView />
    </main>
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
import { RouterLink, RouterView } from 'vue-router'
import { reactive, computed, onMounted, onUnmounted } from 'vue'

const tooltip = reactive({ visible: false, text: '', x: 0, y: 0 })
const lightbox = reactive({ visible: false, src: '' })

function handleImgClick(e) {
  if (e.target.tagName !== 'IMG') return
  const inPreview = e.target.closest('.md-preview-inline, .md-editor-preview')
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
  background: #1a1a2e;
  color: #fff;
  font-size: 11px;
  line-height: 1.4;
  padding: 5px 10px;
  border-radius: 5px;
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
  border-radius: 4px;
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

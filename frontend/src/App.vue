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
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { reactive, computed } from 'vue'

const tooltip = reactive({ visible: false, text: '', x: 0, y: 0 })

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
</style>

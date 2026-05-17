<template>
  <div class="layout">
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
          <span>목표 관리 시스템</span>
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
      </nav>
    </aside>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

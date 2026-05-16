<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="logo-text">
          <h1>설비혁신파트</h1>
          <span>목표 관리 시스템</span>
        </div>
      </div>
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

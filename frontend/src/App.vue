<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <h1>설비혁신파트</h1>
        <span>Objective 관리 시스템</span>
      </div>
      <nav class="sidebar-nav">
        <RouterLink to="/dashboard" class="nav-item" active-class="active">
          <span class="nav-icon">📊</span> 대시보드
        </RouterLink>
        <RouterLink to="/progress" class="nav-item" active-class="active">
          <span class="nav-icon">📋</span> 진행도 관리
        </RouterLink>
        <RouterLink to="/staff" class="nav-item" active-class="active">
          <span class="nav-icon">👥</span> 인력 관리
        </RouterLink>
        <RouterLink to="/admin" class="nav-item" active-class="active">
          <span class="nav-icon">⚙️</span> 관리 도구
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

<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="#2563eb" stroke="none"/>
        </svg>
        <span>설비혁신파트 협업 시스템</span>
      </div>
      <h2 class="auth-title">로그인</h2>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>아이디</label>
          <input v-model="username" type="text" placeholder="아이디 입력" autocomplete="username" required />
        </div>
        <div class="form-group">
          <label>비밀번호</label>
          <input v-model="password" type="password" placeholder="비밀번호 입력" autocomplete="current-password" required />
        </div>
        <div v-if="error" class="auth-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary auth-btn" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
      <p class="auth-link">계정이 없으신가요? <RouterLink to="/signup">회원가입</RouterLink></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.detail || '로그인에 실패했습니다'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--background, #f8fafc);
}
.auth-card {
  background: var(--surface, #fff);
  border: 1px solid var(--outline, #e5e7eb);
  border-radius: 12px;
  padding: 36px 40px;
  width: 360px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
}
.auth-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary, #555);
  margin-bottom: 20px;
}
.auth-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text, #111);
  margin: 0 0 24px;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary, #555);
  margin-bottom: 6px;
}
.form-group input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--outline, #e5e7eb);
  border-radius: 6px;
  font-size: 14px;
  background: var(--background, #f8fafc);
  color: var(--text, #111);
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.15s;
}
.form-group input:focus { border-color: var(--primary, #2563eb); background: #fff; }
.auth-error {
  font-size: 13px;
  color: var(--danger, #ef4444);
  margin-bottom: 12px;
}
.auth-btn {
  width: 100%;
  padding: 10px;
  font-size: 15px;
  margin-top: 4px;
}
.auth-link {
  text-align: center;
  font-size: 13px;
  color: var(--text-muted, #888);
  margin-top: 16px;
}
.auth-link a { color: var(--primary, #2563eb); text-decoration: none; font-weight: 600; }
.auth-link a:hover { text-decoration: underline; }
</style>

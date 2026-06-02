<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary)">
          <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/>
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
  background: var(--bg-main);
}
.auth-card {
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: var(--radius-lg);
  padding: 36px 40px;
  width: 360px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
}
.auth-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-secondary);
  margin-bottom: 20px;
}
.auth-title {
  font-size: var(--fs-h1);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  margin: 0 0 24px;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-secondary);
  margin-bottom: 6px;
}
.form-group input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--outline);
  border-radius: 6px;
  font-size: var(--fs-md);
  background: var(--bg-main);
  color: var(--text-primary);
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.15s;
}
.form-group input:focus { border-color: var(--primary); background: var(--surface); }
.auth-error {
  font-size: var(--fs-sm);
  color: var(--danger);
  margin-bottom: 12px;
}
.auth-btn {
  width: 100%;
  padding: 10px;
  font-size: var(--fs-base);
  margin-top: 4px;
}
.auth-link {
  text-align: center;
  font-size: var(--fs-sm);
  color: var(--text-muted);
  margin-top: 16px;
}
.auth-link a { color: var(--primary); text-decoration: none; font-weight: var(--fw-semibold); }
.auth-link a:hover { text-decoration: underline; }
</style>

<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="#2563eb" stroke="none"/>
        </svg>
        <span>설비혁신파트 협업 시스템</span>
      </div>
      <h2 class="auth-title">회원가입</h2>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>아이디 <span class="req">*</span></label>
          <input v-model="username" type="text" placeholder="로그인에 사용할 아이디" autocomplete="username" required />
        </div>
        <div class="form-group">
          <label>이름 <span class="req">*</span></label>
          <input v-model="name" type="text" placeholder="실명 (예: 홍길동)" required />
        </div>
        <div class="form-group">
          <label>비밀번호 <span class="req">*</span></label>
          <input v-model="password" type="password" placeholder="비밀번호 입력" autocomplete="new-password" required />
        </div>
        <div class="form-group">
          <label>비밀번호 확인 <span class="req">*</span></label>
          <input v-model="confirm" type="password" placeholder="비밀번호 재입력" required />
        </div>
        <div v-if="error" class="auth-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary auth-btn" :disabled="loading">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>
      </form>
      <p class="auth-link">이미 계정이 있으신가요? <RouterLink to="/login">로그인</RouterLink></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const name = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (password.value !== confirm.value) {
    error.value = '비밀번호가 일치하지 않습니다'
    return
  }
  if (password.value.length < 4) {
    error.value = '비밀번호는 4자 이상이어야 합니다'
    return
  }
  loading.value = true
  try {
    await auth.signup(username.value.trim(), name.value.trim(), password.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || '회원가입에 실패했습니다'
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
  margin-bottom: 14px;
}
.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary, #555);
  margin-bottom: 5px;
}
.req { color: var(--danger, #ef4444); }
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

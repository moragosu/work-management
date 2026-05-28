<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="#2563eb" stroke="none"/>
        </svg>
        <span>설비혁신파트 협업 시스템</span>
      </div>
      <h2 class="auth-title">비밀번호 변경</h2>
      <p class="auth-desc">임시 비밀번호로 로그인되었습니다.<br>새 비밀번호를 설정해주세요.</p>
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>현재 비밀번호 (임시 비밀번호)</label>
          <input v-model="currentPassword" type="password" placeholder="임시 비밀번호 입력" required />
        </div>
        <div class="form-group">
          <label>새 비밀번호</label>
          <input v-model="newPassword" type="password" placeholder="6자 이상" required />
        </div>
        <div class="form-group">
          <label>새 비밀번호 확인</label>
          <input v-model="confirmPassword" type="password" placeholder="새 비밀번호 재입력" required />
        </div>
        <div v-if="error" class="auth-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary auth-btn" :disabled="loading">
          {{ loading ? '변경 중...' : '비밀번호 변경' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const auth = useAuthStore()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (newPassword.value.length < 6) {
    error.value = '새 비밀번호는 6자 이상이어야 합니다.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }
  loading.value = true
  try {
    await axios.put('/api/auth/password', {
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    // 로컬 스토리지의 force_password_change 플래그 해제
    const user = JSON.parse(localStorage.getItem('authUser') || 'null')
    if (user) {
      user.force_password_change = false
      localStorage.setItem('authUser', JSON.stringify(user))
      auth.user.force_password_change = false
    }
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || '비밀번호 변경에 실패했습니다.'
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
  margin: 0 0 8px;
}
.auth-desc {
  font-size: 13px;
  color: var(--text-muted, #888);
  margin: 0 0 24px;
  line-height: 1.6;
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
</style>

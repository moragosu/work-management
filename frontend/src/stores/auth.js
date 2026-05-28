import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('authUser') || 'null'))
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isLeader = computed(() => ['leader', 'admin'].includes(user.value?.role))

  function _setAuth(t, u) {
    token.value = t
    user.value = u
    localStorage.setItem('token', t)
    localStorage.setItem('authUser', JSON.stringify(u))
    axios.defaults.headers.common['Authorization'] = `Bearer ${t}`
  }

  function _clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('authUser')
    delete axios.defaults.headers.common['Authorization']
  }

  function initAxiosAuth() {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  async function login(username, password) {
    const form = new FormData()
    form.append('username', username)
    form.append('password', password)
    const { data } = await axios.post('/api/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    _setAuth(data.access_token, data.user)
    return data.user
  }

  async function signup(username, name, password) {
    const { data } = await axios.post('/api/auth/signup', { username, name, password })
    _setAuth(data.access_token, data.user)
    return data.user
  }

  async function fetchMe() {
    try {
      const { data } = await axios.get('/api/auth/me')
      user.value = data
      localStorage.setItem('authUser', JSON.stringify(data))
    } catch {
      _clearAuth()
    }
  }

  function logout() {
    _clearAuth()
  }

  return { user, token, isLoggedIn, isAdmin, isLeader, login, signup, logout, fetchMe, initAxiosAuth }
})

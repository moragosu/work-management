import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import './style.css'
import 'md-editor-v3/lib/style.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 인라인 편집 자동 포커스 디렉티브
app.directive('autofocus', { mounted: el => el.focus() })

import { useAuthStore } from './stores/auth.js'
const authStore = useAuthStore()
authStore.initAxiosAuth()

app.mount('#app')

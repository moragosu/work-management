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

import { useAuthStore } from './stores/auth.js'
const authStore = useAuthStore()
authStore.initAxiosAuth()

app.mount('#app')

<template>
  <div class="go-redirect">
    <span class="material-symbols-outlined spin">progress_activity</span>
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const message = ref('이동 중...')

onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/go/${route.params.id}`)
    router.replace(data.url)
  } catch {
    message.value = '링크를 찾을 수 없습니다.'
  }
})
</script>

<style scoped>
.go-redirect {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  gap: 16px;
  color: var(--text-muted);
  font-size: 14px;
}
.spin {
  font-size: 36px;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>

import { ref } from 'vue'

export function useToast(duration = 2000) {
  const toastMsg = ref('')

  function showToast(msg) {
    toastMsg.value = msg
    setTimeout(() => { toastMsg.value = '' }, duration)
  }

  function toastError(e, fallback = '처리 실패') {
    showToast(e?.response?.data?.detail || fallback)
  }

  return { toastMsg, showToast, toastError }
}

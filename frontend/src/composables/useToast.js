import { ref } from 'vue'

export function useToast(duration = 2000) {
  const toastMsg = ref('')

  function showToast(msg) {
    toastMsg.value = msg
    setTimeout(() => { toastMsg.value = '' }, duration)
  }

  return { toastMsg, showToast }
}

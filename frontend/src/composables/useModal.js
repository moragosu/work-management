import { ref } from 'vue'

export function useModal() {
  const show = ref(false)
  const open = () => { show.value = true }
  const close = () => { show.value = false }
  return { show, open, close }
}

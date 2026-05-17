import { ref } from 'vue'
import axios from 'axios'

export function useImageUpload(onError) {
  const uploading = ref(false)

  async function handlePaste(event, targetArray) {
    const items = Array.from(event.clipboardData?.items || [])
    const imageItems = items.filter(item => item.type.startsWith('image/'))
    if (!imageItems.length) return
    event.preventDefault()
    uploading.value = true
    try {
      for (const item of imageItems) {
        const file = item.getAsFile()
        if (!file) continue
        const formData = new FormData()
        formData.append('file', file, `paste_${Date.now()}.png`)
        const { data } = await axios.post('/api/upload', formData)
        targetArray.push(data.url)
      }
    } catch {
      onError?.('이미지 업로드 실패')
    } finally {
      uploading.value = false
    }
  }

  return { uploading, handlePaste }
}

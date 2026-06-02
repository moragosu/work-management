<template>
  <div
    ref="editorRef"
    class="rich-textarea"
    contenteditable="true"
    :style="{ minHeight: `${rows * 1.6}em` }"
    :data-placeholder="placeholder"
    @input="onInput"
    @paste="onPaste"
  />
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  rows: { type: Number, default: 3 },
})

const emit = defineEmits(['update:modelValue'])
const editorRef = ref(null)
let lastEmitted = ''

watch(() => props.modelValue, (val) => {
  if (!editorRef.value || val === lastEmitted) return
  if (editorRef.value.innerHTML !== val) {
    editorRef.value.innerHTML = val
  }
})

onMounted(() => {
  if (editorRef.value && props.modelValue) {
    editorRef.value.innerHTML = props.modelValue
  }
})

function onInput() {
  const html = editorRef.value.innerHTML
  lastEmitted = html
  emit('update:modelValue', html)
}

async function onPaste(event) {
  const items = Array.from(event.clipboardData?.items || [])
  const imageItem = items.find(item => item.type.startsWith('image/'))
  if (!imageItem) return // 텍스트 붙여넣기는 브라우저 기본 동작

  event.preventDefault()
  const file = imageItem.getAsFile()
  if (!file) return

  const formData = new FormData()
  formData.append('file', file, `paste_${Date.now()}.png`)
  try {
    const { data } = await axios.post('/api/upload', formData)
    insertImageAtCursor(data.url)
    const html = editorRef.value.innerHTML
    lastEmitted = html
    emit('update:modelValue', html)
  } catch {
    // 업로드 실패 시 무시
  }
}

function insertImageAtCursor(url) {
  const img = document.createElement('img')
  img.src = url
  img.className = 'rich-inline-img'

  const sel = window.getSelection()
  if (sel?.rangeCount) {
    const range = sel.getRangeAt(0)
    range.deleteContents()
    range.insertNode(img)
    const newRange = document.createRange()
    newRange.setStartAfter(img)
    newRange.collapse(true)
    sel.removeAllRanges()
    sel.addRange(newRange)
  } else {
    editorRef.value.appendChild(img)
  }
}
</script>

<style scoped>
.rich-textarea {
  display: block;
  width: 100%;
  padding: 8px 12px;
  font-size: var(--fs-md);
  line-height: 1.6;
  color: var(--text-primary);
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: var(--radius-sm);
  outline: none;
  overflow-y: auto;
  word-break: break-word;
  font-family: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
  cursor: text;
}
.rich-textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
}
.rich-textarea:empty::before {
  content: attr(data-placeholder);
  color: var(--text-muted);
  pointer-events: none;
  display: block;
}
</style>

<style>
/* non-scoped: v-html로 렌더된 저장 콘텐츠에도 적용 */
.rich-inline-img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-sm);
  margin: 6px 0;
  display: block;
  cursor: zoom-in;
}
.rich-content { line-height: 1.6; font-size: var(--fs-md); word-break: break-word; }
.rich-content img { max-width: 100%; height: auto; border-radius: var(--radius-sm); margin: 6px 0; display: block; }
</style>

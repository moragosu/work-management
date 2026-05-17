<template>
  <div class="md-editor-wrap">
    <MdEditor
      v-model="content"
      :onUploadImg="handleUpload"
      :toolbars="toolbars"
      :style="{ height: editorHeight }"
      :showCodeRowNumber="false"
      :sanitize="sanitize"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MdEditor } from 'md-editor-v3'
import axios from 'axios'

const props = defineProps({
  modelValue: { type: String, default: '' },
  height: { type: String, default: '200px' },
})
const emit = defineEmits(['update:modelValue'])

const content = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const editorHeight = computed(() => props.height)

const toolbars = [
  'bold', 'italic', 'strikethrough', '-',
  'title', 'quote', 'unorderedList', 'orderedList', 'task', '-',
  'code', 'codeRow', 'link', 'image', 'table', '-',
  'revoke', 'next', '-',
  'preview',
]

function sanitize(html) {
  return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
}

async function handleUpload(files, callback) {
  try {
    const urls = await Promise.all(
      files.map(async (file) => {
        const form = new FormData()
        form.append('file', file)
        const { data } = await axios.post('/api/upload', form)
        return data.url
      })
    )
    callback(urls)
  } catch {
    callback([])
  }
}
</script>

<style scoped>
.md-editor-wrap {
  border-radius: var(--radius-sm);
  overflow: hidden;
}
</style>

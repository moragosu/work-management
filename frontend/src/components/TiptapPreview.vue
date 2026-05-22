<template>
  <div class="tiptap-preview" v-html="renderedHtml"></div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  modelValue: { type: String, default: '' },
})

// alt 텍스트가 "300px" 형태면 width 스타일 적용
marked.use({
  renderer: {
    image(href, title, text) {
      const widthMatch = text?.match(/^(\d+)px$/)
      const style = widthMatch
        ? `width:${widthMatch[1]}px;max-width:100%;height:auto;`
        : 'max-width:100%;height:auto;'
      const titleAttr = title ? ` title="${title}"` : ''
      const altAttr = widthMatch ? '' : ` alt="${text || ''}"`
      return `<img src="${href}"${altAttr}${titleAttr} style="${style}" loading="lazy">`
    },
  },
})
marked.setOptions({ breaks: true, gfm: true })

const renderedHtml = computed(() => {
  if (!props.modelValue?.trim()) return ''
  let html = marked.parse(props.modelValue)
  // XSS: script 태그·이벤트 핸들러 제거
  html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
  html = html.replace(/\son\w+="[^"]*"/gi, '')
  return html
})
</script>

<style scoped>
.tiptap-preview {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary, #111);
  word-break: break-word;
}
:deep(p) { margin: 0 0 6px; }
:deep(p:last-child) { margin-bottom: 0; }
:deep(h1) { font-size: 1.4em; font-weight: 700; margin: 8px 0 4px; }
:deep(h2) { font-size: 1.2em; font-weight: 700; margin: 8px 0 4px; }
:deep(h3) { font-size: 1.05em; font-weight: 700; margin: 6px 0 3px; }
:deep(ul), :deep(ol) { padding-left: 20px; margin: 4px 0; }
:deep(li) { margin: 2px 0; }
:deep(blockquote) {
  border-left: 3px solid var(--primary, #2563eb);
  margin: 6px 0; padding: 4px 12px;
  color: var(--text-secondary, #555);
  background: var(--gray-50, #f9fafb);
}
:deep(code) {
  background: var(--gray-100, #f3f4f6);
  padding: 1px 4px; border-radius: 3px;
  font-family: monospace; font-size: 13px;
}
:deep(pre) {
  background: #1e293b; color: #e2e8f0;
  border-radius: 6px; padding: 10px 14px;
  margin: 6px 0; overflow-x: auto;
}
:deep(pre code) { background: transparent; color: inherit; padding: 0; }
:deep(img) { max-width: 100%; height: auto; border-radius: 4px; }
:deep(a) { color: var(--primary, #2563eb); text-decoration: underline; }
:deep(hr) { border: none; border-top: 1px solid var(--outline, #e5e7eb); margin: 8px 0; }
:deep(s) { text-decoration: line-through; }
:deep(table) { border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 13px; }
:deep(th), :deep(td) { border: 1px solid var(--outline, #e5e7eb); padding: 5px 10px; }
:deep(th) { background: var(--gray-50, #f9fafb); font-weight: 600; }
:deep(input[type="checkbox"]) { margin-right: 4px; }
</style>

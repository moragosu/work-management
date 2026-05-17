<template>
  <div class="md-editor-wrap">
    <MdEditor
      v-model="content"
      language="en-US"
      :onUploadImg="handleUpload"
      :toolbars="toolbars"
      :style="{ height: editorHeight }"
      :showCodeRowNumber="false"
      :sanitize="sanitize"
    >
      <template #defToolbars>
        <NormalToolbar title="마크다운 도움말" @onClick="showHelp = !showHelp">
          <template #trigger>
            <span class="help-trigger" :class="{ active: showHelp }">?</span>
          </template>
        </NormalToolbar>
      </template>
    </MdEditor>

    <div v-if="showHelp" class="help-panel">
      <div class="help-grid">
        <div class="help-item" v-for="item in helpItems" :key="item.syntax">
          <code>{{ item.syntax }}</code>
          <span>{{ item.label }}</span>
        </div>
      </div>
      <p class="help-tip">툴바 버튼으로도 서식을 적용할 수 있고, 이미지는 클립보드에서 바로 붙여넣기(Ctrl+V)가 됩니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MdEditor, NormalToolbar } from 'md-editor-v3'
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
const showHelp = ref(false)

const toolbars = [
  'bold', 'italic', 'strikethrough', '-',
  'title', 'quote', 'unorderedList', 'orderedList', 'task', '-',
  'code', 'codeRow', 'link', 'image', 'table', '-',
  'revoke', 'next', '-',
  'preview', 0,
]

const helpItems = [
  { syntax: '**굵게**',       label: '굵은 글씨' },
  { syntax: '*기울기*',       label: '기울임' },
  { syntax: '~~취소선~~',     label: '취소선' },
  { syntax: '# 제목',         label: '제목 (# 개수로 크기 조절)' },
  { syntax: '- 항목',         label: '글머리 목록' },
  { syntax: '1. 항목',        label: '번호 목록' },
  { syntax: '- [ ] 항목',     label: '체크박스 (- [x] 는 완료)' },
  { syntax: '`코드`',         label: '인라인 코드' },
  { syntax: '> 인용',         label: '인용문' },
  { syntax: '[텍스트](URL)',   label: '링크' },
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

.help-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary, #888);
  border: 1.5px solid currentColor;
  line-height: 1;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}

.help-trigger.active,
.help-trigger:hover {
  color: var(--color-primary, #4f8ef7);
  border-color: var(--color-primary, #4f8ef7);
}

.help-panel {
  background: var(--color-bg-secondary, #f8f9fa);
  border: 1px solid var(--color-border, #e0e0e0);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  padding: 12px 16px;
}

.help-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 6px 20px;
  margin-bottom: 10px;
}

.help-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-size: 13px;
}

.help-item code {
  font-family: monospace;
  font-size: 12px;
  background: var(--color-bg-code, #eef0f3);
  padding: 1px 5px;
  border-radius: 3px;
  white-space: nowrap;
  flex-shrink: 0;
  color: var(--color-text-primary, #333);
}

.help-item span {
  color: var(--color-text-secondary, #666);
  font-size: 12px;
}

.help-tip {
  font-size: 12px;
  color: var(--color-text-secondary, #888);
  margin: 0;
  padding-top: 8px;
  border-top: 1px solid var(--color-border, #e8e8e8);
}
</style>

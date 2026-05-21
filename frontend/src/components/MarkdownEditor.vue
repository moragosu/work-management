<template>
  <div class="md-editor-wrap" @paste.capture="onPaste">
    <MdEditor
      v-model="content"
      language="en-US"
      :onUploadImg="handleUpload"
      :toolbars="toolbars"
      :style="{ height: editorHeight }"
      :showCodeRowNumber="false"
      :sanitize="sanitize"
      :noImgZoomIn="true"
    >
      <template #defToolbars>
        <NormalToolbar title="마크다운 도움말" @onClick="showHelp = !showHelp">
          <template #trigger>
            <span class="help-trigger" :class="{ active: showHelp }">?</span>
          </template>
        </NormalToolbar>
      </template>
    </MdEditor>

    <!-- 이미지 사이즈 피커 -->
    <div v-if="pending.visible" class="img-size-picker">
      <img :src="pending.url" class="img-size-thumb" />
      <div class="img-size-controls">
        <span class="img-size-label">너비 (px)</span>
        <input
          v-model="pending.width"
          ref="widthInputRef"
          type="number"
          min="50"
          max="2000"
          placeholder="원본"
          class="img-size-input"
          @keyup.enter="insertImage"
        />
        <button class="btn btn-primary btn-xs" @click="insertImage">삽입</button>
        <button class="btn btn-ghost btn-xs" @click="cancelInsert">취소</button>
      </div>
    </div>

    <div v-if="uploadError" class="upload-error-msg">{{ uploadError }}</div>

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
import { ref, computed, reactive, nextTick } from 'vue'
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
const widthInputRef = ref(null)

// ── 이미지 사이즈 피커 ──
const pending = reactive({ visible: false, url: '', width: '' })

function showPicker(url) {
  pending.url = url
  pending.width = ''
  pending.visible = true
  nextTick(() => widthInputRef.value?.focus())
}

function insertImage() {
  const w = parseInt(pending.width)
  const url = pending.url
  const markdown = w > 0
    ? `<img src="${url}" width="${w}" style="max-width:100%;height:auto">`
    : `![image](${url})`
  content.value = (content.value ? content.value + '\n' : '') + markdown
  pending.visible = false
}

function cancelInsert() {
  pending.visible = false
}

// ── 업로드 에러 피드백 ──
const uploadError = ref('')
let uploadErrorTimer = null
function showUploadError(msg) {
  uploadError.value = msg
  clearTimeout(uploadErrorTimer)
  uploadErrorTimer = setTimeout(() => { uploadError.value = '' }, 4000)
}

// ── paste 이벤트 — 모든 이미지 붙여넣기를 직접 처리 ──
function onPaste(e) {
  const items = e.clipboardData?.items
  if (!items) return
  // files 우선, 없으면 items에서 추출
  let imageFiles = Array.from(e.clipboardData.files || []).filter(f => f.type.startsWith('image/'))
  if (imageFiles.length === 0) {
    imageFiles = Array.from(items)
      .filter(i => i.type.startsWith('image/'))
      .map(i => i.getAsFile())
      .filter(Boolean)
  }
  if (imageFiles.length === 0) return
  // 라이브러리가 paste를 가로채지 못하도록 차단
  e.stopPropagation()
  e.preventDefault()
  handleUpload(imageFiles, () => {})
}

// ── 업로드 핸들러 ──
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
    // 라이브러리 auto-insert 막고 사이즈 피커로 대체
    callback([])
    if (urls.length > 0) showPicker(urls[0])
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '알 수 없는 오류'
    showUploadError(`이미지 업로드 실패: ${msg}`)
    callback([])
  }
}

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
</script>

<style scoped>
.md-editor-wrap {
  border-radius: var(--radius-sm);
  overflow: hidden;
}

/* 이미지 사이즈 피커 */
.img-size-picker {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: #f0f4ff;
  border: 1px solid var(--primary-light);
  border-top: none;
  flex-wrap: wrap;
}
.img-size-thumb {
  height: 48px;
  max-width: 80px;
  object-fit: contain;
  border-radius: 4px;
  border: 1px solid var(--outline);
  background: #fff;
}
.img-size-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.img-size-label {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}
.img-size-input {
  width: 80px;
  padding: 4px 8px;
  border: 1px solid var(--outline);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: #fff;
}
.img-size-input:focus {
  outline: none;
  border-color: var(--primary);
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
.upload-error-msg {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-top: none;
  color: #b91c1c;
  font-size: 12px;
  padding: 6px 12px;
}
.help-tip {
  font-size: 12px;
  color: var(--color-text-secondary, #888);
  margin: 0;
  padding-top: 8px;
  border-top: 1px solid var(--color-border, #e8e8e8);
}
</style>

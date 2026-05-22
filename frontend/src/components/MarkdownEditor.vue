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
        <NormalToolbar title="전체화면 편집" @onClick="openExpand">
          <template #trigger>
            <span class="material-symbols-outlined expand-trigger">open_in_full</span>
          </template>
        </NormalToolbar>
      </template>
    </MdEditor>

    <div v-if="uploadError" class="upload-error-msg">{{ uploadError }}</div>

    <!-- 이미지 사이즈 피커 (메인 에디터) -->
    <div v-if="pendingImage.url && !expandOpen" class="img-picker">
      <span class="img-picker-label">이미지 삽입</span>
      <button class="img-size-btn" @click="insertImage('origin')">원본</button>
      <button class="img-size-btn" @click="insertImage('S')">S <span class="img-size-hint">300px</span></button>
      <button class="img-size-btn" @click="insertImage('M')">M <span class="img-size-hint">500px</span></button>
      <button class="img-size-btn" @click="insertImage('L')">L <span class="img-size-hint">800px</span></button>
      <label class="img-border-toggle">
        <input type="checkbox" v-model="pendingImage.border" />
        Border
      </label>
      <button class="img-cancel-btn" @click="pendingImage.url = null">취소</button>
    </div>

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

  <!-- 전체화면 편집 모달 -->
  <Teleport to="body">
    <div v-if="expandOpen" class="expand-overlay" @paste.capture="onExpandPaste">
      <div class="expand-modal">
        <div class="expand-header">
          <span class="expand-title">전체화면 편집</span>
          <div class="expand-header-actions">
            <button class="btn btn-ghost btn-sm" @click="cancelExpand">취소</button>
            <button class="btn btn-primary btn-sm" @click="applyExpand">적용</button>
            <button class="expand-close-btn" @click="cancelExpand">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>
        <div class="expand-body">
          <MdEditor
            v-model="expandContent"
            language="en-US"
            :onUploadImg="handleExpandUpload"
            :toolbars="expandToolbars"
            :style="{ height: '100%' }"
            :showCodeRowNumber="false"
            :sanitize="sanitize"
            :noImgZoomIn="true"
          >
            <template #defToolbars>
              <NormalToolbar title="마크다운 도움말" @onClick="showExpandHelp = !showExpandHelp">
                <template #trigger>
                  <span class="help-trigger" :class="{ active: showExpandHelp }">?</span>
                </template>
              </NormalToolbar>
            </template>
          </MdEditor>
        </div>

        <!-- 이미지 사이즈 피커 (확장 모달) -->
        <div v-if="pendingImage.url && expandOpen" class="img-picker expand-img-picker">
          <span class="img-picker-label">이미지 삽입</span>
          <button class="img-size-btn" @click="insertExpandImage('origin')">원본</button>
          <button class="img-size-btn" @click="insertExpandImage('S')">S <span class="img-size-hint">300px</span></button>
          <button class="img-size-btn" @click="insertExpandImage('M')">M <span class="img-size-hint">500px</span></button>
          <button class="img-size-btn" @click="insertExpandImage('L')">L <span class="img-size-hint">800px</span></button>
          <label class="img-border-toggle">
            <input type="checkbox" v-model="pendingImage.border" />
            Border
          </label>
          <button class="img-cancel-btn" @click="pendingImage.url = null">취소</button>
        </div>

        <div v-if="expandUploadError" class="upload-error-msg">{{ expandUploadError }}</div>

        <div v-if="showExpandHelp" class="help-panel expand-help-panel">
          <div class="help-grid">
            <div class="help-item" v-for="item in helpItems" :key="item.syntax">
              <code>{{ item.syntax }}</code>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>

        <div class="expand-footer">
          <button class="btn btn-ghost btn-sm" @click="cancelExpand">취소</button>
          <button class="btn btn-primary btn-sm" @click="applyExpand">적용</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { MdEditor, NormalToolbar } from 'md-editor-v3'
import axios from 'axios'

const props = defineProps({
  modelValue: { type: String, default: '' },
  height: { type: String, default: '200px' },
})
const emit = defineEmits(['update:modelValue', 'image-uploaded'])

const content = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const editorHeight = computed(() => props.height)
const showHelp = ref(false)

// ── 이미지 피커 상태 ──
const pendingImage = reactive({ url: null, border: false })

function buildImageMarkdown(url, size, border) {
  if (size === 'origin' && !border) return `![image](${url})`
  const w = size === 'S' ? 300 : size === 'M' ? 500 : size === 'L' ? 800 : null
  const styleBase = 'max-width:100%;height:auto'
  const style = border
    ? `border:1px solid #ddd;border-radius:4px;${styleBase}`
    : styleBase
  return w
    ? `<img src="${url}" width="${w}" style="${style}">`
    : `<img src="${url}" style="${style}">`
}

function insertImage(size) {
  if (!pendingImage.url) return
  const md = buildImageMarkdown(pendingImage.url, size, pendingImage.border)
  content.value = (content.value ? content.value + '\n' : '') + md
  pendingImage.url = null
  pendingImage.border = false
}

// ── 업로드 에러 피드백 ──
const uploadError = ref('')
let uploadErrorTimer = null
function showUploadError(msg) {
  uploadError.value = msg
  clearTimeout(uploadErrorTimer)
  uploadErrorTimer = setTimeout(() => { uploadError.value = '' }, 4000)
}

// ── paste 이벤트 — 메인 에디터 ──
function onPaste(e) {
  const files = extractImageFiles(e)
  if (!files.length) return
  e.stopPropagation()
  e.preventDefault()
  handleUpload(files, () => {})
}

function extractImageFiles(e) {
  let files = Array.from(e.clipboardData?.files || []).filter(f => f.type.startsWith('image/'))
  if (!files.length) {
    files = Array.from(e.clipboardData?.items || [])
      .filter(i => i.type.startsWith('image/'))
      .map(i => i.getAsFile())
      .filter(Boolean)
  }
  return files
}

// ── 업로드 핸들러 (메인) ──
async function handleUpload(files, callback) {
  try {
    const urls = await uploadFiles(files)
    callback([])
    urls.forEach(u => emit('image-uploaded', u))
    if (urls.length > 0) {
      pendingImage.url = urls[0]
      pendingImage.border = false
    }
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '알 수 없는 오류'
    showUploadError(`이미지 업로드 실패: ${msg}`)
    callback([])
  }
}

// ── 전체화면 편집 ──
const expandOpen = ref(false)
const expandContent = ref('')
const showExpandHelp = ref(false)
const expandUploadError = ref('')
let expandUploadErrorTimer = null

function openExpand() {
  expandContent.value = content.value
  expandOpen.value = true
}

function cancelExpand() {
  expandOpen.value = false
  pendingImage.url = null
  pendingImage.border = false
}

function applyExpand() {
  content.value = expandContent.value
  expandOpen.value = false
  pendingImage.url = null
  pendingImage.border = false
}

function insertExpandImage(size) {
  if (!pendingImage.url) return
  const md = buildImageMarkdown(pendingImage.url, size, pendingImage.border)
  expandContent.value = (expandContent.value ? expandContent.value + '\n' : '') + md
  pendingImage.url = null
  pendingImage.border = false
}

function showExpandUploadError(msg) {
  expandUploadError.value = msg
  clearTimeout(expandUploadErrorTimer)
  expandUploadErrorTimer = setTimeout(() => { expandUploadError.value = '' }, 4000)
}

function onExpandPaste(e) {
  const files = extractImageFiles(e)
  if (!files.length) return
  e.stopPropagation()
  e.preventDefault()
  handleExpandUpload(files, () => {})
}

async function handleExpandUpload(files, callback) {
  try {
    const urls = await uploadFiles(files)
    callback([])
    urls.forEach(u => emit('image-uploaded', u))
    if (urls.length > 0) {
      pendingImage.url = urls[0]
      pendingImage.border = false
    }
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '알 수 없는 오류'
    showExpandUploadError(`이미지 업로드 실패: ${msg}`)
    callback([])
  }
}

async function uploadFiles(files) {
  return Promise.all(
    files.map(async (file) => {
      const form = new FormData()
      form.append('file', file)
      const { data } = await axios.post('/api/upload', form)
      return data.url
    })
  )
}

const toolbars = [
  'bold', 'italic', 'strikethrough', '-',
  'title', 'quote', 'unorderedList', 'orderedList', 'task', '-',
  'code', 'codeRow', 'link', 'image', 'table', '-',
  'revoke', 'next', '-',
  'preview', 0, 1,
]

const expandToolbars = [
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

.expand-trigger {
  font-size: 16px;
  color: var(--color-text-secondary, #888);
  cursor: pointer;
  vertical-align: middle;
  transition: color 0.15s;
}
.expand-trigger:hover {
  color: var(--color-primary, #4f8ef7);
}

/* 이미지 피커 */
.img-picker {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f0f6ff;
  border: 1px solid #c7deff;
  border-top: none;
  flex-wrap: wrap;
}
.expand-img-picker {
  border: none;
  border-top: 1px solid #c7deff;
  border-bottom: 1px solid #c7deff;
}
.img-picker-label {
  font-size: 12px;
  color: var(--color-text-secondary, #666);
  margin-right: 4px;
  flex-shrink: 0;
}
.img-size-btn {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #a0c4ff;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}
.img-size-btn:hover {
  background: #dbeafe;
  border-color: #2563eb;
}
.img-size-hint {
  font-size: 10px;
  font-weight: 400;
  color: #60a5fa;
}
.img-border-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  margin-left: 4px;
}
.img-cancel-btn {
  margin-left: auto;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  background: transparent;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
}
.img-cancel-btn:hover { background: #f3f4f6; }

.help-panel {
  background: var(--color-bg-secondary, #f8f9fa);
  border: 1px solid var(--color-border, #e0e0e0);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  padding: 12px 16px;
}
.expand-help-panel {
  border-radius: 0;
  border-left: none;
  border-right: none;
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

/* 전체화면 편집 모달 */
.expand-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.expand-modal {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 960px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.22);
  overflow: hidden;
  animation: expand-in 0.15s ease;
}
@keyframes expand-in {
  from { opacity: 0; transform: scale(0.97); }
  to   { opacity: 1; transform: scale(1); }
}
.expand-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--outline, #e5e7eb);
  flex-shrink: 0;
}
.expand-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #111);
}
.expand-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.expand-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #6b7280;
  transition: background 0.12s;
}
.expand-close-btn:hover { background: #f3f4f6; }
.expand-close-btn .material-symbols-outlined { font-size: 18px; }

.expand-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.expand-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--outline, #e5e7eb);
  flex-shrink: 0;
}
</style>

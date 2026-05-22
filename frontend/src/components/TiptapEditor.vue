<template>
  <div class="tiptap-wrap" :style="{ minHeight: height }">
    <!-- 툴바 -->
    <div class="tiptap-toolbar" v-if="editor">
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('bold') }" @click="editor.chain().focus().toggleBold().run()" title="굵게 (Ctrl+B)">
          <span class="material-symbols-outlined">format_bold</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('italic') }" @click="editor.chain().focus().toggleItalic().run()" title="기울임 (Ctrl+I)">
          <span class="material-symbols-outlined">format_italic</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('strike') }" @click="editor.chain().focus().toggleStrike().run()" title="취소선">
          <span class="material-symbols-outlined">strikethrough_s</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('code') }" @click="editor.chain().focus().toggleCode().run()" title="인라인 코드">
          <span class="material-symbols-outlined">code</span>
        </button>
      </div>
      <div class="toolbar-sep"></div>
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 1 }) }" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" title="제목 1">H1</button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 2 }) }" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" title="제목 2">H2</button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 3 }) }" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" title="제목 3">H3</button>
      </div>
      <div class="toolbar-sep"></div>
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('bulletList') }" @click="editor.chain().focus().toggleBulletList().run()" title="글머리 목록">
          <span class="material-symbols-outlined">format_list_bulleted</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('orderedList') }" @click="editor.chain().focus().toggleOrderedList().run()" title="번호 목록">
          <span class="material-symbols-outlined">format_list_numbered</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('taskList') }" @click="editor.chain().focus().toggleTaskList().run()" title="체크박스 목록">
          <span class="material-symbols-outlined">checklist</span>
        </button>
      </div>
      <div class="toolbar-sep"></div>
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('blockquote') }" @click="editor.chain().focus().toggleBlockquote().run()" title="인용문">
          <span class="material-symbols-outlined">format_quote</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('codeBlock') }" @click="editor.chain().focus().toggleCodeBlock().run()" title="코드 블록">
          <span class="material-symbols-outlined">data_object</span>
        </button>
        <button type="button" class="tb-btn" @click="insertTable" title="표 삽입">
          <span class="material-symbols-outlined">table</span>
        </button>
        <button type="button" class="tb-btn" @click="setLink" title="링크 삽입">
          <span class="material-symbols-outlined">link</span>
        </button>
        <label class="tb-btn" title="이미지 업로드" style="cursor:pointer">
          <span class="material-symbols-outlined">image</span>
          <input type="file" accept="image/*" style="display:none" @change="onFileSelect" />
        </label>
      </div>
      <div class="toolbar-sep"></div>
      <div class="toolbar-group">
        <button type="button" class="tb-btn" @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()" title="실행 취소">
          <span class="material-symbols-outlined">undo</span>
        </button>
        <button type="button" class="tb-btn" @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()" title="다시 실행">
          <span class="material-symbols-outlined">redo</span>
        </button>
      </div>
    </div>

    <!-- 에디터 본문 -->
    <editor-content :editor="editor" class="tiptap-body" />

    <!-- 업로드 에러 -->
    <div v-if="uploadError" class="tiptap-error">{{ uploadError }}</div>

    <!-- 표 컨텍스트 툴바 -->
    <div v-if="editor && editor.isActive('table')" class="table-toolbar">
      <button type="button" class="tb-sm" @click="editor.chain().focus().addColumnBefore().run()">← 열 추가</button>
      <button type="button" class="tb-sm" @click="editor.chain().focus().addColumnAfter().run()">열 추가 →</button>
      <button type="button" class="tb-sm tb-danger" @click="editor.chain().focus().deleteColumn().run()">열 삭제</button>
      <span class="tb-div">|</span>
      <button type="button" class="tb-sm" @click="editor.chain().focus().addRowBefore().run()">↑ 행 추가</button>
      <button type="button" class="tb-sm" @click="editor.chain().focus().addRowAfter().run()">행 추가 ↓</button>
      <button type="button" class="tb-sm tb-danger" @click="editor.chain().focus().deleteRow().run()">행 삭제</button>
      <span class="tb-div">|</span>
      <button type="button" class="tb-sm tb-danger" @click="editor.chain().focus().deleteTable().run()">표 삭제</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue'
import { useEditor, EditorContent, VueNodeViewRenderer } from '@tiptap/vue-3'
import ImageNodeView from './ImageNodeView.vue'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'

// NodeView로 렌더링 (이미지 바로 아래 사이즈 바 포함)
const CustomImage = Image.extend({
  addNodeView() {
    return VueNodeViewRenderer(ImageNodeView)
  },
})
import Link from '@tiptap/extension-link'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table, TableRow, TableCell, TableHeader } from '@tiptap/extension-table'
import Placeholder from '@tiptap/extension-placeholder'
import { Markdown } from 'tiptap-markdown'
import axios from 'axios'

const props = defineProps({
  modelValue: { type: String, default: '' },
  height:     { type: String, default: '160px' },
  placeholder: { type: String, default: '내용을 입력하세요...' },
})
const emit = defineEmits(['update:modelValue', 'image-uploaded'])

// ── 업로드된 URL 추적 (언마운트 시 미삽입 이미지 정리) ──
const localUploads = ref([])
let isUnmounted = false

onUnmounted(() => {
  isUnmounted = true
  const currentContent = editor.value?.storage?.markdown?.getMarkdown?.() ?? props.modelValue ?? ''
  localUploads.value.filter(u => !currentContent.includes(u)).forEach(u => {
    axios.delete(`/api/upload/${u.split('/').pop()}`).catch(() => {})
  })
})

// ── 업로드 에러 ──
const uploadError = ref('')
let uploadErrorTimer = null
function showUploadError(msg) {
  uploadError.value = msg
  clearTimeout(uploadErrorTimer)
  uploadErrorTimer = setTimeout(() => { uploadError.value = '' }, 4000)
}

// ── 이미지 업로드 ──
async function uploadAndInsert(file) {
  try {
    const form = new FormData()
    form.append('file', file)
    const { data } = await axios.post('/api/upload', form)
    const url = data.url
    if (isUnmounted) {
      axios.delete(`/api/upload/${url.split('/').pop()}`).catch(() => {})
      return
    }
    emit('image-uploaded', url)
    localUploads.value.push(url)
    editor.value?.chain().focus().setImage({ src: url, alt: '' }).run()
    await nextTick()
    const pos = editor.value?.state.selection.from - 1
    if (pos >= 0) editor.value?.commands.setNodeSelection(pos)
  } catch (e) {
    if (!isUnmounted) {
      showUploadError(`이미지 업로드 실패: ${e?.response?.data?.detail || e?.message || '오류'}`)
    }
  }
}

function onFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) uploadAndInsert(file)
  e.target.value = ''
}

// ── Tiptap 에디터 초기화 ──
const editor = useEditor({
  extensions: [
    StarterKit.configure({ codeBlock: { HTMLAttributes: { class: 'code-block' } } }),
    Markdown.configure({ html: true, tightLists: true, transformPastedText: true }),
    CustomImage.configure({ allowBase64: false }),
    Link.configure({ openOnClick: false, HTMLAttributes: { rel: 'noopener noreferrer', target: '_blank' } }),
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({ resizable: false }),
    TableRow,
    TableHeader,
    TableCell,
    Placeholder.configure({ placeholder: props.placeholder }),
  ],
  content: props.modelValue || '',
  onUpdate({ editor }) {
    const md = editor.storage.markdown.getMarkdown()
    emit('update:modelValue', md)
  },
  editorProps: {
    handlePaste(view, event) {
      const items = Array.from(event.clipboardData?.items || [])
      const imageItems = items.filter(i => i.type.startsWith('image/'))
      if (!imageItems.length) return false
      event.preventDefault()
      imageItems.forEach(item => {
        const file = item.getAsFile()
        if (file) uploadAndInsert(file)
      })
      return true
    },
  },
})

// 외부 v-model 변경 반영 (모달 열기 등)
watch(() => props.modelValue, (val) => {
  if (!editor.value) return
  const current = editor.value.storage.markdown.getMarkdown()
  if (current !== val) {
    editor.value.commands.setContent(val || '', false)
  }
})

// ── 표 삽입 ──
function insertTable() {
  editor.value?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
}

// ── 링크 삽입 ──
function setLink() {
  const prev = editor.value?.getAttributes('link').href
  const url = window.prompt('URL 입력', prev || 'https://')
  if (url === null) return
  if (!url) { editor.value?.chain().focus().unsetLink().run(); return }
  editor.value?.chain().focus().setLink({ href: url }).run()
}
</script>

<style scoped>
.tiptap-wrap {
  border: 1px solid var(--outline, #e5e7eb);
  border-radius: var(--radius-sm, 6px);
  display: flex;
  flex-direction: column;
  background: var(--surface, #fff);
}

/* 툴바 */
.tiptap-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  border-bottom: 1px solid var(--outline, #e5e7eb);
  background: var(--gray-50, #f9fafb);
  border-radius: var(--radius-sm, 6px) var(--radius-sm, 6px) 0 0;
  flex-wrap: wrap;
}
.toolbar-group { display: flex; align-items: center; gap: 1px; }
.toolbar-sep { width: 1px; height: 18px; background: var(--outline, #e5e7eb); margin: 0 4px; }

.tb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-secondary, #555);
  font-size: 12px;
  font-weight: 600;
  transition: background 0.1s, color 0.1s;
  padding: 0;
}
.tb-btn .material-symbols-outlined { font-size: 17px; }
.tb-btn:hover:not(:disabled) { background: var(--gray-100, #f3f4f6); color: var(--text-primary, #111); }
.tb-btn.active { background: var(--primary-light, #dbeafe); color: var(--primary, #2563eb); }
.tb-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* 에디터 본문 */
.tiptap-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary, #111);
  cursor: text;
}

/* Tiptap ProseMirror 기본 스타일 */
:deep(.ProseMirror) {
  outline: none;
  min-height: 100px;
}
:deep(.ProseMirror p) { margin: 0 0 6px; }
:deep(.ProseMirror p:last-child) { margin-bottom: 0; }
:deep(.ProseMirror h1) { font-size: 1.4em; font-weight: 700; margin: 10px 0 6px; }
:deep(.ProseMirror h2) { font-size: 1.2em; font-weight: 700; margin: 10px 0 4px; }
:deep(.ProseMirror h3) { font-size: 1.05em; font-weight: 700; margin: 8px 0 4px; }
:deep(.ProseMirror ul), :deep(.ProseMirror ol) { padding-left: 20px; margin: 4px 0; }
:deep(.ProseMirror li) { margin: 2px 0; }
:deep(.ProseMirror blockquote) {
  border-left: 3px solid var(--primary, #2563eb);
  margin: 6px 0; padding: 4px 12px;
  color: var(--text-secondary, #555);
  background: var(--gray-50, #f9fafb);
}
:deep(.ProseMirror code) {
  background: var(--gray-100, #f3f4f6);
  padding: 1px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 13px;
}
:deep(.ProseMirror pre) {
  background: #1e293b;
  color: #e2e8f0;
  border-radius: 6px;
  padding: 10px 14px;
  margin: 6px 0;
  overflow-x: auto;
}
:deep(.ProseMirror pre code) {
  background: transparent; color: inherit; padding: 0; font-size: 13px;
}
:deep(.ProseMirror img) { max-width: 100%; height: auto; border-radius: 4px; cursor: default; }
:deep(.ProseMirror a) { color: var(--primary, #2563eb); text-decoration: underline; }

/* 체크박스 */
:deep(.ProseMirror ul[data-type="taskList"]) { padding-left: 4px; list-style: none; }
:deep(.ProseMirror ul[data-type="taskList"] li) {
  display: flex; align-items: flex-start; gap: 6px; margin: 3px 0;
}
:deep(.ProseMirror ul[data-type="taskList"] li > label) {
  flex-shrink: 0; margin-top: 3px; cursor: pointer;
}
:deep(.ProseMirror ul[data-type="taskList"] li > div) { flex: 1; }

/* 표 */
:deep(.ProseMirror table) {
  border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 13px;
}
:deep(.ProseMirror th), :deep(.ProseMirror td) {
  border: 1px solid var(--outline, #e5e7eb);
  padding: 5px 10px; min-width: 60px;
}
:deep(.ProseMirror th) { background: var(--gray-50, #f9fafb); font-weight: 600; }
:deep(.ProseMirror .selectedCell) { background: #dbeafe; }

/* placeholder */
:deep(.ProseMirror .is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  color: var(--text-muted, #9ca3af);
  float: left;
  pointer-events: none;
  height: 0;
}

/* 표 컨텍스트 툴바 */
.table-toolbar {
  display: flex; align-items: center; gap: 2px;
  padding: 3px 8px;
  background: var(--gray-50, #f9fafb);
  border-top: 1px solid var(--outline, #e5e7eb);
  flex-wrap: wrap;
}
.tb-sm {
  padding: 2px 7px; border: none; border-radius: 3px;
  background: transparent; color: var(--text-secondary, #555);
  font-size: 11px; cursor: pointer; white-space: nowrap;
  transition: background 0.1s;
}
.tb-sm:hover { background: var(--gray-100, #f3f4f6); color: var(--text-primary, #111); }
.tb-danger { color: var(--danger, #ef4444); }
.tb-danger:hover { background: var(--danger-light, #fef2f2); }
.tb-div { color: var(--outline, #e5e7eb); font-size: 12px; padding: 0 2px; }

/* 에러 */
.tiptap-error {
  background: #fef2f2; border-top: 1px solid #fca5a5;
  color: #b91c1c; font-size: 12px; padding: 6px 12px;
  border-radius: 0 0 var(--radius-sm, 6px) var(--radius-sm, 6px);
}
</style>

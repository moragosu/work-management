<template>
  <div class="tiptap-wrap" :style="{ minHeight: height }">
    <!-- 툴바 -->
    <div class="tiptap-toolbar" v-if="editor">
      <button v-if="expandable" type="button" class="tb-expand-btn" @click="openExpand" title="크게 보기">
        <span class="material-symbols-outlined">open_in_full</span>
      </button>
      <div class="toolbar-sep"></div>
      <!-- 인라인 서식 -->
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('bold') }" @click="editor.chain().focus().toggleBold().run()" title="굵게 (Ctrl+B)">
          <span class="material-symbols-outlined">format_bold</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('italic') }" @click="editor.chain().focus().toggleItalic().run()" title="기울임 (Ctrl+I)">
          <span class="material-symbols-outlined">format_italic</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('underline') }" @click="editor.chain().focus().toggleUnderline().run()" title="밑줄 (Ctrl+U)">
          <span class="material-symbols-outlined">format_underlined</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('strike') }" @click="editor.chain().focus().toggleStrike().run()" title="취소선">
          <span class="material-symbols-outlined">strikethrough_s</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('code') }" @click="editor.chain().focus().toggleCode().run()" title="인라인 코드">
          <span class="material-symbols-outlined">code</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('subscript') }" @click="editor.chain().focus().toggleSubscript().run()" title="아래 첨자">
          <span class="material-symbols-outlined">subscript</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('superscript') }" @click="editor.chain().focus().toggleSuperscript().run()" title="위 첨자">
          <span class="material-symbols-outlined">superscript</span>
        </button>
      </div>
      <div class="toolbar-sep"></div>
      <!-- 색상 -->
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('highlight') }" @click="editor.chain().focus().toggleHighlight().run()" title="형광펜">
          <span class="material-symbols-outlined">ink_highlighter</span>
        </button>
        <div class="tb-color-wrap" style="position:relative">
          <button type="button" class="tb-btn" title="글자 색상" @click="toggleColorPalette">
            <span class="material-symbols-outlined">format_color_text</span>
            <span class="tb-color-bar" :style="{ background: editor.getAttributes('textStyle').color || '#111' }"></span>
          </button>
          <div v-if="showColorPalette" class="color-palette" @click.stop>
            <div class="color-swatches">
              <button v-for="c in presetColors" :key="c" type="button"
                class="color-swatch"
                :class="{ active: editor.getAttributes('textStyle').color === c }"
                :style="{ background: c }"
                :title="c"
                @click="applyColor(c)" />
            </div>
            <label class="color-custom-btn">
              <span class="material-symbols-outlined" style="font-size:13px">colorize</span>
              직접 선택
              <input type="color" class="tb-color-input"
                :value="editor.getAttributes('textStyle').color || '#111111'"
                @input="e => { editor.chain().focus().setColor(e.target.value).run(); showColorPalette = false }" />
            </label>
          </div>
        </div>
        <button type="button" class="tb-btn" @click="editor.chain().focus().unsetColor().run()" title="색상 초기화">
          <span class="material-symbols-outlined" style="font-size:14px">format_color_reset</span>
        </button>
      </div>
      <div class="toolbar-sep"></div>
      <!-- 제목 -->
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 1 }) }" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" title="제목 1">H1</button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 2 }) }" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" title="제목 2">H2</button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 3 }) }" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" title="제목 3">H3</button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 4 }) }" @click="editor.chain().focus().toggleHeading({ level: 4 }).run()" title="제목 4">H4</button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 5 }) }" @click="editor.chain().focus().toggleHeading({ level: 5 }).run()" title="제목 5">H5</button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('heading', { level: 6 }) }" @click="editor.chain().focus().toggleHeading({ level: 6 }).run()" title="제목 6">H6</button>
      </div>
      <div class="toolbar-sep"></div>
      <!-- 정렬 -->
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive({ textAlign: 'left' }) }" @click="editor.chain().focus().setTextAlign('left').run()" title="왼쪽 정렬">
          <span class="material-symbols-outlined">format_align_left</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive({ textAlign: 'center' }) }" @click="editor.chain().focus().setTextAlign('center').run()" title="가운데 정렬">
          <span class="material-symbols-outlined">format_align_center</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive({ textAlign: 'right' }) }" @click="editor.chain().focus().setTextAlign('right').run()" title="오른쪽 정렬">
          <span class="material-symbols-outlined">format_align_right</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive({ textAlign: 'justify' }) }" @click="editor.chain().focus().setTextAlign('justify').run()" title="양쪽 정렬">
          <span class="material-symbols-outlined">format_align_justify</span>
        </button>
      </div>
      <div class="toolbar-sep"></div>
      <!-- 목록 -->
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
      <!-- 블록 / 삽입 -->
      <div class="toolbar-group">
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('blockquote') }" @click="editor.chain().focus().toggleBlockquote().run()" title="인용문">
          <span class="material-symbols-outlined">format_quote</span>
        </button>
        <button type="button" class="tb-btn" :class="{ active: editor.isActive('codeBlock') }" @click="editor.chain().focus().toggleCodeBlock().run()" title="코드 블록">
          <span class="material-symbols-outlined">data_object</span>
        </button>
        <button type="button" class="tb-btn" @click="editor.chain().focus().setHorizontalRule().run()" title="구분선">
          <span class="material-symbols-outlined">horizontal_rule</span>
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
      <!-- 실행취소 / 초기화 -->
      <div class="toolbar-group">
        <button type="button" class="tb-btn" @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()" title="실행 취소">
          <span class="material-symbols-outlined">undo</span>
        </button>
        <button type="button" class="tb-btn" @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()" title="다시 실행">
          <span class="material-symbols-outlined">redo</span>
        </button>
        <button type="button" class="tb-btn" @click="editor.chain().focus().clearNodes().unsetAllMarks().run()" title="서식 전체 초기화">
          <span class="material-symbols-outlined">format_clear</span>
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

  <Teleport to="body">
    <div v-if="expanded && expandable" class="tiptap-modal-overlay" @click.self="closeExpand">
      <div class="tiptap-modal">
        <div class="tiptap-modal-header">
          <span class="tiptap-modal-title">내용 편집</span>
          <div class="tiptap-modal-actions">
            <button class="tiptap-modal-cancel" @click="cancelExpand">취소</button>
            <button class="tiptap-modal-close" @click="closeExpand">닫기</button>
          </div>
        </div>
        <div class="tiptap-modal-body">
          <TiptapEditor
            :model-value="modelValue"
            @update:model-value="emit('update:modelValue', $event)"
            @image-uploaded="emit('image-uploaded', $event)"
            height="calc(85vh - 110px)"
            :expandable="false"
            :placeholder="placeholder"
          />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount, onUnmounted } from 'vue'
import { useEditor, EditorContent, VueNodeViewRenderer } from '@tiptap/vue-3'
import { Extension, textInputRule } from '@tiptap/core'
import ImageNodeView from './ImageNodeView.vue'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'

const ArrowInputRules = Extension.create({
  name: 'arrowInputRules',
  addInputRules() {
    return [
      textInputRule({ find: /->$/, replace: '→' }),
      textInputRule({ find: /<-$/, replace: '←' }),
      textInputRule({ find: /=>$/, replace: '⇒' }),
      textInputRule({ find: /<=$/, replace: '⇐' }),
      textInputRule({ find: /\^\^$/, replace: '↑' }),
      textInputRule({ find: /vv$/, replace: '↓' }),
    ]
  },
})

// NodeView로 렌더링 (이미지 바로 아래 사이즈 바 포함)
const CustomImage = Image.extend({
  addNodeView() {
    return VueNodeViewRenderer(ImageNodeView)
  },
})
import Link from '@tiptap/extension-link'
import { Underline } from '@tiptap/extension-underline'
import { TextAlign } from '@tiptap/extension-text-align'
import { Highlight } from '@tiptap/extension-highlight'
import { Color } from '@tiptap/extension-color'
import { TextStyle } from '@tiptap/extension-text-style'
import { Subscript } from '@tiptap/extension-subscript'
import { Superscript } from '@tiptap/extension-superscript'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table, TableRow, TableCell, TableHeader } from '@tiptap/extension-table'
import Placeholder from '@tiptap/extension-placeholder'
import { Markdown } from 'tiptap-markdown'
import axios from 'axios'

const props = defineProps({
  modelValue:  { type: String,  default: '' },
  height:      { type: String,  default: '160px' },
  placeholder: { type: String,  default: '내용을 입력하세요...' },
  expandable:  { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue', 'image-uploaded'])

const expanded = ref(false)
let preExpandContent = ''

// ── 글자색 팔레트 ──
const showColorPalette = ref(false)
const presetColors = [
  '#111827','#374151','#6b7280','#d1d5db',
  '#ef4444','#f97316','#eab308','#22c55e',
  '#14b8a6','#3b82f6','#8b5cf6','#ec4899',
  '#991b1b','#1e40af','#166534','#92400e',
]
function applyColor(color) {
  editor.value?.chain().focus().setColor(color).run()
  showColorPalette.value = false
}
function toggleColorPalette(e) {
  e.stopPropagation()
  showColorPalette.value = !showColorPalette.value
}
function onDocClickForColor() { showColorPalette.value = false }

function openExpand() {
  preExpandContent = props.modelValue ?? ''
  expanded.value = true
}
function closeExpand() {
  expanded.value = false
}
function cancelExpand() {
  emit('update:modelValue', preExpandContent)
  expanded.value = false
}

// ── 업로드 중 unmount 안전 처리 (부모가 이미지 정리 담당) ──
let isUnmounted = false
onMounted(() => document.addEventListener('click', onDocClickForColor))
onUnmounted(() => {
  isUnmounted = true
  document.removeEventListener('click', onDocClickForColor)
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
    StarterKit.configure({ codeBlock: { HTMLAttributes: { class: 'code-block' } }, link: false, underline: false }),
    Markdown.configure({ html: true, tightLists: true, transformPastedText: true }),
    CustomImage.configure({ allowBase64: false }),
    Link.configure({ openOnClick: false, HTMLAttributes: { rel: 'noopener noreferrer', target: '_blank' } }),
    Underline,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Highlight.configure({ multicolor: false }),
    TextStyle,
    Color,
    Subscript,
    Superscript,
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({ resizable: false }),
    TableRow,
    TableHeader,
    TableCell,
    Placeholder.configure({ placeholder: props.placeholder }),
    ArrowInputRules,
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

onBeforeUnmount(() => {
  // editor.destroy() 이후 브라우저 selection이 detached 노드를 가리키는 상태 방지
  window.getSelection()?.removeAllRanges()
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

defineExpose({
  insertText(text) {
    editor.value?.chain().focus().insertContent(text).run()
  }
})
</script>

<style scoped>
.tiptap-wrap {
  border: 1px solid var(--outline);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  background: var(--surface);
}

/* 툴바 */
.tiptap-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  border-bottom: 1px solid var(--outline);
  background: var(--gray-50);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  flex-wrap: wrap;
}
.toolbar-group { display: flex; align-items: center; gap: 1px; }
.toolbar-sep { width: 1px; height: 18px; background: var(--outline); margin: 0 4px; }

.tb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-secondary);
  font-size: var(--fs-xs);
  font-weight: var(--fw-semibold);
  transition: background 0.1s, color 0.1s;
  padding: 0;
}
.tb-btn .material-symbols-outlined { font-size: 17px; }
.tb-btn:hover:not(:disabled) { background: var(--gray-100); color: var(--text-primary, #111); }
.tb-btn.active { background: var(--primary-light, #dbeafe); color: var(--primary); }
.tb-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* 에디터 본문 */
.tiptap-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px 14px;
  font-size: var(--fs-md);
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
:deep(.ProseMirror h1) { font-size: 1.4em; font-weight: var(--fw-bold); margin: 10px 0 6px; }
:deep(.ProseMirror h2) { font-size: 1.2em; font-weight: var(--fw-bold); margin: 10px 0 4px; }
:deep(.ProseMirror h3) { font-size: 1.05em; font-weight: var(--fw-bold); margin: 8px 0 4px; }
:deep(.ProseMirror h4) { font-size: 0.95em; font-weight: var(--fw-bold); margin: 6px 0 3px; }
:deep(.ProseMirror h5) { font-size: 0.9em;  font-weight: var(--fw-semibold); margin: 6px 0 3px; }
:deep(.ProseMirror h6) { font-size: 0.85em; font-weight: var(--fw-semibold); margin: 6px 0 3px; color: var(--text-secondary); }
:deep(.ProseMirror ul), :deep(.ProseMirror ol) { padding-left: 20px; margin: 4px 0; }
:deep(.ProseMirror li) { margin: 2px 0; }
:deep(.ProseMirror blockquote) {
  border-left: 3px solid var(--primary);
  margin: 6px 0; padding: 4px 12px;
  color: var(--text-secondary);
  background: var(--gray-50);
}
:deep(.ProseMirror code) {
  background: var(--gray-100);
  padding: 1px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: var(--fs-sm);
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
  background: transparent; color: inherit; padding: 0; font-size: var(--fs-sm);
}
:deep(.ProseMirror img) { max-width: 100%; height: auto; border-radius: var(--radius-sm); cursor: default; }
:deep(.ProseMirror a) { color: var(--primary); text-decoration: underline; }
:deep(.ProseMirror u) { text-decoration: underline; }
:deep(.ProseMirror mark) { background: #fde68a; border-radius: 2px; padding: 0 2px; }
:deep(.ProseMirror hr) { border: none; border-top: 2px solid var(--outline); margin: 10px 0; }
:deep(.ProseMirror sub) { font-size: 0.75em; vertical-align: sub; }
:deep(.ProseMirror sup) { font-size: 0.75em; vertical-align: super; }

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
  border-collapse: collapse; width: 100%; margin: 8px 0; font-size: var(--fs-sm);
}
:deep(.ProseMirror th), :deep(.ProseMirror td) {
  border: 1px solid var(--outline);
  padding: 5px 10px; min-width: 60px;
}
:deep(.ProseMirror th) { background: var(--gray-50); font-weight: var(--fw-semibold); }
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
  background: var(--gray-50);
  border-top: 1px solid var(--outline);
  flex-wrap: wrap;
}
.tb-sm {
  padding: 2px 7px; border: none; border-radius: 3px;
  background: transparent; color: var(--text-secondary);
  font-size: var(--fs-2xs); cursor: pointer; white-space: nowrap;
  transition: background 0.1s;
}
.tb-sm:hover { background: var(--gray-100); color: var(--text-primary, #111); }
.tb-danger { color: var(--danger); }
.tb-danger:hover { background: var(--danger-light, #fef2f2); }
.tb-div { color: var(--outline); font-size: var(--fs-xs); padding: 0 2px; }
.tb-expand-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1.5px solid var(--primary);
  border-radius: 6px;
  background: var(--primary-light, #dbeafe);
  color: var(--primary);
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}
.tb-expand-btn .material-symbols-outlined { font-size: 17px; }
.tb-expand-btn:hover { background: var(--primary); color: #fff; }

/* 글자색 버튼 */
.tb-color-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.tb-color-bar {
  width: 14px; height: 3px; border-radius: 1px;
  position: absolute; bottom: 3px; left: 50%; transform: translateX(-50%);
}
.tb-color-input {
  position: absolute; inset: 0; opacity: 0; cursor: pointer;
  width: 100%; height: 100%; border: none; padding: 0;
}

/* 색상 팔레트 팝업 */
.color-palette {
  position: absolute; top: calc(100% + 4px); left: 0; z-index: 200;
  background: white; border: 1px solid var(--outline);
  border-radius: var(--radius-md); padding: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,.12);
  width: 116px;
}
.color-swatches {
  display: grid; grid-template-columns: repeat(4, 20px); gap: 4px;
  margin-bottom: 6px;
}
.color-swatch {
  width: 20px; height: 20px; border-radius: var(--radius-sm);
  border: 1.5px solid rgba(0,0,0,.1); cursor: pointer; padding: 0;
  transition: transform .1s;
}
.color-swatch:hover { transform: scale(1.2); border-color: rgba(0,0,0,.3); }
.color-swatch.active { border: 2px solid var(--primary); box-shadow: 0 0 0 1px var(--primary); }
.color-custom-btn {
  display: flex; align-items: center; gap: 4px;
  width: 100%; padding: 4px 6px; border-radius: var(--radius-sm);
  font-size: var(--fs-2xs); color: var(--text-secondary); cursor: pointer;
  position: relative; overflow: hidden; border: none; background: none;
  box-sizing: border-box;
}
.color-custom-btn:hover { background: var(--gray-50); }

/* 확장 모달 */
.tiptap-modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 2000;
  display: flex; align-items: center; justify-content: center;
}
.tiptap-modal {
  background: var(--surface);
  border-radius: 10px;
  width: 860px;
  max-width: 94vw;
  height: 85vh;
  display: flex; flex-direction: column;
  box-shadow: 0 12px 40px rgba(0,0,0,0.2);
  animation: tiptap-modal-in 0.15s ease;
}
@keyframes tiptap-modal-in {
  from { opacity:0; transform: scale(0.97); }
  to   { opacity:1; transform: scale(1); }
}
.tiptap-modal-header {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--outline);
  flex-shrink: 0;
}
.tiptap-modal-title { font-weight: var(--fw-semibold); font-size: var(--fs-md); color: var(--text-primary, #111); flex: 1; }
.tiptap-modal-actions { display: flex; gap: 6px; }
.tiptap-modal-cancel {
  padding: 4px 12px;
  border: 1px solid var(--outline);
  border-radius: 5px;
  background: var(--surface); font-size: var(--fs-sm); cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.1s;
}
.tiptap-modal-cancel:hover { background: var(--danger-light, #fef2f2); border-color: var(--danger); color: var(--danger); }
.tiptap-modal-close {
  padding: 4px 12px;
  border: 1px solid var(--outline);
  border-radius: 5px;
  background: var(--surface); font-size: var(--fs-sm); cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.1s;
}
.tiptap-modal-close:hover { background: var(--gray-100); color: var(--text-primary, #111); }
.tiptap-modal-body { flex: 1; overflow: hidden; padding: 12px; display: flex; flex-direction: column; }
.tiptap-modal-body :deep(.tiptap-wrap) { flex: 1; height: 100%; }

/* 에러 */
.tiptap-error {
  background: #fef2f2; border-top: 1px solid #fca5a5;
  color: #b91c1c; font-size: var(--fs-xs); padding: 6px 12px;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
}
</style>

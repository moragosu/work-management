<template>
  <node-view-wrapper class="image-nv" :class="{ 'image-nv--selected': selected }">
    <img :src="node.attrs.src" :style="imgStyle" data-drag-handle draggable="true" />
    <div v-if="selected" class="image-size-bar" contenteditable="false">
      <span class="bar-label">크기변경</span>
      <span class="bar-sep">:</span>
      <input
        type="number"
        class="bar-input"
        v-model.number="customPx"
        placeholder="px"
        min="50"
        max="1200"
        @keyup.enter="applyCustom"
      />
      <button class="bar-btn" @click="applyCustom">적용</button>
      <span class="bar-div">|</span>
      <button class="bar-btn" @click="applySize(300)">S</button>
      <button class="bar-btn" @click="applySize(500)">M</button>
      <button class="bar-btn" @click="applySize(700)">L</button>
      <button class="bar-btn" @click="applySize(null)">원본</button>
      <span class="bar-div">|</span>
      <button class="bar-btn" :class="{ 'bar-btn--active': hasBorder }" @click="toggleBorder">테두리</button>
    </div>
  </node-view-wrapper>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { NodeViewWrapper, nodeViewProps } from '@tiptap/vue-3'

const props = defineProps(nodeViewProps)

const customPx = ref('')

const currentWidth = computed(() => {
  const alt = props.node.attrs.alt || ''
  const m = alt.match(/^(\d+)px$/)
  return m ? parseInt(m[1]) : null
})

const hasBorder = computed(() => props.node.attrs.title === 'border')

watch(currentWidth, (v) => { customPx.value = v || '' }, { immediate: true })

const imgStyle = computed(() => {
  const w = currentWidth.value ? `width:${currentWidth.value}px;` : ''
  const b = hasBorder.value ? 'border:2px solid #94a3b8;' : ''
  return `${w}max-width:100%;height:auto;border-radius:4px;${b}`
})

function applySize(widthPx) {
  props.updateAttributes({ alt: widthPx ? `${widthPx}px` : '' })
  customPx.value = widthPx || ''
}

function applyCustom() {
  const px = parseInt(customPx.value)
  if (px >= 50 && px <= 1200) applySize(px)
}

function toggleBorder() {
  props.updateAttributes({ title: hasBorder.value ? '' : 'border' })
}
</script>

<style scoped>
.image-nv {
  display: inline-block;
  max-width: 100%;
  vertical-align: bottom;
}
.image-nv--selected img {
  outline: 2px solid var(--primary, #2563eb);
  border-radius: 4px;
}
.image-nv img {
  display: block;
  cursor: default;
}

.image-size-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  padding: 4px 8px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 6px;
  font-size: var(--fs-xs);
  flex-wrap: wrap;
  user-select: none;
}
.bar-label { color: var(--text-secondary, #555); font-size: var(--fs-xs); }
.bar-sep { color: var(--text-muted, #9ca3af); }
.bar-div { color: var(--outline, #d1d5db); padding: 0 2px; }
.bar-input {
  width: 56px;
  padding: 2px 6px;
  border: 1px solid var(--outline, #e5e7eb);
  border-radius: 4px;
  font-size: var(--fs-xs);
  text-align: right;
  outline: none;
}
.bar-input:focus { border-color: var(--primary, #2563eb); }
.bar-btn {
  padding: 2px 8px;
  border: 1px solid var(--outline, #e5e7eb);
  border-radius: 4px;
  background: #fff;
  font-size: var(--fs-xs);
  cursor: pointer;
  color: var(--text-primary, #111);
  transition: all 0.1s;
}
.bar-btn:hover {
  background: var(--primary-light, #dbeafe);
  border-color: var(--primary, #2563eb);
  color: var(--primary, #2563eb);
}
.bar-btn--active {
  background: #e2e8f0;
  border-color: #94a3b8;
  color: #334155;
  font-weight: 600;
}
.bar-btn--active:hover {
  background: #cbd5e1;
  border-color: #64748b;
  color: #1e293b;
}
</style>

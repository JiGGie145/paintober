<script setup>
import { useFileUpload } from '../../composables/useFileUpload.js'

const emit = defineEmits(['file-selected'])

const {
  file,
  error,
  isDragging,
  isValid,
  onDragEnter,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileInput,
  clear,
} = useFileUpload()

function handleDrop(event) {
  onDrop(event)
  if (isValid.value) emit('file-selected', file.value)
}

function handleInput(event) {
  onFileInput(event)
  if (isValid.value) emit('file-selected', file.value)
}

function handleClear() {
  clear()
  emit('file-selected', null)
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ 'dropzone--active': isDragging, 'dropzone--filled': isValid }"
    @dragenter="onDragEnter"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="handleDrop"
  >
    <!-- Icon -->
    <div class="dropzone__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" x2="12" y1="3" y2="15"/>
      </svg>
    </div>

    <!-- Default state -->
    <template v-if="!isValid">
      <p class="dropzone__heading">Drop your image here</p>
      <p class="dropzone__sub">or click to browse · JPG, PNG, WEBP · max 50 MB</p>
      <label class="dropzone__btn">
        Choose File
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          class="sr-only"
          @change="handleInput"
        />
      </label>
    </template>

    <!-- Filled state -->
    <template v-else>
      <p class="dropzone__filename">{{ file.name }}</p>
      <p class="dropzone__filesize">{{ formatSize(file.size) }}</p>
      <button class="dropzone__clear" @click.stop="handleClear">✕ Remove</button>
    </template>

    <!-- Error state -->
    <p v-if="error" class="dropzone__error">{{ error }}</p>
  </div>
</template>

<style scoped>
.dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  padding: var(--space-2xl) var(--space-xl);
  border: 3px dashed var(--color-indigo);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-sticker-md);
  background-color: var(--color-bg);
  cursor: pointer;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  min-height: 240px;
  text-align: center;
}

.dropzone--active {
  border-color: var(--color-lime);
  box-shadow: 6px 6px 0 0 var(--color-lime);
}

.dropzone--filled {
  border-color: var(--color-lime);
  border-style: solid;
}

/* ── Icon ─────────────────────────────────────────────────── */
.dropzone__icon {
  width: 56px;
  height: 56px;
  color: var(--color-indigo);
}

.dropzone--active .dropzone__icon,
.dropzone--filled .dropzone__icon {
  color: var(--color-lime);
}

.dropzone__icon svg {
  width: 100%;
  height: 100%;
}

/* ── Text ─────────────────────────────────────────────────── */
.dropzone__heading {
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
}

.dropzone__sub {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: var(--color-lavender);
}

.dropzone__filename {
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-bold);
  color: var(--color-lime);
  word-break: break-all;
}

.dropzone__filesize {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: var(--color-snow);
}

/* ── Buttons ──────────────────────────────────────────────── */
.dropzone__btn {
  display: inline-block;
  padding: var(--space-sm) var(--space-lg);
  background-color: var(--color-indigo);
  border: 3px solid var(--color-snow);
  box-shadow: var(--shadow-sticker-sm);
  border-radius: var(--radius-button);
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.dropzone__btn:hover { transform: scale(1.04); }

.dropzone__clear {
  padding: var(--space-sm) var(--space-md);
  background: transparent;
  border: 2px solid var(--color-pink);
  border-radius: var(--radius-button);
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  color: var(--color-pink);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.dropzone__clear:hover { transform: scale(1.04); }

/* ── Error ────────────────────────────────────────────────── */
.dropzone__error {
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  color: var(--color-pink);
}
</style>

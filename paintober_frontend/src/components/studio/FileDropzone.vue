<script setup>
import { ref } from 'vue'
import { useFileUpload } from '../../composables/useFileUpload.js'

const emit = defineEmits(['file-selected'])

const inputRef = ref(null)

const {
  file,
  error,
  previewUrl,
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
  // Reset so the same file can be re-selected
  event.target.value = ''
  if (isValid.value) emit('file-selected', file.value)
}

function triggerReupload() {
  if (inputRef.value) {
    inputRef.value.value = ''
    inputRef.value.click()
  }
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
    <!-- Hidden file input — always in DOM so reupload button can trigger it -->
    <input
      ref="inputRef"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="sr-only"
      @change="handleInput"
    />

    <Transition name="dz-fade" mode="out-in">
      <!-- ── Empty state ──────────────────────────────────── -->
      <div v-if="!isValid" key="empty" class="dropzone__body dropzone__body--empty">
        <div class="dropzone__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" x2="12" y1="3" y2="15"/>
          </svg>
        </div>
        <p class="dropzone__heading">Drop your image here</p>
        <p class="dropzone__sub">or click to browse · JPG, PNG, WEBP · max 50 MB</p>
        <button class="dropzone__btn" type="button" @click.stop="triggerReupload">
          Choose File
        </button>
        <p v-if="error" class="dropzone__error">{{ error }}</p>
      </div>

      <!-- ── Filled state — compact strip ───────────────────── -->
      <div v-else key="filled" class="dropzone__body dropzone__body--filled">
        <img
          class="dropzone__thumb"
          :src="previewUrl"
          :alt="file.name"
        />
        <div class="dropzone__info">
          <p class="dropzone__filename">{{ file.name }}</p>
          <p class="dropzone__filesize">{{ formatSize(file.size) }}</p>
        </div>
        <div class="dropzone__actions">
          <!-- Reupload -->
          <button
            class="dropzone__action-btn"
            type="button"
            title="Choose a different image"
            @click.stop="triggerReupload"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" x2="12" y1="3" y2="15"/>
            </svg>
          </button>
          <!-- Remove -->
          <button
            class="dropzone__action-btn dropzone__action-btn--remove"
            type="button"
            title="Remove image"
            @click.stop="handleClear"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* ── Outer shell — transitions between tall and compact ─────── */
.dropzone {
  border: 3px dashed var(--color-indigo);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-sticker-md);
  background-color: var(--color-bg);
  overflow: hidden;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    padding 0.35s ease,
    min-height 0.35s ease;
}

.dropzone--active {
  border-color: var(--color-lime);
  box-shadow: 6px 6px 0 0 var(--color-lime);
}

.dropzone--filled {
  border-color: var(--color-lime);
  border-style: solid;
  cursor: default;
}

/* ── Body layouts ───────────────────────────────────────────── */
.dropzone__body--empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  padding: var(--space-2xl) var(--space-xl);
  min-height: 240px;
  text-align: center;
  cursor: pointer;
}

.dropzone__body--filled {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
}

/* ── Transition ─────────────────────────────────────────────── */
.dz-fade-enter-active,
.dz-fade-leave-active {
  transition: opacity 0.18s ease;
}
.dz-fade-enter-from,
.dz-fade-leave-to {
  opacity: 0;
}

/* ── Icon (empty state) ─────────────────────────────────────── */
.dropzone__icon {
  width: 56px;
  height: 56px;
  color: var(--color-indigo);
}

.dropzone--active .dropzone__icon {
  color: var(--color-lime);
}

.dropzone__icon svg {
  width: 100%;
  height: 100%;
}

/* ── Empty state text ───────────────────────────────────────── */
.dropzone__heading {
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
}

.dropzone__sub {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-lavender);
}

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

/* ── Filled strip ───────────────────────────────────────────── */
.dropzone__thumb {
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 2px solid var(--color-indigo);
  flex-shrink: 0;
}

.dropzone__info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.dropzone__filename {
  font-family: var(--font-display);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
  color: var(--color-lime);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropzone__filesize {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-snow);
}

/* ── Action buttons (reupload / remove) ─────────────────────── */
.dropzone__actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.dropzone__action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: 2px solid var(--color-indigo);
  border-radius: var(--radius-sm);
  color: var(--color-indigo);
  cursor: pointer;
  transition: transform var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
}

.dropzone__action-btn svg {
  width: 18px;
  height: 18px;
}

.dropzone__action-btn:hover {
  border-color: var(--color-lime);
  color: var(--color-lime);
  transform: scale(1.1);
}

.dropzone__action-btn--remove:hover {
  border-color: var(--color-pink);
  color: var(--color-pink);
}

/* ── Error ───────────────────────────────────────────────────── */
.dropzone__error {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--color-pink);
}

/* ── Utility ─────────────────────────────────────────────────── */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>

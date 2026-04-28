<script setup>
import { ref } from 'vue'

const props = defineProps({
  params: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update:params'])

// Local state for the color picker
const pickerHex = ref('#ff5e04')
const hexInput = ref('#ff5e04')
const addError = ref(null)

const HEX_RE = /^#([0-9A-Fa-f]{6})$/

function syncFromPicker() {
  hexInput.value = pickerHex.value
  addError.value = null
}

function syncFromText() {
  const val = hexInput.value.trim()
  if (HEX_RE.test(val)) {
    pickerHex.value = val
    addError.value = null
  }
}

function addColor() {
  const val = hexInput.value.trim()
  if (!HEX_RE.test(val)) {
    addError.value = 'Enter a valid hex color, e.g. #ff5e04'
    return
  }
  if (props.params.user_palette_hex.includes(val)) {
    addError.value = 'Color already in palette.'
    return
  }
  addError.value = null
  emit('update:params', {
    ...props.params,
    user_palette_hex: [...props.params.user_palette_hex, val],
  })
}

function removeColor(hex) {
  emit('update:params', {
    ...props.params,
    user_palette_hex: props.params.user_palette_hex.filter((c) => c !== hex),
  })
}

function toggleReuse() {
  emit('update:params', {
    ...props.params,
    allow_color_reuse: !props.params.allow_color_reuse,
  })
}
</script>

<template>
  <div class="byop">
    <p class="byop__hint">
      Build your own palette. The pipeline will use only these colours.
    </p>

    <!-- Color adder -->
    <div class="byop__adder">
      <input
        type="color"
        v-model="pickerHex"
        class="byop__color-picker"
        @input="syncFromPicker"
        aria-label="Pick color"
      />
      <input
        type="text"
        v-model="hexInput"
        class="byop__hex-input"
        maxlength="7"
        placeholder="#rrggbb"
        @input="syncFromText"
        aria-label="Hex color value"
      />
      <button class="byop__add-btn" @click="addColor">+ Add</button>
    </div>
    <p v-if="addError" class="byop__error">{{ addError }}</p>

    <!-- Swatches -->
    <div v-if="params.user_palette_hex.length > 0" class="byop__swatches">
      <div
        v-for="hex in params.user_palette_hex"
        :key="hex"
        class="byop__swatch"
        :style="{ backgroundColor: hex }"
        :title="hex"
      >
        <button
          class="byop__swatch-remove"
          @click="removeColor(hex)"
          :aria-label="`Remove ${hex}`"
        >✕</button>
      </div>
    </div>
    <p v-else class="byop__empty">No colours added yet.</p>

    <!-- Allow reuse toggle -->
    <div class="byop__reuse-row">
      <span class="byop__reuse-label">Allow colour reuse across regions</span>
      <button
        class="toggle"
        :class="{ 'toggle--on': params.allow_color_reuse }"
        role="switch"
        :aria-checked="params.allow_color_reuse"
        @click="toggleReuse"
      >
        <span class="toggle__thumb" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.byop {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding-top: var(--space-md);
  border-top: 2px dashed var(--color-lavender);
}

.byop__hint {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: var(--color-lavender);
}

/* ── Adder ──────────────────────────────────────────────────── */
.byop__adder {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
  flex-wrap: wrap;
}

.byop__color-picker {
  width: 44px;
  height: 44px;
  padding: 2px;
  border: 3px solid var(--color-snow);
  border-radius: var(--radius-circle);
  box-shadow: var(--shadow-sticker-sm);
  background: none;
  cursor: pointer;
}

.byop__hex-input {
  flex: 1;
  min-width: 120px;
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--color-bg);
  border: 2px solid var(--color-indigo);
  border-radius: var(--radius-sm);
  color: var(--color-snow);
  font-family: var(--font-body);
  font-size: var(--text-body);
}

.byop__hex-input:focus {
  outline: none;
  border-color: var(--color-lime);
}

.byop__add-btn {
  padding: var(--space-xs) var(--space-lg);
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

.byop__add-btn:hover { transform: scale(1.04); }

.byop__error {
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  color: var(--color-pink);
}

/* ── Swatches ───────────────────────────────────────────────── */
.byop__swatches {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.byop__swatch {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-circle);
  border: 3px solid var(--color-snow);
  box-shadow: var(--shadow-sticker-sm);
}

.byop__swatch-remove {
  position: absolute;
  inset: -8px -8px auto auto;
  width: 20px;
  height: 20px;
  background-color: var(--color-pink);
  border: 2px solid var(--color-snow);
  border-radius: 50%;
  font-size: 9px;
  font-weight: var(--weight-black);
  color: var(--color-snow);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  padding: 0;
}

.byop__empty {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: var(--color-lavender);
}

/* ── Reuse toggle ───────────────────────────────────────────── */
.byop__reuse-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
}

.byop__reuse-label {
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
}

/* ── Shared toggle (same style as BasicParams) ──────────────── */
.toggle {
  position: relative;
  width: 52px;
  height: 28px;
  background-color: var(--color-lavender);
  border: 3px solid var(--color-snow);
  border-radius: 999px;
  box-shadow: var(--shadow-sticker-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  flex-shrink: 0;
}

.toggle--on {
  background-color: var(--color-lime);
}

.toggle__thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background-color: var(--color-snow);
  border-radius: 50%;
  transition: transform var(--transition-fast);
  box-shadow: 1px 1px 0 var(--color-midnight);
}

.toggle--on .toggle__thumb {
  transform: translateX(24px);
}
</style>

<script setup>
import { ref } from 'vue'
import BasicParams from './BasicParams.vue'
import ByopSection from './ByopSection.vue'

const props = defineProps({
  params: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update:params'])

const open = ref(false)

function updateParams(updated) {
  emit('update:params', updated)
}

function toggleByop() {
  emit('update:params', {
    ...props.params,
    use_user_palette: !props.params.use_user_palette,
  })
}
</script>

<template>
  <div class="params-panel">
    <!-- Header / toggle -->
    <button class="params-panel__header" @click="open = !open" :aria-expanded="open">
      <span class="params-panel__title">
        <svg class="params-panel__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/>
        </svg>
        Advanced Settings
      </span>
      <span class="params-panel__chevron" :class="{ 'params-panel__chevron--open': open }">▾</span>
    </button>

    <!-- Collapsible body -->
    <div v-show="open" class="params-panel__body">
      <BasicParams :params="params" @update:params="updateParams" />

      <!-- BYOP toggle row -->
      <div class="params-panel__byop-toggle">
        <span class="params-panel__byop-label">Use my own colour palette</span>
        <button
          class="toggle"
          :class="{ 'toggle--on': params.use_user_palette }"
          role="switch"
          :aria-checked="params.use_user_palette"
          @click="toggleByop"
        >
          <span class="toggle__thumb" />
        </button>
      </div>

      <ByopSection
        v-if="params.use_user_palette"
        :params="params"
        @update:params="updateParams"
      />
    </div>
  </div>
</template>

<style scoped>
.params-panel {
  background-color: color-mix(in srgb, var(--color-snow) 8%, transparent);
  border: var(--border-width-sticker) solid var(--color-indigo);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-sticker-md);
  overflow: hidden;
}

/* ── Header ─────────────────────────────────────────────────── */
.params-panel__header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
}

.params-panel__title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-family: var(--font-display);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
}

.params-panel__icon {
  width: 18px;
  height: 18px;
  color: var(--color-indigo);
}

.params-panel__chevron {
  font-size: var(--text-subheading);
  color: var(--color-lavender);
  transition: transform var(--transition-fast);
  line-height: 1;
}

.params-panel__chevron--open {
  transform: rotate(180deg);
}

/* ── Body ───────────────────────────────────────────────────── */
.params-panel__body {
  padding: var(--space-lg);
  border-top: 2px solid var(--color-indigo);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ── BYOP toggle row ────────────────────────────────────────── */
.params-panel__byop-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-md);
  background-color: color-mix(in srgb, var(--color-indigo) 12%, transparent);
  border-radius: var(--radius-md);
  border: 2px dashed var(--color-indigo);
}

.params-panel__byop-label {
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
}

/* ── Toggle (shared) ────────────────────────────────────────── */
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

<script setup>
import { computed } from 'vue'
import { useJobStore } from '../../stores/jobStore.js'

const jobStore = useJobStore()

const statusText = computed(() =>
  jobStore.status === 'processing'
    ? 'Processing your image…'
    : 'Queued — starting soon…'
)
</script>

<template>
  <div class="processing">
    <!-- Spinning ring -->
    <div class="processing__ring" aria-hidden="true">
      <div class="processing__spinner" />
    </div>

    <!-- Status text -->
    <p class="processing__heading">Generating your paint-by-numbers kit</p>
    <p class="processing__status">{{ statusText }}</p>

    <!-- Job ID -->
    <p class="processing__id">Job ID: {{ jobStore.id }}</p>

    <!-- Decorative step hints -->
    <div class="processing__steps">
      <div class="processing__step">
        <span class="processing__step-dot processing__step-dot--done" />
        Uploaded
      </div>
      <div class="processing__step-divider" />
      <div class="processing__step">
        <span class="processing__step-dot processing__step-dot--active" />
        Processing
      </div>
      <div class="processing__step-divider" />
      <div class="processing__step">
        <span class="processing__step-dot" />
        Ready
      </div>
    </div>
  </div>
</template>

<style scoped>
.processing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  min-height: 70vh;
  padding: var(--space-2xl);
  text-align: center;
}

/* ── Ring ───────────────────────────────────────────────────── */
.processing__ring {
  position: relative;
  width: 96px;
  height: 96px;
}

.processing__spinner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 6px solid color-mix(in srgb, var(--color-indigo) 30%, transparent);
  border-top-color: var(--color-lime);
  animation: spin 1s linear infinite;
}

/* ── Text ───────────────────────────────────────────────────── */
.processing__heading {
  font-family: var(--font-display);
  font-size: var(--text-heading);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
  max-width: 480px;
}

.processing__status {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-lavender);
}

.processing__id {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: color-mix(in srgb, var(--color-snow) 40%, transparent);
  letter-spacing: 0.05em;
}

/* ── Steps ──────────────────────────────────────────────────── */
.processing__steps {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-top: var(--space-md);
}

.processing__step {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  color: var(--color-lavender);
}

.processing__step-divider {
  width: 32px;
  height: 2px;
  background-color: color-mix(in srgb, var(--color-lavender) 40%, transparent);
}

.processing__step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: color-mix(in srgb, var(--color-lavender) 40%, transparent);
  border: 2px solid var(--color-lavender);
  flex-shrink: 0;
}

.processing__step-dot--done {
  background-color: var(--color-lime);
  border-color: var(--color-lime);
}

.processing__step-dot--active {
  background-color: transparent;
  border-color: var(--color-lime);
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-lime) 60%, transparent); }
  50%       { box-shadow: 0 0 0 6px transparent; }
}
</style>

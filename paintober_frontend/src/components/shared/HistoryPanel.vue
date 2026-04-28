<script setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useHistoryStore } from '../../stores/historyStore.js'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])

const router = useRouter()
const historyStore = useHistoryStore()

// Fetch fresh history whenever the panel opens
watch(() => props.open, (isOpen) => {
  if (isOpen) historyStore.fetchHistory()
})

function statusLabel(status) {
  if (status === 'done')       return 'Done'
  if (status === 'failed')     return 'Failed'
  if (status === 'processing') return 'Processing'
  return 'Queued'
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString(undefined, {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function openJob(job) {
  emit('close')
  router.push({ name: 'studio', params: { jobId: job.id } })
}
</script>

<template>
  <!-- Backdrop -->
  <Transition name="fade">
    <div
      v-if="open"
      class="history-backdrop"
      aria-hidden="true"
      @click="emit('close')"
    />
  </Transition>

  <!-- Panel -->
  <Transition name="slide">
    <aside v-if="open" class="history-panel" role="dialog" aria-label="Job history">

      <!-- Header -->
      <div class="history-panel__header">
        <h2 class="history-panel__title">History</h2>
        <button class="history-panel__close" aria-label="Close history" @click="emit('close')">✕</button>
      </div>

      <!-- Loading -->
      <div v-if="historyStore.loading" class="history-panel__state">
        <div class="history-panel__spinner" aria-hidden="true" />
        <p class="history-panel__state-text">Loading…</p>
      </div>

      <!-- Error -->
      <div v-else-if="historyStore.error" class="history-panel__state">
        <p class="history-panel__error-text">{{ historyStore.error }}</p>
      </div>

      <!-- Empty -->
      <div v-else-if="historyStore.jobs.length === 0" class="history-panel__state">
        <p class="history-panel__state-text">No jobs yet. Go make something!</p>
      </div>

      <!-- Job list -->
      <ul v-else class="history-panel__list" role="list">
        <li
          v-for="job in historyStore.jobs"
          :key="job.id"
          class="history-panel__item"
          :class="`history-panel__item--${job.status}`"
          :role="job.status === 'done' ? 'button' : undefined"
          :tabindex="job.status === 'done' ? 0 : undefined"
          :aria-label="job.status === 'done' ? `Open results for job ${job.id}` : undefined"
          @click="job.status === 'done' && openJob(job)"
          @keydown.enter="job.status === 'done' && openJob(job)"
        >
          <div class="history-panel__item-row">
            <span class="history-panel__item-id">{{ job.id.slice(0, 8) }}…</span>
            <span class="history-panel__badge" :class="`history-panel__badge--${job.status}`">
              {{ statusLabel(job.status) }}
            </span>
          </div>
          <time class="history-panel__item-date" :datetime="job.created_at">
            {{ formatDate(job.created_at) }}
          </time>
          <span v-if="job.status === 'done'" class="history-panel__item-cta">
            View results →
          </span>
        </li>
      </ul>

    </aside>
  </Transition>
</template>

<style scoped>
/* ── Backdrop ───────────────────────────────────────────────── */
.history-backdrop {
  position: fixed;
  inset: 0;
  background-color: color-mix(in srgb, var(--color-bg) 60%, transparent);
  z-index: var(--z-panel);
}

/* ── Panel ──────────────────────────────────────────────────── */
.history-panel {
  position: fixed;
  top: 0;
  right: 0;
  height: 100dvh;
  width: min(360px, 92vw);
  background-color: var(--color-bg);
  border-left: 4px solid var(--color-indigo);
  box-shadow: -6px 0 0 0 var(--color-midnight);
  z-index: calc(var(--z-panel) + 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Panel header ───────────────────────────────────────────── */
.history-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 3px solid var(--color-indigo);
  flex-shrink: 0;
}

.history-panel__title {
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-extrabold);
  color: var(--color-snow);
}

.history-panel__close {
  background: transparent;
  border: 2px solid var(--color-lavender);
  border-radius: var(--radius-badge);
  color: var(--color-lavender);
  font-size: var(--text-body);
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--transition-fast);
}
.history-panel__close:hover { transform: scale(1.1); }

/* ── States ─────────────────────────────────────────────────── */
.history-panel__state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  padding: var(--space-xl);
}

.history-panel__spinner {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid var(--color-indigo);
  border-top-color: var(--color-lime);
  animation: spin 0.8s linear infinite;
}

.history-panel__state-text {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-lavender);
  text-align: center;
}

.history-panel__error-text {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-pink);
  text-align: center;
}

/* ── List ───────────────────────────────────────────────────── */
.history-panel__list {
  list-style: none;
  padding: var(--space-md);
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  overflow-y: auto;
  flex: 1;
}

/* ── Item ───────────────────────────────────────────────────── */
.history-panel__item {
  background-color: var(--color-snow);
  border: 3px solid var(--color-bg);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-sticker-sm);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  transition: transform var(--transition-fast);
}

.history-panel__item--done {
  cursor: pointer;
}
.history-panel__item--done:hover {
  transform: scale(1.02);
}

.history-panel__item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-panel__item-id {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--color-bg);
}

.history-panel__item-date {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: color-mix(in srgb, var(--color-bg) 60%, transparent);
}

.history-panel__item-cta {
  font-family: var(--font-display);
  font-size: var(--text-sm);
  font-weight: var(--weight-extrabold);
  color: var(--color-indigo);
}

/* ── Status badges ──────────────────────────────────────────── */
.history-panel__badge {
  padding: 2px var(--space-sm);
  border-radius: 999px;
  border: 2px solid var(--color-bg);
  font-family: var(--font-display);
  font-size: var(--text-sm);
  font-weight: var(--weight-extrabold);
  box-shadow: var(--shadow-sticker-sm);
}

.history-panel__badge--done       { background-color: var(--color-lime);     color: var(--color-bg); }
.history-panel__badge--processing { background-color: var(--color-lavender); color: var(--color-snow); }
.history-panel__badge--pending    { background-color: var(--color-lavender); color: var(--color-snow); }
.history-panel__badge--failed     { background-color: var(--color-pink);     color: var(--color-snow); }

/* ── Transitions ────────────────────────────────────────────── */
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to    { opacity: 0; }

.slide-enter-active,
.slide-leave-active { transition: transform 0.25s ease; }
.slide-enter-from,
.slide-leave-to    { transform: translateX(100%); }
</style>

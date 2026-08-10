<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useJobStore } from '../stores/jobStore.js'
import { useJobPoller } from '../composables/useJobPoller.js'
import { getJob } from '../api/jobs.js'
import UploadPanel from '../components/studio/UploadPanel.vue'
import ProcessingScreen from '../components/studio/ProcessingScreen.vue'
import ResultsScreen from '../components/studio/ResultsScreen.vue'

const route = useRoute()
const router = useRouter()
const jobStore = useJobStore()
const { start: startPoller } = useJobPoller()
const processingFile = ref(null)

// ── Re-hydrate from URL (on load AND when param changes) ────────
const rehydrating = ref(false)

async function hydrateFromParam(jobId) {
  if (!jobId) {
    // No param — clear any active job and show the upload form
    jobStore.reset()
    processingFile.value = null
    return
  }
  if (jobStore.id === jobId) return  // already loaded — nothing to do
  rehydrating.value = true
  processingFile.value = null
  jobStore.reset()
  try {
    const job = await getJob(jobId)
    jobStore.setFromStatusResponse(job)
  } catch {
    // Job not found or session mismatch — clear param and show upload form
    router.replace({ name: 'studio' })
  } finally {
    rehydrating.value = false
  }
}

onMounted(() => hydrateFromParam(route.params.jobId))

// Re-runs when HistoryPanel (or any navigation) changes the param
watch(() => route.params.jobId, (jobId) => hydrateFromParam(jobId))

// ── Keep URL in sync with active job ────────────────────────────
watch(() => jobStore.id, (id) => {
  if (id) {
    if (route.params.jobId !== id) {
      router.replace({ name: 'studio', params: { jobId: id } })
    }
    startPoller()
  }
}, { immediate: true })

const showUpload      = computed(() => !rehydrating.value && jobStore.status === null)
const showProcessing  = computed(() => !rehydrating.value && (jobStore.status === 'pending' || jobStore.status === 'processing'))
const showResults     = computed(() => !rehydrating.value && jobStore.status === 'done')
const showFailed      = computed(() => !rehydrating.value && jobStore.status === 'failed')

function handleJobCreated(file) {
  processingFile.value = file
}

function startOver() {
  processingFile.value = null
  jobStore.reset()
  router.push({ name: 'studio' })
}
</script>

<template>
  <div class="studio">

    <!-- Re-hydrating from URL -->
    <div v-if="rehydrating" class="studio__loading" aria-live="polite">
      <div class="studio__loading-spinner" aria-hidden="true" />
      <p class="studio__loading-text">Fetching job…</p>
    </div>

    <!-- Upload & Configure -->
    <UploadPanel v-if="showUpload" @job-created="handleJobCreated" />

    <!-- Processing -->
    <ProcessingScreen v-else-if="showProcessing" :file="processingFile" />

    <!-- Results -->
    <ResultsScreen v-else-if="showResults" @start-over="startOver" />

    <!-- Failed -->
    <div v-else-if="showFailed" class="studio__error-state">
      <p class="studio__error-heading">Something went wrong</p>
      <p class="studio__error-msg">{{ jobStore.error ?? 'Job failed. Please try again.' }}</p>
      <button class="studio__reset-btn" @click="startOver">Try Again</button>
    </div>

  </div>
</template>

<style scoped>
.studio {
  min-height: calc(100dvh - 80px);
}

/* ── Re-hydrating state ─────────────────────────────────────── */
.studio__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  min-height: calc(100dvh - 80px);
}

.studio__loading-spinner {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 4px solid var(--color-indigo);
  border-top-color: var(--color-lime);
  animation: spin 0.8s linear infinite;
}

.studio__loading-text {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-lavender);
}

/* ── Failed state ───────────────────────────────────────────── */
.studio__error-state {
  max-width: 680px;
  margin: 0 auto;
  padding: var(--space-2xl) var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.studio__error-heading {
  font-family: var(--font-display);
  font-size: var(--text-heading);
  font-weight: var(--weight-black);
  color: var(--color-pink);
}

.studio__error-msg {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-snow);
}

.studio__reset-btn {
  align-self: flex-start;
  padding: var(--space-sm) var(--space-xl);
  background-color: var(--color-indigo);
  border: 4px solid var(--color-snow);
  box-shadow: var(--shadow-sticker-md);
  border-radius: var(--radius-button);
  font-family: var(--font-display);
  font-size: var(--text-body);
  font-weight: var(--weight-extrabold);
  color: var(--color-snow);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.studio__reset-btn:hover  { transform: scale(1.05); }
.studio__reset-btn:active { transform: scale(0.95); }
</style>


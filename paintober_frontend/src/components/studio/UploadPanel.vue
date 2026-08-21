<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import FileDropzone from './FileDropzone.vue'
import ParametersPanel from './ParametersPanel.vue'
import PaletteSelector from './PaletteSelector.vue'
import ErrorBanner from '../shared/ErrorBanner.vue'
import { createJob } from '../../api/jobs.js'
import { useJobStore } from '../../stores/jobStore.js'
import { parseApiError } from '../../utils/parseApiError.js'
import { usePalettes } from '../../composables/usePalettes.js'
import { listOrganizerEvents } from '../../api/events.js'
import { useAuthStore } from '../../stores/authStore.js'
import { useEventContextStore } from '../../stores/eventContextStore.js'

const jobStore = useJobStore()
const route = useRoute()
const auth = useAuthStore()
const eventContext = useEventContextStore()
const { palettes, loading: palettesLoading, fetchPalettes } = usePalettes()
const emit = defineEmits(['job-created'])

const selectedFile = ref(null)
const submitting = ref(false)
const submitError = ref(null)
const organizerEvents = ref([])
const selectedEventId = ref('')
const kitName = ref('')

// 'auto' | 'preset' | 'byop'
const paletteMode = ref('auto')
const selectedPresetId = ref(null)

// Default parameter values
const params = ref({
  k_colors: 12,
  line_thickness: 1,
  smooth_method: 'gaussian',
  blur_sigma: 1.5,
  min_region_pct: 0.03,
  no_merge: false,
  use_user_palette: false,
  allow_color_reuse: true,
  user_palette_hex: [],
})

onMounted(async () => {
  if (!auth.hydrated) await auth.hydrate()
  if (!auth.isAuthenticated || eventContext.isActive) return
  try {
    organizerEvents.value = (await listOrganizerEvents()).filter((event) => event.accepts_new_generations)
    const requestedEventId = String(route.query.eventId ?? '')
    if (organizerEvents.value.some((event) => event.id === requestedEventId)) selectedEventId.value = requestedEventId
  } catch {
    organizerEvents.value = []
  }
})

// React to palette mode changes
watch(paletteMode, (mode) => {
  if (mode === 'auto') {
    selectedPresetId.value = null
    params.value = {
      ...params.value,
      use_user_palette: false,
      user_palette_hex: [],
    }
  } else if (mode === 'byop') {
    selectedPresetId.value = null
    params.value = {
      ...params.value,
      use_user_palette: true,
      user_palette_hex: [],
    }
  } else if (mode === 'preset') {
    fetchPalettes()
    // Clear any BYOP hex; a preset must be explicitly chosen
    params.value = {
      ...params.value,
      use_user_palette: false,
      user_palette_hex: [],
    }
  }
})

function onPresetSelected(presetId) {
  selectedPresetId.value = presetId
  const set = palettes.value?.find((p) => p.id === presetId)
  if (!set) return
  params.value = {
    ...params.value,
    use_user_palette: true,
    user_palette_hex: set.colors.map((c) => c.hex),
    k_colors: set.colors.length,
  }
}

function onFileSelected(file) {
  selectedFile.value = file
  submitError.value = null
}

async function submit() {
  if (!selectedFile.value) return
  submitting.value = true
  submitError.value = null

  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    if (kitName.value.trim()) formData.append('kit_name', kitName.value.trim())
    if (selectedEventId.value) formData.append('event_id', selectedEventId.value)

    // Append each param
    // A selected preset/BYOP palette defines the number of colours to use.
    // Do not retain the auto-generated default of 12 for larger palettes.
    const kColors = params.value.use_user_palette
      ? params.value.user_palette_hex.length
      : params.value.k_colors
    formData.append('k_colors', kColors)
    formData.append('line_thickness', params.value.line_thickness)
    formData.append('smooth_method', params.value.smooth_method)
    formData.append('blur_sigma', params.value.blur_sigma)
    formData.append('min_region_pct', params.value.min_region_pct)
    formData.append('no_merge', params.value.no_merge)

    if (params.value.use_user_palette) {
      formData.append('use_user_palette', true)
      formData.append('allow_color_reuse', params.value.allow_color_reuse)
      params.value.user_palette_hex.forEach((hex) => {
        formData.append('user_palette_hex', hex)
      })
    }

    const result = await createJob(formData)
    jobStore.setFromCreateResponse(result)
    emit('job-created', selectedFile.value)
  } catch (err) {
    submitError.value = parseApiError(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="upload-panel">
    <h1 class="upload-panel__heading">Create Your Kit</h1>
    <p class="upload-panel__sub">Upload a photo and we'll turn it into a paint-by-numbers kit.</p>

    <div class="upload-panel__kit-options">
      <label for="kit-name">Kit name <span>(optional)</span></label>
      <input id="kit-name" v-model="kitName" maxlength="200" placeholder="e.g. Summer garden" />
      <label v-if="auth.isAuthenticated && !eventContext.isActive" for="kit-event">Create for event</label>
      <select v-if="auth.isAuthenticated && !eventContext.isActive" id="kit-event" v-model="selectedEventId">
        <option value="">Personal kit</option>
        <option v-for="event in organizerEvents" :key="event.id" :value="event.id">{{ event.name }}</option>
      </select>
    </div>

    <FileDropzone @file-selected="onFileSelected" />

    <PaletteSelector
      :params="params"
      :paletteMode="paletteMode"
      :palettes="palettes"
      :palettesLoading="palettesLoading"
      :selectedPresetId="selectedPresetId"
      @update:paletteMode="paletteMode = $event"
      @update:params="params = $event"
      @select-preset="onPresetSelected"
    />

    <ParametersPanel v-model:params="params" :paletteMode="paletteMode" />

    <ErrorBanner v-if="submitError" :message="submitError" @dismiss="submitError = null" />

    <button
      class="upload-panel__submit"
      :disabled="!selectedFile || submitting"
      @click="submit"
    >
      <span v-if="submitting">Generating…</span>
      <span v-else>Generate Kit →</span>
    </button>
  </div>
</template>

<style scoped>
.upload-panel {
  max-width: 80vw;
  margin: 0 auto;
  padding: var(--space-2xl) var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

@media (max-width: 600px) {
  .upload-panel {
    padding: 0 0;
    max-width: 90vw;
  }
}

.upload-panel__heading {
  font-family: var(--font-display);
  font-size: var(--text-heading);
  font-weight: var(--weight-black);
  color: var(--color-snow);
  text-shadow: 3px 3px 0 var(--color-midnight);
  align-self: center;
}

.upload-panel__kit-options {
  display: grid;
  gap: var(--space-sm);
  max-width: 620px;
  width: 100%;
  margin: 0 auto;
}

.upload-panel__kit-options label {
  color: var(--color-lime);
  font-weight: var(--weight-bold);
}

.upload-panel__kit-options label span {
  color: var(--color-lavender);
  font-weight: var(--weight-normal);
}

.upload-panel__kit-options input,
.upload-panel__kit-options select {
  min-height: 48px;
  padding: 0 var(--space-md);
  border: var(--border-sticker-snow);
  border-radius: var(--radius-sm);
  background: var(--color-snow);
  color: var(--color-bg);
  font-size: var(--text-body);
}

.upload-panel__sub {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-lavender);
  margin-top: calc(-1 * var(--space-md));
  align-self: center;
}



.upload-panel__submit {
  align-self: flex-start;
  padding: var(--space-md) var(--space-2xl);
  background-color: var(--color-lime);
  border: 4px solid var(--color-bg);
  box-shadow: var(--shadow-sticker-lg);
  border-radius: var(--radius-button);
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-extrabold);
  color: var(--color-bg);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.upload-panel__submit:hover:not(:disabled) { transform: scale(1.05); }
.upload-panel__submit:active:not(:disabled) { transform: scale(0.95); }

.upload-panel__submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}
</style>

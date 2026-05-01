<script setup>
import { ref, watch } from 'vue'
import FileDropzone from './FileDropzone.vue'
import ParametersPanel from './ParametersPanel.vue'
import PaletteSelector from './PaletteSelector.vue'
import ErrorBanner from '../shared/ErrorBanner.vue'
import { createJob } from '../../api/jobs.js'
import { useJobStore } from '../../stores/jobStore.js'
import { parseApiError } from '../../utils/parseApiError.js'
import { usePalettes } from '../../composables/usePalettes.js'

const jobStore = useJobStore()
const { palettes, loading: palettesLoading, fetchPalettes } = usePalettes()

const selectedFile = ref(null)
const submitting = ref(false)
const submitError = ref(null)

// 'auto' | 'preset' | 'byop'
const paletteMode = ref('auto')
const selectedPresetId = ref(null)

// Default parameter values
const params = ref({
  k_colors: 12,
  line_thickness: 1,
  min_region_area: 200,
  apply_gaussian: true,
  contour_epsilon: 0.002,
  use_user_palette: false,
  allow_color_reuse: false,
  user_palette_hex: [],
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

    // Append each param
    formData.append('k_colors', params.value.k_colors)
    formData.append('line_thickness', params.value.line_thickness)
    formData.append('min_region_area', params.value.min_region_area)
    formData.append('apply_gaussian', params.value.apply_gaussian)
    formData.append('contour_epsilon', params.value.contour_epsilon)

    if (params.value.use_user_palette) {
      formData.append('use_user_palette', true)
      formData.append('allow_color_reuse', params.value.allow_color_reuse)
      params.value.user_palette_hex.forEach((hex) => {
        formData.append('user_palette_hex', hex)
      })
    }

    const result = await createJob(formData)
    jobStore.setFromCreateResponse(result)
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

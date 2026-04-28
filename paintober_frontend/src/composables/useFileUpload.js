import { ref, computed } from 'vue'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE_BYTES = 50 * 1024 * 1024 // 50 MB

/**
 * Manages file selection via drag-and-drop or a file picker.
 * Performs client-side validation before any API call is made.
 *
 * Usage:
 *   const { file, error, isDragging, onDrop, onFileInput, clear } = useFileUpload()
 */
export function useFileUpload() {
  /** @type {import('vue').Ref<File|null>} */
  const file = ref(null)
  /** @type {import('vue').Ref<string|null>} */
  const error = ref(null)
  const isDragging = ref(false)

  const isValid = computed(() => file.value !== null && error.value === null)

  function validate(candidate) {
    if (!ACCEPTED_TYPES.includes(candidate.type)) {
      return 'Unsupported format. Please upload a JPG, PNG, or WEBP image.'
    }
    if (candidate.size > MAX_SIZE_BYTES) {
      return `File is too large (${(candidate.size / 1024 / 1024).toFixed(1)} MB). Maximum size is 50 MB.`
    }
    return null
  }

  function setFile(candidate) {
    const validationError = validate(candidate)
    if (validationError) {
      file.value = null
      error.value = validationError
    } else {
      file.value = candidate
      error.value = null
    }
  }

  function clear() {
    file.value = null
    error.value = null
    isDragging.value = false
  }

  // ---- Drag-and-drop handlers --------------------------------

  function onDragEnter(event) {
    event.preventDefault()
    isDragging.value = true
  }

  function onDragOver(event) {
    event.preventDefault()
  }

  function onDragLeave(event) {
    event.preventDefault()
    isDragging.value = false
  }

  function onDrop(event) {
    event.preventDefault()
    isDragging.value = false
    const dropped = event.dataTransfer?.files?.[0]
    if (dropped) setFile(dropped)
  }

  // ---- File input handler ------------------------------------

  function onFileInput(event) {
    const picked = event.target?.files?.[0]
    if (picked) setFile(picked)
  }

  return {
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
  }
}

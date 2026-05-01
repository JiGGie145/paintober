import { ref } from 'vue'
import { getPalettes } from '../api/palettes.js'

// Module-level cache — survives component remounts within a session.
const palettes = ref(null)
const loading = ref(false)
const error = ref(null)

export function usePalettes() {
  async function fetchPalettes() {
    if (palettes.value !== null || loading.value) return
    loading.value = true
    error.value = null
    try {
      palettes.value = await getPalettes()
    } catch (err) {
      error.value = err.message ?? 'Failed to load palettes.'
    } finally {
      loading.value = false
    }
  }

  return { palettes, loading, error, fetchPalettes }
}

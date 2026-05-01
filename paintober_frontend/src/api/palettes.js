const BASE = (import.meta.env.VITE_API_BASE ?? '') + '/api'

/**
 * Fetch all preset paint sets with nested color arrays.
 * @returns {PaintSet[]}
 */
export async function getPalettes() {
  const response = await fetch(`${BASE}/palettes/`, {
    credentials: 'include',
  })
  if (!response.ok) {
    throw new Error(`Failed to load palettes: ${response.status}`)
  }
  return response.json()
}

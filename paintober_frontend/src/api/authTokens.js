const BASE = (import.meta.env.VITE_API_BASE ?? '') + '/api'
const REFRESH_STORAGE_KEY = 'paintober_refresh_token'

let accessToken = ''

export function getAccessToken() {
  return accessToken
}

export function setTokens({ access, refresh }) {
  accessToken = access ?? ''
  if (refresh) sessionStorage.setItem(REFRESH_STORAGE_KEY, refresh)
}

export function clearTokens() {
  accessToken = ''
  sessionStorage.removeItem(REFRESH_STORAGE_KEY)
}

export function getRefreshToken() {
  return sessionStorage.getItem(REFRESH_STORAGE_KEY) ?? ''
}

export async function refreshAccessToken() {
  const refresh = getRefreshToken()
  if (!refresh) throw new Error('No refresh token available')

  const response = await fetch(`${BASE}/djoser-auth/jwt/refresh/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })

  if (!response.ok) {
    clearTokens()
    throw new Error(`Token refresh failed: ${response.status}`)
  }

  const tokens = await response.json()
  setTokens(tokens)
  return tokens.access
}
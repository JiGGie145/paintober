/**
 * Paintober API client.
 * All requests go through the Vite proxy (/api → http://localhost:8000).
 * CSRF token is read fresh from the cookie on every unsafe request.
 */

const BASE = '/api'

// ----------------------------------------------------------------
// CSRF helper — reads csrftoken cookie set by Django
// ----------------------------------------------------------------
function getCsrfToken() {
  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
  return match ? match.split('=')[1] : ''
}

// ----------------------------------------------------------------
// Core fetch wrapper
// ----------------------------------------------------------------
async function apiFetch(path, options = {}) {
  const { method = 'GET', body, headers = {} } = options

  const isUnsafe = !['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(
    method.toUpperCase()
  )

  const requestHeaders = {
    ...headers,
    ...(isUnsafe && { 'X-CSRFToken': getCsrfToken() }),
  }

  // Let the browser set Content-Type for FormData automatically
  if (!(body instanceof FormData)) {
    requestHeaders['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${BASE}${path}`, {
    method,
    credentials: 'include',
    headers: requestHeaders,
    body,
  })

  if (!response.ok) {
    const error = new Error(`API error: ${response.status}`)
    error.status = response.status
    error.retryAfter = response.headers.get('Retry-After') ?? null
    try {
      error.data = await response.json()
    } catch {
      error.data = null
    }
    throw error
  }

  // 204 No Content — return null
  if (response.status === 204) return null

  return response.json()
}

// ----------------------------------------------------------------
// Public API functions
// ----------------------------------------------------------------

/**
 * Submit a new job.
 * @param {FormData} formData — must include `image` file + optional params
 * @returns {{ job_id: string, status: string }}
 */
export function createJob(formData) {
  return apiFetch('/jobs/create/', {
    method: 'POST',
    body: formData,
  })
}

/**
 * Poll a single job by ID.
 * @param {string} jobId
 * @returns {JobStatus}
 */
export function getJob(jobId) {
  return apiFetch(`/jobs/${jobId}/`)
}

/**
 * List all jobs for the current session.
 * @returns {JobList[]}
 */
export function listJobs() {
  return apiFetch('/jobs/')
}

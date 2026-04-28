/**
 * Converts a thrown API error into a human-readable string.
 *
 * Covers:
 *  - Network failures (no err.status)
 *  - 400 Bad Request — field-level or detail message
 *  - 402 Payment Required — daily free limit reached
 *  - 404 Not Found
 *  - 429 Too Many Requests — includes Retry-After seconds when available
 *  - All other HTTP errors
 */
export function parseApiError(err) {
  // Network / fetch failure
  if (!err.status) {
    return 'Network error. Check your connection and try again.'
  }

  if (err.status === 402) {
    return err.data?.detail ?? "You've used all your free jobs for today. Purchase credits to continue."
  }

  if (err.status === 429) {
    const wait = err.retryAfter
    return wait
      ? `Too many requests. Please try again in ${wait} seconds.`
      : 'Too many requests. Please wait a moment and try again.'
  }

  if (err.status === 404) {
    return 'Job not found. It may have expired or been created in a different session.'
  }

  if (err.status === 400) {
    const data = err.data
    if (!data) return 'Invalid request. Please check your inputs.'
    if (typeof data.detail === 'string') return data.detail
    // Field-level errors — flatten to a readable string
    const messages = Object.entries(data)
      .map(([field, msgs]) => {
        const text = Array.isArray(msgs) ? msgs.join(' ') : String(msgs)
        return `${field}: ${text}`
      })
      .join(' · ')
    return messages || 'Invalid request. Please check your inputs.'
  }

  return err.data?.detail ?? err.data?.error ?? 'Something went wrong. Please try again.'
}

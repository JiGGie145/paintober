import { onUnmounted } from 'vue'
import { useJobStore } from '../stores/jobStore.js'
import { getJob } from '../api/jobs.js'

const POLL_INTERVAL_MS = 5000
const TERMINAL_STATUSES = ['done', 'failed']

/**
 * Polls the active job every 5 seconds until it reaches a terminal status.
 * Safe to call from any component — clears its interval on unmount.
 *
 * Usage:
 *   const { start, stop } = useJobPoller()
 *   start()
 */
export function useJobPoller() {
  const jobStore = useJobStore()
  let intervalId = null

  function stop() {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  function start() {
    stop() // clear any previous interval before starting

    intervalId = setInterval(async () => {
      if (!jobStore.id) {
        stop()
        return
      }

      try {
        const job = await getJob(jobStore.id)
        jobStore.setFromStatusResponse(job)

        if (TERMINAL_STATUSES.includes(job.status)) {
          stop()
        }
      } catch (err) {
        // Surface the error in the store but keep polling for transient failures
        jobStore.error = err.message ?? 'Polling error'

        // Stop on 404 — job no longer accessible
        if (err.status === 404) {
          stop()
        }
      }
    }, POLL_INTERVAL_MS)
  }

  // Always clean up when the component using this composable is unmounted
  onUnmounted(stop)

  return { start, stop }
}

import { defineStore } from 'pinia'
import { listJobs } from '../api/jobs.js'

/**
 * Tracks the full job history for the current session.
 */
export const useHistoryStore = defineStore('history', {
  state: () => ({
    /** @type {Array<{ id: string, status: string, created_at: string, updated_at: string }>} */
    jobs: [],
    loading: false,
    /** @type {string|null} */
    error: null,
  }),

  actions: {
    async fetchHistory() {
      this.loading = true
      this.error = null
      try {
        this.jobs = await listJobs()
      } catch (err) {
        this.error = err.message ?? 'Failed to load history'
      } finally {
        this.loading = false
      }
    },
  },
})

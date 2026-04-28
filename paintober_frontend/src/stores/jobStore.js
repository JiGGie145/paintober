import { defineStore } from 'pinia'

/**
 * Tracks the active job the user is currently working with.
 */
export const useJobStore = defineStore('job', {
  state: () => ({
    /** @type {string|null} */
    id: null,
    /** @type {'pending'|'processing'|'done'|'failed'|null} */
    status: null,
    /** @type {{ outline: string, color: string, palette: string, zip: string }|null} */
    downloadUrls: null,
    /** @type {string|null} */
    error: null,
    /** @type {object|null} Pipeline params echo'd back by the API */
    parameters: null,
  }),

  actions: {
    setFromCreateResponse({ job_id, status }) {
      this.id = job_id
      this.status = status
      this.downloadUrls = null
      this.error = null
      this.parameters = null
    },

    setFromStatusResponse(job) {
      this.id = job.id
      this.status = job.status
      this.downloadUrls = job.download_urls ?? null
      this.error = job.error_message ?? null
      this.parameters = job.parameters ?? null
    },

    reset() {
      this.id = null
      this.status = null
      this.downloadUrls = null
      this.error = null
      this.parameters = null
    },
  },
})

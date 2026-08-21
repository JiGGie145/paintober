import { defineStore } from 'pinia'
import { enterEvent, resolveEvent } from '../api/events.js'

const STORAGE_KEY = 'paintober_event_context'

export const useEventContextStore = defineStore('eventContext', {
  state: () => ({ event: null, attendeeId: null, token: null, loading: false, error: null }),
  getters: { isActive: (state) => Boolean(state.event && state.attendeeId) },
  actions: {
    restore() {
      try { Object.assign(this, JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? '{}')) } catch { this.clear() }
    },
    async resolve(token) { this.loading = true; this.error = null; try { this.event = await resolveEvent(token); this.token = token; return this.event } catch (error) { this.error = error; throw error } finally { this.loading = false } },
    async enter(phoneNumber) { this.loading = true; this.error = null; try { const result = await enterEvent({ event_token: this.token, phone_number: phoneNumber }); this.event = result.event; this.attendeeId = result.attendee_id; sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ event: this.event, attendeeId: this.attendeeId, token: this.token })); return result } catch (error) { this.error = error; throw error } finally { this.loading = false } },
    clear() { this.event = null; this.attendeeId = null; this.token = null; sessionStorage.removeItem(STORAGE_KEY) },
  },
})
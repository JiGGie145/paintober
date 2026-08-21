import { defineStore } from 'pinia'
import { getCurrentOrganizer, login, logout, register } from '../api/auth.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({ organizer: null, loading: false, hydrated: false, error: null }),
  getters: { isAuthenticated: (state) => Boolean(state.organizer) },
  actions: {
    async hydrate() {
      try { this.organizer = await getCurrentOrganizer() } catch { this.organizer = null } finally { this.hydrated = true }
    },
    async signIn(payload) { this.loading = true; this.error = null; try { this.organizer = await login(payload); return this.organizer } catch (error) { this.error = error; throw error } finally { this.loading = false } },
    async signUp(payload) { this.loading = true; this.error = null; try { this.organizer = await register(payload); return this.organizer } catch (error) { this.error = error; throw error } finally { this.loading = false } },
    async signOut() { await logout(); this.organizer = null },
  },
})
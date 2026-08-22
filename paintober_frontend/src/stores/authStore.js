import { defineStore } from 'pinia'
import { getCurrentOrganizer, login, logout, refresh, register } from '../api/auth.js'
import { clearTokens, getRefreshToken } from '../api/authTokens.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({ organizer: null, loading: false, hydrated: false, error: null }),
  getters: { isAuthenticated: (state) => Boolean(state.organizer) },
  actions: {
    async hydrate() {
      try {
        if (getRefreshToken()) await refresh()
        this.organizer = await getCurrentOrganizer()
      } catch {
        clearTokens()
        this.organizer = null
      } finally { this.hydrated = true }
    },
    async signIn(payload) { this.loading = true; this.error = null; try { this.organizer = await login(payload); return this.organizer } catch (error) { this.error = error; throw error } finally { this.loading = false } },
    async signUp(payload) { this.loading = true; this.error = null; try { this.organizer = await register(payload); return this.organizer } catch (error) { this.error = error; throw error } finally { this.loading = false } },
    async signOut() { try { await logout() } finally { clearTokens(); this.organizer = null } },
  },
})
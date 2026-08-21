import { apiFetch } from './jobs.js'

export const register = (payload) => apiFetch('/auth/register/', { method: 'POST', body: JSON.stringify(payload) })
export const login = (payload) => apiFetch('/auth/login/', { method: 'POST', body: JSON.stringify(payload) })
export const logout = () => apiFetch('/auth/logout/', { method: 'POST' })
export const getCurrentOrganizer = () => apiFetch('/auth/me/')
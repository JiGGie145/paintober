import { apiFetch } from './jobs.js'

export const resolveEvent = (token) => apiFetch(`/events/resolve/${encodeURIComponent(token)}/`)
export const enterEvent = (payload) => apiFetch('/events/enter/', { method: 'POST', body: JSON.stringify(payload) })
export const listOrganizerEvents = () => apiFetch('/events/mine/')
export const getOrganizerEvent = (id) => apiFetch(`/events/mine/${id}/`)
export const getOrganizerEventKits = (id) => apiFetch(`/events/mine/${id}/kits/`)
export const createOrganizerEvent = (payload) => apiFetch('/events/mine/', { method: 'POST', body: JSON.stringify(payload) })
export const updateOrganizerEvent = (id, payload) => apiFetch(`/events/mine/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) })
export const getCreditBalance = () => apiFetch('/events/credits/')
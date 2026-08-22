import { apiFetch } from './jobs.js'
import { clearTokens, getRefreshToken, refreshAccessToken, setTokens } from './authTokens.js'

export const register = async (payload) => {
	const response = await apiFetch('/auth/register/', { method: 'POST', body: JSON.stringify(payload), skipAuthRefresh: true })
	setTokens(response)
	return response.organizer
}

export const login = async (payload) => {
	const response = await apiFetch('/auth/login/', { method: 'POST', body: JSON.stringify(payload), skipAuthRefresh: true })
	setTokens(response)
	return response.organizer
}

export const refresh = refreshAccessToken

export const logout = async () => {
	const response = await apiFetch('/auth/logout/', {
		method: 'POST',
		body: JSON.stringify({ refresh: getRefreshToken() }),
		skipAuthRefresh: true,
	})
	clearTokens()
	return response
}

export const getCurrentOrganizer = () => apiFetch('/auth/me/')
import { readSessionToken } from './session'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

async function request(path, options = {}) {
  const token = readSessionToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const error = new Error(payload.detail || `Request failed (${response.status})`)
    error.status = response.status
    throw error
  }
  return payload
}

export function getLanguages() {
  return request('/languages')
}

export function runCode(problemId, submission) {
  return request(`/problems/${problemId}/run`, { method: 'POST', body: JSON.stringify(submission) })
}

export function submitCode(problemId, submission) {
  return request(`/problems/${problemId}/submit`, { method: 'POST', body: JSON.stringify(submission) })
}

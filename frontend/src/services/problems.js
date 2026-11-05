const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

export async function fetchProblem(problemId, { signal } = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}/problems/${encodeURIComponent(problemId)}`, {
async function getJson(path, { signal } = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: 'application/json' },
      signal,
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('Could not reach the problem service. Check your connection and try again.')
  }

  if (!response.ok) {
    let message = response.status === 404
      ? 'This problem could not be found or is no longer published.'
      : `The problem could not be loaded (${response.status}).`
    throw new Error('Could not reach the problem library. Check your connection and try again.')
  }

  if (!response.ok) {
    let message = `The problem library could not be loaded (${response.status}).`
    try {
      const payload = await response.json()
      if (typeof payload.detail === 'string') message = payload.detail
    } catch {
      // Keep the status-based message if the API response is not JSON.
    }
    const error = new Error(message)
    error.status = response.status
    throw error
      // Keep the status-based message when the API response is not JSON.
    }
    throw new Error(message)
  }

  return response.json()
}

export function fetchProblems({ search, difficulty, tag, offset, limit, signal }) {
  const params = new URLSearchParams()
  if (search) params.set('q', search)
  if (difficulty) params.set('difficulty', difficulty)
  if (tag) params.set('tag', tag)
  params.set('offset', String(offset))
  params.set('limit', String(limit))
  return getJson(`/problems?${params.toString()}`, { signal })
}

export function fetchProblemTags({ signal } = {}) {
  return getJson('/tags', { signal })
}

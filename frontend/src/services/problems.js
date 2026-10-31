const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

export async function fetchProblem(problemId, { signal } = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}/problems/${encodeURIComponent(problemId)}`, {
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
    try {
      const payload = await response.json()
      if (typeof payload.detail === 'string') message = payload.detail
    } catch {
      // Keep the status-based message if the API response is not JSON.
    }
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return response.json()
}

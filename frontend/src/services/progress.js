const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
const SESSION_KEY = 'codestreak-session'

export function readSession() {
  try {
    const session = JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null')
    return session?.accessToken ? session : null
  } catch {
    return null
  }
}

async function request(path, options = {}) {
  const token = readSession()?.accessToken
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (!response.ok) {
    let message = `Could not load progress (${response.status}).`
    try {
      const payload = await response.json()
      if (typeof payload.detail === 'string') message = payload.detail
    } catch {
      // Keep the status message for non-JSON errors.
    }
    const error = new Error(message)
    error.status = response.status
    throw error
  }
  return response.status === 204 ? null : response.json()
}

export function getProgressSummary() {
  return request('/progress/summary')
}

export function getActivity(startDate, endDate) {
  const query = new URLSearchParams({ start_date: startDate, end_date: endDate })
  return request(`/progress/activity?${query}`)
}

export function getAttempts() {
  return request('/attempts?offset=0&limit=6')
}

export function getTodayPlan(today) {
  const query = new URLSearchParams({ start_date: today, end_date: today })
  return request(`/plans?${query}`)
}

export function saveDailyGoal(today, dailyGoal) {
  return request(`/plans/${today}`, {
    method: 'PUT',
    body: JSON.stringify({ daily_goal: dailyGoal }),
  })
}

export function getNextRecommendation() {
  return request('/recommendations/next')
}

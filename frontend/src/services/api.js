const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
export const SESSION_KEY = 'codestreak-session'

function readSession() {
  try {
    const sharedSession = localStorage.getItem(SESSION_KEY)
    if (sharedSession) return JSON.parse(sharedSession)

    // Migrate sessions created before authentication was shared between tabs.
    const previousSession = sessionStorage.getItem(SESSION_KEY)
    if (!previousSession) return null
    const session = JSON.parse(previousSession)
    if (session?.accessToken && session?.user?.user_id) {
      localStorage.setItem(SESSION_KEY, JSON.stringify(session))
      sessionStorage.removeItem(SESSION_KEY)
    }
    return session
  } catch {
    return null
  }
}

export function getSession() {
  const session = readSession()
  if (!session?.accessToken || !session?.user?.user_id) return null
  return session
}

export function signOut() {
  localStorage.removeItem(SESSION_KEY)
  sessionStorage.removeItem(SESSION_KEY)
}

export async function apiRequest(path, options = {}) {
  const session = getSession()
  const headers = new Headers(options.headers)
  headers.set('Accept', 'application/json')
  if (options.body != null) headers.set('Content-Type', 'application/json')
  if (session?.accessToken) headers.set('Authorization', `Bearer ${session.accessToken}`)

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('Unable to reach CodeStreak. Check your connection and try again.')
  }

  if (!response.ok) {
    let message = `Request failed (${response.status}). Please try again.`
    try {
      const payload = await response.json()
      if (typeof payload.detail === 'string') message = payload.detail
      else if (Array.isArray(payload.detail)) message = 'Please check your email and password.'
    } catch {
      // Keep the response-status message when the server does not return JSON.
    }
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return response.status === 204 ? null : response.json()
}

function saveSession(result) {
  if (!result?.access_token || !result?.user?.user_id) {
    throw new Error('The authentication response was incomplete. Please try again.')
  }
  const session = {
    accessToken: result.access_token,
    user: result.user,
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
  sessionStorage.removeItem(SESSION_KEY)
  return session
}

export async function signIn(email, password) {
  const result = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  return saveSession(result)
}

export async function createAccount({ name, email, password, timezone }) {
  const result = await apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name,
      email,
      password,
      timezone,
      consent_status: 'accepted',
    }),
  })
  return saveSession(result)
}

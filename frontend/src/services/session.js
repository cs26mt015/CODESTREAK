const SESSION_KEY = 'codestreak-session'

export function readSessionToken() {
  try {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY) || sessionStorage.getItem(SESSION_KEY) || 'null')
    return session?.accessToken || session?.access_token || ''
  } catch {
    return ''
  }
}

export function saveSessionToken(token) {
  let session = {}
  try {
    session = JSON.parse(localStorage.getItem(SESSION_KEY) || sessionStorage.getItem(SESSION_KEY) || '{}')
  } catch {
    // Replace malformed stored data with the supplied token.
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify({ ...session, accessToken: token }))
  sessionStorage.removeItem(SESSION_KEY)
}

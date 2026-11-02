const SESSION_KEY = 'codestreak-session'

export function readSessionToken() {
  try {
    const session = JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null')
    return session?.accessToken || session?.access_token || ''
  } catch {
    return ''
  }
}

export function saveSessionToken(token) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ accessToken: token }))
}

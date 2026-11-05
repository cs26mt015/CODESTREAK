import { useEffect, useState } from 'react'
import AdminStudio from './pages/AdminStudio'
import CodeEditor from './pages/CodeEditor'
import ProblemDetail from './pages/ProblemDetail'
import Problems from './pages/Problems'
import ProgressDashboard from './pages/ProgressDashboard'
import Register from './pages/Register'
import SignIn from './pages/SignIn'
import { getSession, SESSION_KEY, signOut } from './services/api'

function getRoute() {
  const path = window.location.pathname.replace(/\/$/, '') || '/'
  const editor = path.match(/^\/problems\/(\d+)\/solve$/)
  if (editor) return { page: 'editor', problemId: Number(editor[1]) }
  const detail = path.match(/^\/problems\/(\d+)$/)
  if (detail) return { page: 'detail', problemId: Number(detail[1]) }
  if (path === '/problems') return { page: 'problems' }
  if (path === '/admin' || path === '/admin/problems') return { page: 'admin' }
  if (path === '/sign-in') return { page: 'sign-in' }
  if (path === '/register') return { page: 'register' }
  const adminEditor = path.match(/^\/admin\/problems\/(new|\d+)$/)
  if (adminEditor) return { page: 'admin-editor', problemId: adminEditor[1] === 'new' ? null : Number(adminEditor[1]) }
  return path === '/' ? { page: 'home' } : { page: 'not-found' }
}

export default function App() {
  const [session, setSession] = useState(getSession)
  const [authPage, setAuthPage] = useState(window.location.pathname === '/register' ? 'register' : 'sign-in')
  const route = getRoute()
  const isAdmin = session?.user?.role === 'admin'

  useEffect(() => {
    function syncSession(event) {
      if (event.key === SESSION_KEY) setSession(getSession())
    }
    window.addEventListener('storage', syncSession)
    return () => window.removeEventListener('storage', syncSession)
  }, [])

  function switchAuthPage(page) {
    setAuthPage(page)
    window.history.pushState({}, '', page === 'register' ? '/register' : '/sign-in')
  }

  function handleAuthentication(nextSession) {
    setSession(nextSession)
    if (route.page === 'sign-in' || route.page === 'register') window.history.replaceState({}, '', '/')
  }

  function handleSignOut() {
    signOut()
    setSession(null)
    setAuthPage('sign-in')
    window.history.replaceState({}, '', '/')
  }

  if (route.page === 'sign-in' || route.page === 'register') {
    if (session) return isAdmin ? <AdminStudio onSignOut={handleSignOut} /> : <ProgressDashboard onSignOut={handleSignOut} />
    return authPage === 'register'
      ? <Register onRegistered={handleAuthentication} onSignInRequested={() => switchAuthPage('sign-in')} />
      : <SignIn onSignedIn={handleAuthentication} onRegisterRequested={() => switchAuthPage('register')} />
  }

  if (route.page === 'problems') return <Problems />
  if (route.page === 'detail') return <ProblemDetail problemId={route.problemId} />

  if (route.page === 'home') {
    if (!session) return <SignIn onSignedIn={handleAuthentication} onRegisterRequested={() => switchAuthPage('register')} />
    return isAdmin ? <AdminStudio onSignOut={handleSignOut} /> : <ProgressDashboard onSignOut={handleSignOut} />
  }

  if (route.page === 'admin' || route.page === 'admin-editor') {
    if (!session) return <SignIn onSignedIn={handleAuthentication} onRegisterRequested={() => switchAuthPage('register')} />
    if (!isAdmin) return <AccessDenied />
    return <AdminStudio problemId={route.problemId} onSignOut={handleSignOut} />
  }

  if (route.page === 'editor') {
    if (!session) return <SignIn onSignedIn={handleAuthentication} onRegisterRequested={() => switchAuthPage('register')} />
    if (isAdmin) return <AccessDenied />
    return <CodeEditor problemId={route.problemId} />
  }

  return <main className="not-found"><h1>Page not found</h1><a href="/">Back to CodeStreak</a></main>
}

function AccessDenied() {
  return <main className="access-denied"><div><span aria-hidden="true">!</span><p className="eyebrow">ACCESS RESTRICTED</p><h1>You don’t have access to this page.</h1><p>Use an account with the required role, or return to CodeStreak.</p><a href="/">Go to home</a></div></main>
}

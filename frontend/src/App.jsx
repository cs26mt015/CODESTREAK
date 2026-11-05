import ProgressDashboard from './pages/ProgressDashboard'

export default function App() {
  return <ProgressDashboard />
import ProblemDetail from './pages/ProblemDetail'
import CodeEditor from './pages/CodeEditor'

function getProblemId() {
  const pathMatch = window.location.pathname.match(/^\/problems\/(\d+)(?:\/solve)?\/?$/)
  const queryId = new URLSearchParams(window.location.search).get('id')
  const value = pathMatch?.[1] || queryId || '1'
  const problemId = Number(value)
  return Number.isInteger(problemId) && problemId > 0 ? problemId : null
}

export default function App() {
  if (/^\/problems\/\d+\/solve\/?$/.test(window.location.pathname)) {
    return <CodeEditor problemId={getProblemId()} />
  }
  return <ProblemDetail problemId={getProblemId()} />
}
import Problems from './pages/Problems'

export default function App() {
  return <Problems />
import { useState } from 'react'
import Register from './pages/Register'
import SignIn from './pages/SignIn'
import { getSession, signOut } from './services/api'

export default function App() {
  const [session, setSession] = useState(getSession)
  const [authPage, setAuthPage] = useState('sign-in')

  function handleSignOut() {
    signOut()
    setSession(null)
  }

  if (!session) {
    if (authPage === 'register') {
      return <Register onRegistered={setSession} onSignInRequested={() => setAuthPage('sign-in')} />
    }
    return <SignIn onSignedIn={setSession} onRegisterRequested={() => setAuthPage('register')} />
  }

  return (
    <main className="signed-in-page">
      <section className="signed-in-card" aria-labelledby="signed-in-title">
        <a className="brand" href="/" aria-label="CodeStreak home">
          <span className="brand-mark" aria-hidden="true">{'{ }'}</span>
          <span>code<span className="brand-accent">streak</span></span>
        </a>
        <div className="signed-in-check" aria-hidden="true">✓</div>
        <p className="eyebrow">SIGNED IN</p>
        <h1 id="signed-in-title">Welcome, {session.user.name}.</h1>
        <p className="signed-in-copy">You’re signed in to CodeStreak as {session.user.email}.</p>
        <button className="button button-secondary sign-out-button" onClick={handleSignOut}>
          Sign out
        </button>
      </section>
    </main>
  )
}

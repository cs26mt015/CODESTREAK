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

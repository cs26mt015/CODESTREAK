import { useState } from 'react'
import { signIn } from '../services/api'

export default function SignIn({ onSignedIn }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const session = await signIn(email.trim(), password)
      onSignedIn(session)
    } catch (requestError) {
      setError(requestError.message || 'Sign-in failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-shell" aria-label="Sign in to CodeStreak">
        <aside className="auth-story">
          <a className="brand brand-light" href="/" aria-label="CodeStreak">
            <span className="brand-mark" aria-hidden="true">{'{ }'}</span>
            <span>code<span className="brand-accent">streak</span></span>
          </a>
          <div className="story-content">
            <p className="story-kicker">YOUR PRACTICE SPACE</p>
            <h1>Build skill<br />one problem<br />at a time.</h1>
            <p className="story-description">
              Sign in to continue your coding practice and keep your progress together.
            </p>
            <div className="practice-preview" aria-hidden="true">
              <div className="preview-topline"><span /><span /><span /><i>daily-practice.cpp</i></div>
              <div className="preview-code"><b>01</b><span>int</span> main() {'{'}</div>
              <div className="preview-code"><b>02</b>&nbsp;&nbsp;keep_learning();</div>
              <div className="preview-code"><b>03</b>{'}'}</div>
              <div className="preview-footer"><span>●</span> Ready for today's challenge</div>
            </div>
          </div>
          <p className="story-footer">CodeStreak <span>·</span> Practice smarter</p>
        </aside>

        <div className="auth-form-side">
          <div className="auth-mobile-brand" aria-hidden="true">
            <span className="brand-mark">{'{ }'}</span> code<span className="brand-accent">streak</span>
          </div>
          <div className="auth-form-wrap">
            <p className="eyebrow">WELCOME BACK</p>
            <h2>Sign in to your account</h2>
            <p className="form-intro">Enter your account details to continue.</p>

            <form className="sign-in-form" onSubmit={handleSubmit}>
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                inputMode="email"
                maxLength={320}
                placeholder="you@example.com"
                value={email}
                onChange={event => setEmail(event.target.value)}
                required
                disabled={isSubmitting}
              />

              <div className="password-label-row">
                <label htmlFor="password">Password</label>
              </div>
              <div className="password-field">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  maxLength={128}
                  placeholder="Enter your password"
                  value={password}
                  onChange={event => setPassword(event.target.value)}
                  required
                  disabled={isSubmitting}
                />
                <button
                  className="password-toggle"
                  type="button"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  aria-pressed={showPassword}
                  onClick={() => setShowPassword(value => !value)}
                  disabled={isSubmitting}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              {error && <p className="form-error" role="alert">{error}</p>}

              <button className="button button-primary submit-button" type="submit" disabled={isSubmitting}>
                {isSubmitting ? <><span className="button-spinner" aria-hidden="true" /> Signing in…</> : 'Sign in'}
              </button>
            </form>

            <p className="auth-note">Your account is protected with secure sign-in.</p>
          </div>
          <p className="form-side-footer">© 2026 CodeStreak</p>
        </div>
      </section>
    </main>
  )
}

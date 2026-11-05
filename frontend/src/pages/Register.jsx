import { useState } from 'react'
import { createAccount } from '../services/api'

export default function Register({ onRegistered, onSignInRequested }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [timezone, setTimezone] = useState('Asia/Kolkata')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [consent, setConsent] = useState(false)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (password.length < 12) {
      setError('Use at least 12 characters for your password.')
      return
    }
    if (password !== confirmPassword) {
      setError('The passwords do not match.')
      return
    }

    setIsSubmitting(true)
    try {
      const session = await createAccount({
        name: name.trim(),
        email: email.trim(),
        password,
        timezone: timezone.trim(),
      })
      onRegistered(session)
    } catch (requestError) {
      setError(requestError.message || 'Account creation failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-shell" aria-label="Create a CodeStreak account">
        <aside className="auth-story">
          <a className="brand brand-light" href="/" aria-label="CodeStreak">
            <span className="brand-mark" aria-hidden="true">{'{ }'}</span>
            <span>code<span className="brand-accent">streak</span></span>
          </a>
          <div className="story-content">
            <p className="story-kicker">START YOUR PRACTICE</p>
            <h1>Make room<br />for your next<br />breakthrough.</h1>
            <p className="story-description">
              Create an account to keep your practice and progress in one place.
            </p>
            <div className="practice-preview" aria-hidden="true">
              <div className="preview-topline"><span /><span /><span /><i>daily-practice.cpp</i></div>
              <div className="preview-code"><b>01</b><span>int</span> main() {'{'}</div>
              <div className="preview-code"><b>02</b>&nbsp;&nbsp;start_small();</div>
              <div className="preview-code"><b>03</b>{'}'}</div>
              <div className="preview-footer"><span>●</span> Your next session starts here</div>
            </div>
          </div>
          <p className="story-footer">CodeStreak <span>·</span> Practice smarter</p>
        </aside>

        <div className="auth-form-side">
          <div className="auth-mobile-brand" aria-hidden="true">
            <span className="brand-mark">{'{ }'}</span> code<span className="brand-accent">streak</span>
          </div>
          <div className="auth-form-wrap">
            <p className="eyebrow">CREATE YOUR ACCOUNT</p>
            <h2>Start practicing</h2>
            <p className="form-intro">A few details and you’re ready to begin.</p>

            <form className="sign-in-form register-form" onSubmit={handleSubmit}>
              <label htmlFor="register-name">Name</label>
              <input
                id="register-name"
                name="name"
                type="text"
                autoComplete="name"
                maxLength={255}
                placeholder="Your name"
                value={name}
                onChange={event => setName(event.target.value)}
                required
                disabled={isSubmitting}
              />

              <label htmlFor="register-email">Email address</label>
              <input
                id="register-email"
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

              <label htmlFor="register-timezone">Time zone</label>
              <input
                id="register-timezone"
                name="timezone"
                type="text"
                autoComplete="off"
                maxLength={100}
                placeholder="Asia/Kolkata"
                value={timezone}
                onChange={event => setTimezone(event.target.value)}
                required
                disabled={isSubmitting}
              />
              <span className="field-help">Use an IANA time zone, such as Asia/Kolkata or UTC.</span>

              <label htmlFor="register-password">Password</label>
              <div className="password-field">
                <input
                  id="register-password"
                  name="new-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  minLength={12}
                  maxLength={128}
                  placeholder="At least 12 characters"
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

              <label htmlFor="confirm-password">Confirm password</label>
              <input
                id="confirm-password"
                name="confirm-password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                minLength={12}
                maxLength={128}
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={event => setConfirmPassword(event.target.value)}
                required
                disabled={isSubmitting}
              />

              <label className="consent-field" htmlFor="account-consent">
                <input
                  id="account-consent"
                  name="consent"
                  type="checkbox"
                  checked={consent}
                  onChange={event => setConsent(event.target.checked)}
                  required
                  disabled={isSubmitting}
                />
                <span>I consent to creating and maintaining my CodeStreak account.</span>
              </label>

              {error && <p className="form-error" role="alert">{error}</p>}

              <button className="button button-primary submit-button" type="submit" disabled={isSubmitting}>
                {isSubmitting ? <><span className="button-spinner" aria-hidden="true" /> Creating account…</> : 'Create account'}
              </button>
            </form>

            <p className="auth-switch">
              Already have an account?{' '}
              <button type="button" onClick={onSignInRequested}>Sign in</button>
            </p>
          </div>
          <p className="form-side-footer">© 2026 CodeStreak</p>
        </div>
      </section>
    </main>
  )
}

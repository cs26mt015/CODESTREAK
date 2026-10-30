import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  getActivity,
  getAttempts,
  getNextRecommendation,
  getProgressSummary,
  getTodayPlan,
  readSession,
  saveDailyGoal,
} from '../services/progress'
import './ProgressDashboard.css'

export default function ProgressDashboard() {
  const [session, setSession] = useState(readSession)
  const [summary, setSummary] = useState(null)
  const [activity, setActivity] = useState([])
  const [attempts, setAttempts] = useState([])
  const [recommendation, setRecommendation] = useState(null)
  const [todayPlan, setTodayPlan] = useState(null)
  const [goalInput, setGoalInput] = useState('')
  const [isLoading, setIsLoading] = useState(Boolean(session))
  const [isSavingGoal, setIsSavingGoal] = useState(false)
  const [error, setError] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const timezone = session?.user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  const today = useMemo(() => todayInTimezone(timezone), [timezone])

  const loadDashboard = useCallback(async () => {
    if (!readSession()) {
      setIsLoading(false)
      setSummary(null)
      return
    }
    setIsLoading(true)
    setError('')
    const activityStart = startOfActivityWindow(today)
    try {
      const [nextSummary, nextActivity, nextAttempts, nextPlan, nextRecommendation] = await Promise.all([
        getProgressSummary(),
        getActivity(activityStart, today),
        getAttempts(),
        getTodayPlan(today),
        getNextRecommendation(),
      ])
      setSummary(nextSummary)
      setActivity(nextActivity)
      setAttempts(nextAttempts.items || [])
      setTodayPlan(nextPlan[0] || null)
      setRecommendation(nextRecommendation)
      setGoalInput(String(nextPlan[0]?.daily_goal || nextSummary.daily_goal || ''))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsLoading(false)
    }
  }, [today])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard, refreshKey])

  function syncSession() {
    setSession(readSession())
    setRefreshKey(value => value + 1)
  }

  async function handleGoalSave(event) {
    event.preventDefault()
    const dailyGoal = Number(goalInput)
    if (!Number.isInteger(dailyGoal) || dailyGoal < 1 || dailyGoal > 1000) {
      setError('Choose a daily goal from 1 to 1000 problems.')
      return
    }
    setIsSavingGoal(true)
    setError('')
    try {
      const plan = await saveDailyGoal(today, dailyGoal)
      setTodayPlan(plan)
      setSummary(value => value ? { ...value, daily_goal: plan.daily_goal } : value)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSavingGoal(false)
    }
  }

  if (!session) {
    return <SignInRequired onSessionChanged={syncSession} />
  }

  const completed = summary?.completed_today || 0
  const dailyGoal = summary?.daily_goal || todayPlan?.daily_goal || 0
  const goalPercent = dailyGoal ? Math.min(100, Math.round((completed / dailyGoal) * 100)) : 0

  return (
    <div className="progress-app">
      <header className="progress-topbar">
        <a className="progress-brand" href="/" aria-label="CodeStreak home">
          <span className="progress-brand-mark" aria-hidden="true">{'{ }'}</span>
          <span>code<span>streak</span></span>
        </a>
        <nav className="progress-nav" aria-label="Main navigation">
          <a className="active" href="/">Overview</a>
          <a href="/problems">Problems</a>
        </nav>
        <div className="progress-user">
          <span className="user-avatar" aria-hidden="true">{initials(session.user?.name)}</span>
          <span className="progress-user-name">{session.user?.name || 'Learner'}</span>
        </div>
      </header>

      <main className="progress-main">
        <div className="progress-heading">
          <div>
            <p className="progress-eyebrow">YOUR LEARNING JOURNEY</p>
            <h1>Progress overview</h1>
            <p className="progress-subtitle">A clear view of the practice you’ve put in.</p>
          </div>
          <button className="refresh-button" type="button" onClick={() => setRefreshKey(value => value + 1)} disabled={isLoading}>
            <span aria-hidden="true">↻</span> Refresh
          </button>
        </div>

        {error && (
          <div className="progress-alert" role="alert">
            <span>{error}</span>
            <button type="button" onClick={() => setRefreshKey(value => value + 1)}>Try again</button>
          </div>
        )}

        {isLoading && !summary ? <DashboardLoading /> : summary ? (
          <>
            <section className="progress-stat-grid" aria-label="Progress summary">
              <StatCard label="Problems solved" value={summary.total_solved} detail="Across all topics" accent="violet" icon="✓" />
              <StatCard label="Current streak" value={summary.current_streak} detail={summary.current_streak === 1 ? 'day in a row' : 'days in a row'} accent="orange" icon="↗" />
              <StatCard label="Longest streak" value={summary.longest_streak} detail="Your personal best" accent="blue" icon="⌁" />
              <StatCard label="Solved today" value={completed} detail={dailyGoal ? `Daily goal: ${dailyGoal}` : 'Set a daily goal'} accent="green" icon="◎" />
            </section>

            <section className="progress-primary-grid">
              <div className="progress-panel activity-panel">
                <div className="panel-heading">
                  <div><h2>Activity</h2><p>Daily practice over the last year</p></div>
                  <span className="activity-total">{activity.filter(day => day.problems_attempted > 0).length} active days</span>
                </div>
                <ActivityHeatmap activity={activity} endDate={today} timezone={timezone} />
                <div className="heatmap-legend"><span>Less</span>{[0, 1, 2, 4, 7].map(level => <i key={level} className={`heat-level level-${level}`} />)}<span>More</span></div>
              </div>

              <div className="progress-panel daily-goal-panel">
                <div className="panel-heading"><div><h2>Daily goal</h2><p>Build a steady routine</p></div><span className="goal-icon" aria-hidden="true">◎</span></div>
                <div className="goal-ring-wrap">
                  <div className="goal-ring" style={{ '--goal-progress': `${goalPercent}%` }}>
                    <div><strong>{completed}<span> / {dailyGoal || '—'}</span></strong><small>solved today</small></div>
                  </div>
                </div>
                <form className="goal-form" onSubmit={handleGoalSave}>
                  <label htmlFor="daily-goal">Problems per day</label>
                  <div><input id="daily-goal" type="number" min="1" max="1000" value={goalInput} onChange={event => setGoalInput(event.target.value)} placeholder="e.g. 3" /><button type="submit" disabled={isSavingGoal}>{isSavingGoal ? 'Saving…' : 'Save goal'}</button></div>
                </form>
              </div>
            </section>

            <section className="progress-secondary-grid">
              <div className="progress-panel breakdown-panel">
                <div className="panel-heading"><div><h2>By difficulty</h2><p>Solved problems in each level</p></div></div>
                <Breakdown items={summary.by_difficulty} palette="difficulty" empty="Solve a problem to see your breakdown." />
              </div>
              <div className="progress-panel breakdown-panel">
                <div className="panel-heading"><div><h2>By topic</h2><p>Your strongest areas so far</p></div></div>
                <Breakdown items={summary.by_topic} palette="topic" empty="Topic progress will appear as you solve tagged problems." />
              </div>
              <div className="progress-panel recommendation-panel">
                <div className="panel-heading"><div><h2>Recommended next</h2><p>Keep your momentum going</p></div><span className="recommendation-mark" aria-hidden="true">✦</span></div>
                {recommendation?.problem ? (
                  <a className="recommended-problem" href={`/problems/${recommendation.problem.problem_id}`}>
                    <span className="recommended-difficulty">{recommendation.problem.difficulty}</span>
                    <strong>{recommendation.problem.title}</strong>
                    <span className="recommended-cta">Open problem <b aria-hidden="true">→</b></span>
                  </a>
                ) : <p className="empty-copy">{recommendation?.message || 'No recommendation is available yet.'}</p>}
              </div>
            </section>

            <section className="progress-panel attempts-panel">
              <div className="panel-heading"><div><h2>Recent attempts</h2><p>Your latest practice activity</p></div><span className="attempt-count">{attempts.length} recent</span></div>
              {attempts.length ? <RecentAttempts attempts={attempts} /> : <p className="empty-copy">Your attempts will show here when you start practicing.</p>}
            </section>
          </>
        ) : null}
      </main>
    </div>
  )
}

function StatCard({ label, value, detail, accent, icon }) {
  return <article className={`progress-stat-card accent-${accent}`}><span className="stat-icon" aria-hidden="true">{icon}</span><p>{label}</p><strong>{value ?? 0}</strong><small>{detail}</small></article>
}

function ActivityHeatmap({ activity, endDate, timezone }) {
  const counts = new Map(activity.map(day => [day.local_date, day.problems_attempted]))
  const start = startOfActivityWindow(endDate)
  const days = []
  for (let date = parseDate(start); formatDate(date) <= endDate; date.setUTCDate(date.getUTCDate() + 1)) {
    const key = formatDate(date)
    days.push({ date: key, count: counts.get(key) || 0 })
  }
  const weeks = []
  for (let index = 0; index < days.length; index += 7) weeks.push(days.slice(index, index + 7))
  const monthLabels = weeks.map(week => week[0] ? parseDate(week[0].date).toLocaleDateString('en', { month: 'short', timeZone: 'UTC' }) : '')
  return (
    <div className="heatmap-scroll" role="img" aria-label={`Practice activity heatmap in ${timezone}`}>
      <div className="heatmap-months">{monthLabels.map((month, index) => <span key={`${month}-${index}`}>{index === 0 || month !== monthLabels[index - 1] ? month : ''}</span>)}</div>
      <div className="heatmap-body"><div className="heatmap-weekdays"><span>Mon</span><span>Wed</span><span>Fri</span></div><div className="heatmap-weeks">{weeks.map((week, index) => <div className="heatmap-week" key={index}>{week.map(day => <span key={day.date} className={`heat-cell ${heatLevel(day.count)}`} title={`${day.count} attempted · ${day.date}`} />)}</div>)}</div></div>
    </div>
  )
}

function Breakdown({ items = [], palette, empty }) {
  if (!items.length) return <p className="empty-copy">{empty}</p>
  const maximum = Math.max(...items.map(item => item.solved), 1)
  const sortedItems = [...items].sort((left, right) => right.solved - left.solved)
  return <div className={`breakdown-list ${palette}`}>{sortedItems.slice(0, 6).map(item => <div className={`breakdown-row ${palette === 'difficulty' ? `difficulty-${normalize(item.name)}` : ''}`} key={item.name}><div><span>{item.name}</span><strong>{item.solved}</strong></div><i><b style={{ width: `${Math.max(5, (item.solved / maximum) * 100)}%` }} /></i></div>)}</div>
}

function RecentAttempts({ attempts }) {
  return <div className="attempt-list">{attempts.map(attempt => {
    const accepted = ['accepted', 'solved'].includes((attempt.verdict || '').toLowerCase())
    return <a className="attempt-row" href={`/problems/${attempt.problem_id}`} key={attempt.attempt_id}>
      <span className={`attempt-status ${accepted ? 'passed' : 'not-passed'}`} aria-label={accepted ? 'Passed' : 'Attempted'}>{accepted ? '✓' : '↗'}</span>
      <span className="attempt-problem"><strong>Problem #{attempt.problem_id}</strong><small>{attempt.language}</small></span>
      <span className={`attempt-verdict ${accepted ? 'passed-text' : ''}`}>{attempt.verdict}</span>
      <time dateTime={attempt.attempted_at}>{formatAttemptDate(attempt.attempted_at)}</time>
      <span className="attempt-arrow" aria-hidden="true">→</span>
    </a>
  })}</div>
}

function SignInRequired({ onSessionChanged }) {
  return <main className="progress-auth-page"><section className="progress-auth-card"><a className="progress-brand" href="/" aria-label="CodeStreak home"><span className="progress-brand-mark">{'{ }'}</span><span>code<span>streak</span></span></a><span className="auth-lock" aria-hidden="true">↗</span><p className="progress-eyebrow">YOUR LEARNING JOURNEY</p><h1>Sign in to see your progress</h1><p>Your solved problems, practice streaks, and daily activity are private to your learner account.</p><button type="button" onClick={onSessionChanged}>Check sign-in</button></section></main>
}

function DashboardLoading() {
  return <div className="dashboard-loading" role="status" aria-label="Loading progress"><div className="loading-stat-grid">{[1, 2, 3, 4].map(item => <i key={item} />)}</div><i className="loading-large" /><i className="loading-large" /></div>
}

function todayInTimezone(timezone) {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: timezone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date())
  const values = Object.fromEntries(parts.map(part => [part.type, part.value]))
  return `${values.year}-${values.month}-${values.day}`
}

function startOfActivityWindow(today) {
  const end = parseDate(today)
  end.setUTCDate(end.getUTCDate() - 359)
  end.setUTCDate(end.getUTCDate() - ((end.getUTCDay() + 6) % 7))
  return formatDate(end)
}

function parseDate(value) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(Date.UTC(year, month - 1, day))
}

function formatDate(date) {
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`
}

function heatLevel(count) {
  if (count >= 7) return 'heat-4'
  if (count >= 4) return 'heat-3'
  if (count >= 2) return 'heat-2'
  if (count >= 1) return 'heat-1'
  return 'heat-0'
}

function initials(name = '') {
  return name.trim().split(/\s+/).slice(0, 2).map(part => part[0]?.toUpperCase()).join('') || 'L'
}

function normalize(value = '') {
  return value.toLowerCase().replace(/[^a-z0-9-]/g, '')
}

function formatAttemptDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

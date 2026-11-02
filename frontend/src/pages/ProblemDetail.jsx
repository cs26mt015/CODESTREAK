import { useEffect, useState } from 'react'
import { fetchProblem } from '../services/problems'

export default function ProblemDetail({ problemId }) {
  const [problem, setProblem] = useState(null)
  const [isLoading, setIsLoading] = useState(Boolean(problemId))
  const [error, setError] = useState(problemId ? '' : 'Enter a valid problem ID in the address bar.')
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    if (!problemId) {
      setProblem(null)
      setIsLoading(false)
      setError('Enter a valid problem ID in the address bar.')
      return undefined
    }

    const controller = new AbortController()
    setIsLoading(true)
    setError('')

    fetchProblem(problemId, { signal: controller.signal })
      .then(setProblem)
      .catch(requestError => {
        if (requestError.name !== 'AbortError') setError(requestError.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })

    return () => controller.abort()
  }, [problemId, retryCount])

  return (
    <div className="detail-app">
      <header className="detail-header">
        <a className="detail-brand" href="/" aria-label="CodeStreak">
          <span className="detail-brand-mark" aria-hidden="true">{'{ }'}</span>
          <span>code<span>streak</span></span>
        </a>
        <span className="header-divider" aria-hidden="true" />
        <span className="header-section">Problem detail</span>
      </header>

      <main className="detail-main">
        {isLoading ? (
          <DetailLoading />
        ) : error ? (
          <section className="detail-error" role="alert">
            <span className="detail-error-icon" aria-hidden="true">!</span>
            <p className="detail-eyebrow">PROBLEM DETAIL</p>
            <h1>We couldn’t load this problem.</h1>
            <p className="detail-error-copy">{error}</p>
            {problemId && (
              <button className="detail-retry" type="button" onClick={() => setRetryCount(value => value + 1)}>
                Try again
              </button>
            )}
          </section>
        ) : problem ? (
          <>
            <div className="detail-breadcrumb"><span>Problem library</span><span aria-hidden="true">/</span><strong>Problem #{problem.problem_id}</strong></div>
            <div className="detail-title-block">
              <div>
                <p className="detail-eyebrow">PROBLEM #{String(problem.problem_id).padStart(3, '0')}</p>
                <h1>{problem.title}</h1>
              </div>
              <span className={`detail-difficulty difficulty-${normalizeDifficulty(problem.difficulty)}`}>
                <i aria-hidden="true" />{problem.difficulty}
              </span>
            </div>
            <a className="open-editor-link" href={`/problems/${problem.problem_id}/solve`}>Open code editor <span aria-hidden="true">→</span></a>

            <div className="detail-layout">
              <div className="detail-content">
                <section className="detail-section" aria-labelledby="statement-title">
                  <div className="section-heading">
                    <span className="section-number">01</span>
                    <h2 id="statement-title">Problem statement</h2>
                  </div>
                  <div className="statement-copy">{problem.statement}</div>
                </section>

                {problem.constraints && (
                  <section className="detail-section" aria-labelledby="constraints-title">
                    <div className="section-heading">
                      <span className="section-number">02</span>
                      <h2 id="constraints-title">Constraints</h2>
                    </div>
                    <pre className="constraints-copy">{problem.constraints}</pre>
                  </section>
                )}

                {(problem.sample_input || problem.sample_output) && (
                  <section className="detail-section" aria-labelledby="examples-title">
                    <div className="section-heading">
                      <span className="section-number">{problem.constraints ? '03' : '02'}</span>
                      <h2 id="examples-title">Example</h2>
                    </div>
                    <div className="sample-grid">
                      <SampleBlock title="Input" value={problem.sample_input} />
                      <SampleBlock title="Output" value={problem.sample_output} />
                    </div>
                  </section>
                )}
              </div>

              <aside className="detail-sidebar" aria-label="Problem information">
                <section className="info-card">
                  <p className="info-card-title">Problem information</p>
                  <div className="info-row"><span>Difficulty</span><strong className={`text-${normalizeDifficulty(problem.difficulty)}`}>{problem.difficulty}</strong></div>
                  <div className="info-row"><span>Problem ID</span><strong>#{problem.problem_id}</strong></div>
                  <div className="info-divider" />
                  <p className="topic-heading">Topics</p>
                  {problem.tags?.length ? (
                    <div className="detail-topic-list">
                      {problem.tags.map(item => <span className="detail-topic" key={item.tag_id}>{item.name}</span>)}
                    </div>
                  ) : (
                    <p className="no-topics">No topics assigned.</p>
                  )}
                </section>
                <p className="public-content-note">This view contains public problem content. Private editorials and reference solutions are not shown here.</p>
              </aside>
            </div>
          </>
        ) : null}
      </main>
    </div>
  )
}

function SampleBlock({ title, value }) {
  return (
    <div className="sample-block">
      <div className="sample-heading"><span className="sample-dot" />{title}</div>
      <pre>{value || '—'}</pre>
    </div>
  )
}

function DetailLoading() {
  return (
    <div className="detail-loading" role="status" aria-label="Loading problem details">
      <div className="loading-line loading-eyebrow" />
      <div className="loading-line loading-title" />
      <div className="loading-grid"><div className="loading-panel" /><div className="loading-panel" /></div>
    </div>
  )
}

function normalizeDifficulty(value) {
  return (value || 'unknown').toLowerCase().replace(/[^a-z0-9-]/g, '')
}

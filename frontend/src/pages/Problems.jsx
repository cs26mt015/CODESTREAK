import { useEffect, useMemo, useState } from 'react'
import { fetchProblemTags, fetchProblems } from '../services/problems'

const PAGE_SIZE = 10
const DIFFICULTIES = ['Easy', 'Medium', 'Hard']

export default function Problems() {
  const [searchDraft, setSearchDraft] = useState('')
  const [search, setSearch] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [tag, setTag] = useState('')
  const [offset, setOffset] = useState(0)
  const [page, setPage] = useState({ items: [], total: 0 })
  const [tags, setTags] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [tagError, setTagError] = useState('')
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearch(searchDraft.trim())
      setOffset(0)
    }, 250)
    return () => window.clearTimeout(timer)
  }, [searchDraft])

  useEffect(() => {
    const controller = new AbortController()
    setIsLoading(true)
    setError('')

    fetchProblems({
      search,
      difficulty,
      tag,
      offset,
      limit: PAGE_SIZE,
      signal: controller.signal,
    })
      .then(result => {
        setPage({ items: Array.isArray(result.items) ? result.items : [], total: result.total || 0 })
      })
      .catch(requestError => {
        if (requestError.name !== 'AbortError') setError(requestError.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })

    return () => controller.abort()
  }, [search, difficulty, tag, offset, retryCount])

  useEffect(() => {
    const controller = new AbortController()
    fetchProblemTags({ signal: controller.signal })
      .then(result => setTags(Array.isArray(result) ? result : []))
      .catch(requestError => {
        if (requestError.name !== 'AbortError') setTagError(requestError.message)
      })
    return () => controller.abort()
  }, [])

  const pageCount = Math.max(1, Math.ceil(page.total / PAGE_SIZE))
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1
  const firstResult = page.total === 0 ? 0 : offset + 1
  const lastResult = Math.min(offset + page.items.length, page.total)
  const hasFilters = Boolean(searchDraft || difficulty || tag)

  const visibleRange = useMemo(() => {
    if (page.total === 0) return 'No problems found'
    return `Showing ${firstResult}–${lastResult} of ${page.total} problems`
  }, [firstResult, lastResult, page.total])

  function changeFilter(setter, value) {
    setter(value)
    setOffset(0)
  }

  function resetFilters() {
    setSearchDraft('')
    setSearch('')
    setDifficulty('')
    setTag('')
    setOffset(0)
  }

  return (
    <div className="library-app">
      <header className="library-header">
        <a className="library-brand" href="/" aria-label="CodeStreak">
          <span className="library-brand-mark" aria-hidden="true">{'{ }'}</span>
          <span>code<span>streak</span></span>
        </a>
        <div className="header-context"><span className="header-status-dot" /> Coding practice</div>
      </header>

      <main className="library-main">
        <section className="library-intro" aria-labelledby="library-title">
          <p className="library-eyebrow">PROBLEM LIBRARY</p>
          <div className="library-title-row">
            <div>
              <h1 id="library-title">Find your next challenge.</h1>
              <p className="library-subtitle">
                Browse focused practice problems and choose what you want to work on next.
              </p>
            </div>
            <div className="library-count" aria-live="polite">
              <strong>{page.total}</strong>
              <span>published problems</span>
            </div>
          </div>
        </section>

        <section className="library-panel" aria-label="Browse problems">
          <div className="library-toolbar">
            <label className="library-search">
              <span className="search-symbol" aria-hidden="true" />
              <span className="visually-hidden">Search problem titles and descriptions</span>
              <input
                type="search"
                value={searchDraft}
                onChange={event => setSearchDraft(event.target.value)}
                placeholder="Search titles and descriptions"
                maxLength={200}
              />
              {searchDraft && (
                <button className="clear-search" type="button" onClick={() => setSearchDraft('')} aria-label="Clear search">
                  ×
                </button>
              )}
            </label>

            <label className="filter-control">
              <span>Difficulty</span>
              <select value={difficulty} onChange={event => changeFilter(setDifficulty, event.target.value)}>
                <option value="">All levels</option>
                {DIFFICULTIES.map(level => <option key={level} value={level}>{level}</option>)}
              </select>
            </label>

            <label className="filter-control topic-filter">
              <span>Topic</span>
              <select value={tag} onChange={event => changeFilter(setTag, event.target.value)} disabled={Boolean(tagError)}>
                <option value="">All topics</option>
                {tags.map(item => <option key={item.tag_id} value={item.name}>{item.name}</option>)}
              </select>
            </label>

            {hasFilters && (
              <button className="reset-button" type="button" onClick={resetFilters}>Clear filters</button>
            )}
          </div>

          {tagError && <p className="topic-note" role="status">Topic filters are temporarily unavailable.</p>}

          <div className="results-bar">
            <span aria-live="polite">{visibleRange}</span>
            <span>Sorted by problem number</span>
          </div>

          <div className="problem-list" aria-busy={isLoading}>
            {isLoading ? (
              <div className="loading-list" aria-label="Loading problems">
                {Array.from({ length: 5 }, (_, index) => <div className="problem-skeleton" key={index} />)}
              </div>
            ) : error ? (
              <div className="library-message error-message" role="alert">
                <span className="message-icon" aria-hidden="true">!</span>
                <h2>We couldn’t load the problems.</h2>
                <p>{error}</p>
                <button className="retry-button" type="button" onClick={() => setRetryCount(value => value + 1)}>
                  Try again
                </button>
              </div>
            ) : page.items.length === 0 ? (
              <div className="library-message empty-message">
                <span className="empty-mark" aria-hidden="true">∅</span>
                <h2>{hasFilters ? 'No matching problems' : 'The library is empty for now'}</h2>
                <p>{hasFilters ? 'Try a different search or clear one of your filters.' : 'Published problems will appear here when they are available.'}</p>
                {hasFilters && <button className="retry-button" type="button" onClick={resetFilters}>Clear filters</button>}
              </div>
            ) : (
              page.items.map(problem => <ProblemCard key={problem.problem_id} problem={problem} />)
            )}
          </div>

          <footer className="library-pagination">
            <span>{visibleRange}</span>
            <div className="pagination-controls" aria-label="Problem pages">
              <button
                type="button"
                className="page-button"
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                disabled={isLoading || currentPage <= 1}
                aria-label="Previous page"
              >
                ← <span>Previous</span>
              </button>
              <span className="page-indicator">Page <strong>{currentPage}</strong> of {pageCount}</span>
              <button
                type="button"
                className="page-button"
                onClick={() => setOffset(offset + PAGE_SIZE)}
                disabled={isLoading || currentPage >= pageCount || Boolean(error)}
                aria-label="Next page"
              >
                <span>Next</span> →
              </button>
            </div>
          </footer>
        </section>

        <p className="library-footer-note">Choose a challenge that fits your pace. You can refine the list any time.</p>
      </main>
    </div>
  )
}

function ProblemCard({ problem }) {
  const level = (problem.difficulty || 'Unknown').toLowerCase()
  const tags = Array.isArray(problem.tags) ? problem.tags : []

  return (
    <article className="problem-card">
      <div className={`problem-number difficulty-tone-${level}`} aria-hidden="true">
        {String(problem.problem_id).padStart(2, '0')}
      </div>
      <div className="problem-copy">
        <div className="problem-heading-line">
          <h2>{problem.title}</h2>
          <span className={`difficulty-pill difficulty-${level}`}>
            <i aria-hidden="true" />{problem.difficulty}
          </span>
        </div>
        <p className="problem-description">{problem.statement}</p>
        <div className="problem-meta">
          <span className="problem-id">Problem #{problem.problem_id}</span>
          {tags.length > 0 && <span className="meta-divider" aria-hidden="true">·</span>}
          {tags.map(item => <span className="topic-chip" key={item.tag_id}>{item.name}</span>)}
        </div>
      </div>
    </article>
  )
}

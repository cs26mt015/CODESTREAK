import { useEffect, useState } from 'react'
import { apiRequest, getSession } from '../services/api'
import './AdminStudio.css'

const PAGE_SIZE = 20
const EMPTY_CASE = { input: '', output: '' }
const EMPTY_PROBLEM = {
  title: '',
  difficulty: 'Easy',
  statement: '',
  constraints: '',
  sample_input: '',
  sample_output: '',
  editorial_notes: '',
  reference_solution: '',
  tags: '',
  hidden_test_cases: [],
}

export default function AdminStudio({ onSignOut }) {
  const path = window.location.pathname.replace(/\/$/, '')
  const formMatch = path.match(/^\/admin\/problems\/(new|\d+)$/)
  const problemId = formMatch && formMatch[1] !== 'new' ? Number(formMatch[1]) : null
  if (formMatch) return <ProblemForm key={problemId || 'new'} problemId={problemId} onSignOut={onSignOut} />
  return <ProblemList onSignOut={onSignOut} />
}

function AdminHeader({ onSignOut, active = 'problems' }) {
  const session = getSession()
  return (
    <header className="admin-header">
      <a className="admin-brand" href="/" aria-label="CodeStreak home"><span className="admin-brand-mark">{'{ }'}</span><span>code<span>streak</span></span></a>
      <nav className="admin-nav" aria-label="Admin navigation">
        <a className={active === 'overview' ? 'active' : ''} href="/">Overview</a>
        <a className={active === 'problems' ? 'active' : ''} href="/admin/problems">Problem studio</a>
        <a href="/problems">View library</a>
      </nav>
      <div className="admin-account"><span>{session?.user?.name || 'Administrator'}</span><button type="button" onClick={onSignOut}>Sign out</button></div>
    </header>
  )
}

function ProblemList({ onSignOut }) {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState(new URLSearchParams(window.location.search).has('created') ? 'Problem created as a draft.' : '')
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setError('')
    apiRequest(`/admin/problems?offset=${offset}&limit=${PAGE_SIZE}`, { signal: controller.signal })
      .then(result => {
        setItems(result.items || [])
        setTotal(result.total || 0)
      })
      .catch(requestError => {
        if (requestError.name !== 'AbortError') setError(requestError.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [offset, refreshKey])

  async function togglePublication(problem) {
    setError('')
    setNotice('')
    if (!problem.is_published && !problem.hidden_test_cases?.length) {
      setError('Add at least one hidden test case before publishing this problem.')
      return
    }
    try {
      const updated = await apiRequest(`/admin/problems/${problem.problem_id}/publication`, {
        method: 'PUT',
        body: JSON.stringify({ is_published: !problem.is_published }),
      })
      setItems(current => current.map(item => item.problem_id === updated.problem_id ? updated : item))
      setNotice(updated.is_published ? 'Problem published to the public library.' : 'Problem unpublished.')
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  async function deleteProblem(problem) {
    if (!window.confirm(`Delete “${problem.title}”? This cannot be undone.`)) return
    setError('')
    setNotice('')
    try {
      await apiRequest(`/admin/problems/${problem.problem_id}`, { method: 'DELETE' })
      setNotice(`“${problem.title}” was deleted.`)
      setRefreshKey(value => value + 1)
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  const publishedCount = items.filter(problem => problem.is_published).length
  const pageNumber = Math.floor(offset / PAGE_SIZE) + 1
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="admin-app">
      <AdminHeader onSignOut={onSignOut} />
      <main className="admin-main">
        <div className="admin-title-row">
          <div><p className="admin-eyebrow">CONTENT MANAGEMENT</p><h1>Problem studio</h1><p className="admin-subtitle">Write, review, and publish coding problems.</p></div>
          <a className="admin-primary-link" href="/admin/problems/new"><span aria-hidden="true">＋</span> Create problem</a>
        </div>

        <section className="admin-metrics" aria-label="Problem totals">
          <div><span>Problems</span><strong>{total}</strong></div>
          <div><span>Published on this page</span><strong>{publishedCount}</strong></div>
          <div><span>Drafts on this page</span><strong>{items.length - publishedCount}</strong></div>
        </section>

        {notice && <div className="admin-notice" role="status">{notice}</div>}
        {error && <div className="admin-error" role="alert">{error}<button type="button" onClick={() => setRefreshKey(value => value + 1)}>Reload</button></div>}

        <section className="admin-table-panel" aria-labelledby="admin-list-title">
          <div className="admin-table-heading"><div><h2 id="admin-list-title">All problems</h2><p>Drafts are visible only to administrators until published.</p></div><span>{total} total</span></div>
          {loading ? <div className="admin-loading" role="status">Loading problems…</div> : items.length ? (
            <div className="admin-table-scroll"><table className="admin-table"><thead><tr><th>Problem</th><th>Difficulty</th><th>Test cases</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>{items.map(problem => <tr key={problem.problem_id}>
                <td><strong>{problem.title}</strong><small>#{problem.problem_id} · {problem.tags?.map(tag => tag.name).join(', ') || 'No topics'}</small></td>
                <td><span className={`admin-difficulty ${normalize(problem.difficulty)}`}>{problem.difficulty}</span></td>
                <td>{problem.hidden_test_cases?.length || 0}</td>
                <td><span className={`admin-status ${problem.is_published ? 'published' : 'draft'}`}>{problem.is_published ? 'Published' : 'Draft'}</span></td>
                <td><div className="admin-row-actions"><a href={`/admin/problems/${problem.problem_id}`}>Edit</a><button type="button" onClick={() => togglePublication(problem)}>{problem.is_published ? 'Unpublish' : 'Publish'}</button><button className="danger" type="button" onClick={() => deleteProblem(problem)}>Delete</button></div></td>
              </tr>)}</tbody>
            </table></div>
          ) : <div className="admin-empty"><span aria-hidden="true">◇</span><h2>No problems yet</h2><p>Create a draft and add test cases before publishing it.</p><a href="/admin/problems/new">Create your first problem</a></div>}
          <footer className="admin-pagination"><span>{total ? `${offset + 1}–${Math.min(offset + items.length, total)} of ${total}` : 'No problems'}</span><div><button type="button" disabled={loading || offset === 0} onClick={() => setOffset(value => Math.max(0, value - PAGE_SIZE))}>Previous</button><span>Page {pageNumber} of {pageCount}</span><button type="button" disabled={loading || offset + PAGE_SIZE >= total} onClick={() => setOffset(value => value + PAGE_SIZE)}>Next</button></div></footer>
        </section>
      </main>
    </div>
  )
}

function ProblemForm({ problemId, onSignOut }) {
  const [form, setForm] = useState(EMPTY_PROBLEM)
  const [loading, setLoading] = useState(Boolean(problemId))
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  useEffect(() => {
    if (!problemId) return
    const controller = new AbortController()
    apiRequest(`/admin/problems/${problemId}`, { signal: controller.signal })
      .then(problem => setForm({
        title: problem.title || '',
        difficulty: problem.difficulty || 'Easy',
        statement: problem.statement || '',
        constraints: problem.constraints || '',
        sample_input: problem.sample_input || '',
        sample_output: problem.sample_output || '',
        editorial_notes: problem.editorial_notes || '',
        reference_solution: problem.reference_solution || '',
        tags: (problem.tags || []).map(tag => tag.name).join(', '),
        hidden_test_cases: problem.hidden_test_cases || [],
      }))
      .catch(requestError => {
        if (requestError.name !== 'AbortError') setError(requestError.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [problemId])

  function setField(name, value) {
    setForm(current => ({ ...current, [name]: value }))
  }

  function updateCase(index, field, value) {
    setForm(current => ({
      ...current,
      hidden_test_cases: current.hidden_test_cases.map((testCase, caseIndex) => caseIndex === index ? { ...testCase, [field]: value } : testCase),
    }))
  }

  function removeCase(index) {
    setForm(current => ({ ...current, hidden_test_cases: current.hidden_test_cases.filter((_, caseIndex) => caseIndex !== index) }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setNotice('')
    const payload = {
      title: form.title.trim(),
      difficulty: form.difficulty,
      statement: form.statement.trim(),
      constraints: form.constraints || null,
      sample_input: form.sample_input || null,
      sample_output: form.sample_output || null,
      editorial_notes: form.editorial_notes || null,
      reference_solution: form.reference_solution || null,
      tags: [...new Set(form.tags.split(',').map(tag => tag.trim()).filter(Boolean))],
      hidden_test_cases: form.hidden_test_cases,
    }
    if (!payload.title || !payload.statement) {
      setError('Enter a title and problem statement.')
      return
    }
    if (payload.hidden_test_cases.length > 20) {
      setError('A problem can have at most 20 hidden test cases.')
      return
    }
    setSaving(true)
    try {
      if (problemId) {
        await apiRequest(`/admin/problems/${problemId}`, { method: 'PATCH', body: JSON.stringify(payload) })
        setNotice('Problem changes saved.')
      } else {
        await apiRequest('/admin/problems', { method: 'POST', body: JSON.stringify(payload) })
        window.location.assign('/admin/problems?created=1')
      }
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="admin-app">
      <AdminHeader onSignOut={onSignOut} />
      <main className="admin-main admin-form-main">
        <a className="admin-back-link" href="/admin/problems">← Back to problems</a>
        <div className="admin-title-row form-title-row"><div><p className="admin-eyebrow">CONTENT MANAGEMENT</p><h1>{problemId ? 'Edit problem' : 'Create problem'}</h1><p className="admin-subtitle">New problems are saved as drafts until you publish them.</p></div></div>
        {error && <div className="admin-error" role="alert">{error}</div>}
        {notice && <div className="admin-notice" role="status">{notice}</div>}
        {loading ? <div className="admin-loading">Loading problem…</div> : (
          <form className="admin-form" onSubmit={handleSubmit}>
            <section className="admin-form-section"><div className="admin-form-section-title"><span>01</span><div><h2>Problem details</h2><p>Public content learners see in the problem library.</p></div></div>
              <div className="admin-form-grid">
                <label className="admin-field field-wide">Title<input required maxLength={255} value={form.title} onChange={event => setField('title', event.target.value)} placeholder="e.g. Two Sum" /></label>
                <label className="admin-field">Difficulty<select value={form.difficulty} onChange={event => setField('difficulty', event.target.value)}><option>Easy</option><option>Medium</option><option>Hard</option></select></label>
                <label className="admin-field">Topics<input value={form.tags} onChange={event => setField('tags', event.target.value)} placeholder="Arrays, Hash Map, Sorting" /><small>Separate topics with commas.</small></label>
                <label className="admin-field field-wide">Statement<textarea required maxLength={50000} rows={7} value={form.statement} onChange={event => setField('statement', event.target.value)} placeholder="Describe the problem and expected behavior." /></label>
                <label className="admin-field field-wide">Constraints<textarea rows={3} maxLength={30000} value={form.constraints} onChange={event => setField('constraints', event.target.value)} placeholder="List input and output constraints." /></label>
                <label className="admin-field">Sample input<textarea rows={4} maxLength={30000} value={form.sample_input} onChange={event => setField('sample_input', event.target.value)} /></label>
                <label className="admin-field">Sample output<textarea rows={4} maxLength={30000} value={form.sample_output} onChange={event => setField('sample_output', event.target.value)} /></label>
              </div>
            </section>

            <section className="admin-form-section"><div className="admin-form-section-title"><span>02</span><div><h2>Private content</h2><p>Only administrators can view this material.</p></div></div>
              <div className="admin-form-grid">
                <label className="admin-field">Editorial notes<textarea rows={4} maxLength={30000} value={form.editorial_notes} onChange={event => setField('editorial_notes', event.target.value)} /></label>
                <label className="admin-field">Reference solution<textarea rows={4} maxLength={50000} value={form.reference_solution} onChange={event => setField('reference_solution', event.target.value)} /></label>
              </div>
            </section>

            <section className="admin-form-section"><div className="admin-form-section-title"><span>03</span><div><h2>Hidden test cases</h2><p>Expected input/output pairs used by Judge0 submissions. Up to 20 cases.</p></div><button className="add-case-button" type="button" disabled={form.hidden_test_cases.length >= 20} onClick={() => setField('hidden_test_cases', [...form.hidden_test_cases, { ...EMPTY_CASE }])}>＋ Add case</button></div>
              {form.hidden_test_cases.length ? <div className="admin-test-cases">{form.hidden_test_cases.map((testCase, index) => <article className="admin-test-case" key={index}><div className="test-case-heading"><strong>Case {index + 1}</strong><button type="button" onClick={() => removeCase(index)} aria-label={`Remove test case ${index + 1}`}>Remove</button></div><label className="admin-field">Input<textarea rows={3} maxLength={64000} value={testCase.input} onChange={event => updateCase(index, 'input', event.target.value)} /></label><label className="admin-field">Expected output<textarea rows={3} maxLength={64000} value={testCase.output} onChange={event => updateCase(index, 'output', event.target.value)} /></label></article>)}</div> : <p className="no-test-cases">No hidden cases added. Add at least one before publishing so submissions can be judged.</p>}
            </section>

            <footer className="admin-form-footer"><a href="/admin/problems">Cancel</a><button type="submit" className="admin-primary-link" disabled={saving}>{saving ? 'Saving…' : problemId ? 'Save changes' : 'Save draft'}</button></footer>
          </form>
        )}
      </main>
    </div>
  )
}

function normalize(value = '') {
  return value.toLowerCase().replace(/[^a-z0-9-]/g, '')
}

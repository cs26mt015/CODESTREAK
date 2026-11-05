import Editor from '@monaco-editor/react'
import { useEffect, useMemo, useState } from 'react'
import { fetchProblem } from '../services/problems'
import { getLanguages, runCode, submitCode } from '../services/judge'
import { readSessionToken, saveSessionToken } from '../services/session'
import './CodeEditor.css'

const STARTER_CODE = {
  python: 'import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # Write your solution here\n\nif __name__ == "__main__":\n    solve()\n',
  cpp: '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // Write your solution here\n    return 0;\n}\n',
  java: 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        // Write your solution here\n    }\n}\n',
}

export default function CodeEditor({ problemId }) {
  const [problem, setProblem] = useState(null)
  const [languages, setLanguages] = useState([])
  const [languageId, setLanguageId] = useState('')
  const [code, setCode] = useState('')
  const [stdin, setStdin] = useState('')
  const [token, setToken] = useState(readSessionToken)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const selectedLanguage = useMemo(() => languages.find(item => String(item.id) === languageId), [languages, languageId])
  const languageKey = getLanguageKey(selectedLanguage?.name)

  useEffect(() => {
    fetchProblem(problemId).then(data => {
      setProblem(data)
      setStdin(data.sample_input || '')
    }).catch(e => setError(e.message))
    getLanguages().then(items => {
      const available = items.filter(item => !item.is_archived)
      setLanguages(available)
      const preferred = available.find(item => /python/i.test(item.name)) || available[0]
      if (preferred) {
        setLanguageId(String(preferred.id))
        setCode(STARTER_CODE[getLanguageKey(preferred.name)] || '')
      }
    }).catch(e => setError(e.message))
  }, [problemId])

  function changeLanguage(event) {
    const nextId = event.target.value
    const language = languages.find(item => String(item.id) === nextId)
    setLanguageId(nextId)
    setCode(STARTER_CODE[getLanguageKey(language?.name)] || '')
  }

  async function execute(submit) {
    setBusy(true)
    setError('')
    setResult(null)
    try {
      if (token.trim()) saveSessionToken(token.trim())
      const payload = { language_id: Number(languageId), source_code: code, stdin }
      const response = submit ? await submitCode(problemId, payload) : await runCode(problemId, payload)
      setResult({ ...response, kind: submit ? 'submit' : 'run' })
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="editor-page">
      <header className="editor-topbar">
        <a className="detail-brand" href={`/problems/${problemId}`}><span className="detail-brand-mark">{'{ }'}</span><span>code<span>streak</span></span></a>
        <a className="editor-back" href={`/problems/${problemId}`}>← Problem</a>
        <span className="editor-problem-title">{problem?.title || `Problem #${problemId}`}</span>
        <label className="editor-language-label" htmlFor="language-select">Language</label>
        <select id="language-select" value={languageId} onChange={changeLanguage} disabled={!languages.length}>
          {languages.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </header>
      <div className="editor-workspace">
        <section className="editor-code-pane" aria-label="Source code editor">
          <div className="editor-pane-heading"><span>Solution</span><span>{selectedLanguage?.name || 'Loading languages…'}</span></div>
          <Editor height="100%" language={languageKey} theme="vs-dark" value={code} onChange={value => setCode(value || '')} options={{ minimap: { enabled: false }, fontSize: 14, automaticLayout: true, scrollBeyondLastLine: false, tabSize: 4, padding: { top: 16 } }} />
        </section>
        <aside className="editor-side-pane">
          <section className="editor-problem-card">
            <p className="detail-eyebrow">PROBLEM #{String(problemId).padStart(3, '0')}</p>
            <h1>{problem?.title || 'Loading problem…'}</h1>
            <span className="detail-difficulty">{problem?.difficulty || '—'}</span>
            <p>{problem?.statement || 'The problem statement will appear here.'}</p>
            {problem?.constraints && <><h2>Constraints</h2><pre>{problem.constraints}</pre></>}
          </section>
          <section className="editor-input-card">
            <label htmlFor="custom-input">Custom input</label>
            <textarea id="custom-input" value={stdin} onChange={event => setStdin(event.target.value)} spellCheck="false" />
            <label htmlFor="judge-token">Session token</label>
            <input id="judge-token" type="password" autoComplete="off" value={token} onChange={event => setToken(event.target.value)} placeholder="Sign in to run or submit" />
            <p className="editor-token-note">The token goes to CodeStreak only. It is never sent to Judge0.</p>
            <div className="editor-actions">
              <button type="button" onClick={() => execute(false)} disabled={busy || !languageId}>{busy ? 'Running…' : 'Run'}</button>
              <button type="button" className="submit-action" onClick={() => execute(true)} disabled={busy || !languageId}>{busy ? 'Judging…' : 'Submit'}</button>
            </div>
          </section>
          <section className="editor-result-card" aria-live="polite">
            <h2>{result ? (result.kind === 'run' ? 'Run result' : 'Submission result') : 'Output'}</h2>
            {error && <p className="editor-error">{error}</p>}
            {result && (result.kind === 'run' ? <RunOutput result={result} /> : <SubmissionOutput result={result} />)}
            {!result && !error && <p className="editor-output-empty">Run your code to see output here.</p>}
          </section>
        </aside>
      </div>
    </main>
  )
}

function RunOutput({ result }) {
  const status = result.status?.description || 'Finished'
  return <><strong className={status === 'Accepted' ? 'verdict-ok' : 'verdict-bad'}>{status}</strong><pre>{result.stdout || result.compile_output || result.stderr || 'No output'}</pre>{result.time && <small>{result.time}s · {result.memory || '—'} KB</small>}</>
}

function SubmissionOutput({ result }) {
  return <><strong className={result.verdict === 'Accepted' ? 'verdict-ok' : 'verdict-bad'}>{result.verdict}</strong><p>{result.passed}/{result.total} test cases passed{result.failed_case ? ` · failed at case ${result.failed_case}` : ''}</p><small>{result.time || 0}s · {result.memory || '—'} KB</small></>
}

function getLanguageKey(name = '') {
  if (/python/i.test(name)) return 'python'
  if (/c\+\+/i.test(name)) return 'cpp'
  if (/java/i.test(name)) return 'java'
  if (/javascript/i.test(name)) return 'javascript'
  return 'plaintext'
}

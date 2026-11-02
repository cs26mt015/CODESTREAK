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

import ProblemDetail from './pages/ProblemDetail'

function getProblemId() {
  const pathMatch = window.location.pathname.match(/^\/problems\/(\d+)\/?$/)
  const queryId = new URLSearchParams(window.location.search).get('id')
  const value = pathMatch?.[1] || queryId || '1'
  const problemId = Number(value)
  return Number.isInteger(problemId) && problemId > 0 ? problemId : null
}

export default function App() {
  return <ProblemDetail problemId={getProblemId()} />
}

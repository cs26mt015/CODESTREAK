import { apiRequest } from './api'

export function fetchProblems({ search, difficulty, tag, offset, limit, signal }) {
  const params = new URLSearchParams()
  if (search) params.set('q', search)
  if (difficulty) params.set('difficulty', difficulty)
  if (tag) params.set('tag', tag)
  params.set('offset', String(offset))
  params.set('limit', String(limit))
  return apiRequest(`/problems?${params.toString()}`, { signal })
}

export function fetchProblemTags({ signal } = {}) {
  return apiRequest('/tags', { signal })
}

export function fetchProblem(problemId, { signal } = {}) {
  return apiRequest(`/problems/${encodeURIComponent(problemId)}`, { signal })
}

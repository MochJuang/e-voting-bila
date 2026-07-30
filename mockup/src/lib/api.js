const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

const STUDENT_TOKEN_KEY = 'evoting_student_token'
const ADMIN_TOKEN_KEY = 'evoting_admin_token'

function getStoredToken(key) {
  return localStorage.getItem(key)
}

function setStoredToken(key, value) {
  if (!value) localStorage.removeItem(key)
  else localStorage.setItem(key, value)
}

async function request(path, { method = 'GET', body, token, headers = {}, responseType = 'json' } = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  const contentType = response.headers.get('content-type') || ''

  if (responseType === 'blob') {
    if (!response.ok) {
      const errorText = await response.text()
      let message = errorText || 'Request gagal'
      if (contentType.includes('application/json')) {
        try {
          const parsed = JSON.parse(errorText)
          message = parsed?.detail || parsed?.message || message
        } catch {
          // fallback to raw text
        }
      }
      throw new Error(message)
    }
    return response.blob()
  }

  const payload = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const message = typeof payload === 'string' ? payload : payload?.detail || payload?.message || 'Request gagal'
    throw new Error(message)
  }

  return payload
}

export function getStudentToken() {
  return getStoredToken(STUDENT_TOKEN_KEY)
}

export function setStudentToken(token) {
  setStoredToken(STUDENT_TOKEN_KEY, token)
}

export function clearStudentToken() {
  setStoredToken(STUDENT_TOKEN_KEY, '')
}

export function getAdminToken() {
  return getStoredToken(ADMIN_TOKEN_KEY)
}

export function setAdminToken(token) {
  setStoredToken(ADMIN_TOKEN_KEY, token)
}

export function clearAdminToken() {
  setStoredToken(ADMIN_TOKEN_KEY, '')
}

export const api = {
  auth: {
    login: (body) => request('/auth/login', { method: 'POST', body }),
    register: (body) => request('/auth/register', { method: 'POST', body }),
    me: (token) => request('/auth/me', { token }),
    changePassword: (body, token) => request('/auth/password/change', { method: 'POST', body, token }),
  },
  voters: {
    me: (token) => request('/voters/me', { token }),
    status: (token) => request('/voters/me/status', { token }),
    facePhoto: (token) => request('/voters/me/face-photo', { token }),
    byNim: (nim, token) => request(`/voters/${nim}`, { token }),
  },
  face: {
    enroll: (body, token) => request('/face/enroll', { method: 'POST', body, token }),
    verify: (body, token) => request('/face/verify', { method: 'POST', body, token }),
  },
  election: {
    active: () => request('/election/active'),
    ballot: (token) => request('/election/ballot', { token }),
  },
  votes: {
    submit: (body, token) => request('/votes/submit', { method: 'POST', body, token }),
    confirmation: (token) => request('/votes/confirmation', { token }),
  },
  admin: {
    login: (body) => request('/admin/auth/login', { method: 'POST', body }),
    dashboard: (token) => request('/admin/dashboard', { token }),
    voters: (token) => request('/admin/voters', { token }),
    createVoter: (body, token) => request('/admin/voters', { method: 'POST', body, token }),
    bulkCreateVoters: (body, token) => request('/admin/voters/bulk', { method: 'POST', body, token }),
    updateVoter: (nim, body, token) => request(`/admin/voters/${nim}`, { method: 'PATCH', body, token }),
    deleteVoter: (nim, token) => request(`/admin/voters/${nim}`, { method: 'DELETE', token }),
    voterFacePhoto: (nim, token) => request(`/admin/voters/${nim}/face-photo`, { token }),
    accounts: (token) => request('/admin/accounts', { token }),
    createAccount: (body, token) => request('/admin/accounts', { method: 'POST', body, token }),
    updateAccount: (id, body, token) => request(`/admin/accounts/${id}`, { method: 'PATCH', body, token }),
    deleteAccount: (id, token) => request(`/admin/accounts/${id}`, { method: 'DELETE', token }),
    positions: (token) => request('/admin/positions', { token }),
    createPosition: (body, token) => request('/admin/positions', { method: 'POST', body, token }),
    updatePosition: (id, body, token) => request(`/admin/positions/${id}`, { method: 'PATCH', body, token }),
    deletePosition: (id, token) => request(`/admin/positions/${id}`, { method: 'DELETE', token }),
    candidates: (positionId, token) => request(`/admin/positions/${positionId}/candidates`, { token }),
    createCandidate: (positionId, body, token) =>
      request(`/admin/positions/${positionId}/candidates`, { method: 'POST', body, token }),
    updateCandidate: (positionId, candidateId, body, token) =>
      request(`/admin/positions/${positionId}/candidates/${candidateId}`, { method: 'PATCH', body, token }),
    deleteCandidate: (positionId, candidateId, token) =>
      request(`/admin/positions/${positionId}/candidates/${candidateId}`, { method: 'DELETE', token }),
    kiosks: (token) => request('/admin/kiosks', { token }),
    createKiosk: (body, token) => request('/admin/kiosks', { method: 'POST', body, token }),
    updateKiosk: (id, body, token) => request(`/admin/kiosks/${id}`, { method: 'PATCH', body, token }),
    deleteKiosk: (id, token) => request(`/admin/kiosks/${id}`, { method: 'DELETE', token }),
    results: (token) => request('/admin/results', { token }),
    exportPdf: (token) => request('/admin/results/export/pdf', { token, responseType: 'blob' }),
    exportExcel: (token) => request('/admin/results/export/excel', { token, responseType: 'blob' }),
  },
}

export { API_BASE_URL }

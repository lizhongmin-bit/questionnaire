const API_BASE =
  import.meta.env.VITE_API_BASE ||
  `http://${window.location.hostname}:8000`

const envPublicBaseUrl = import.meta.env.VITE_PUBLIC_BASE_URL
const envPublicHost = import.meta.env.VITE_PUBLIC_HOST

const PUBLIC_BASE_URL =
  envPublicBaseUrl ||
  (envPublicHost ? `${window.location.protocol}//${envPublicHost}` : '')

export function getPublicBaseUrl() {
  return PUBLIC_BASE_URL || ''
}

export function getAdminToken() {
  return localStorage.getItem('admin_token') || ''
}

export function setAdminToken(token) {
  localStorage.setItem('admin_token', token)
}

export async function apiFetch(path, options = {}) {
  const headers = options.headers || {}
  if (options.admin) {
    headers['X-Admin-Token'] = getAdminToken()
  }
  if (!(options.body instanceof FormData) && options.body) {
    headers['Content-Type'] = 'application/json'
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || '请求失败')
  }
  return res
}

export default API_BASE

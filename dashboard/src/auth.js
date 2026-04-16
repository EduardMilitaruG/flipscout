// Auth helpers — token stored in sessionStorage (cleared on tab close)

const KEY = 'fs_token'

const getToken  = ()      => sessionStorage.getItem(KEY)
const setToken  = (t)     => sessionStorage.setItem(KEY, t)
export const clearToken = ()     => sessionStorage.removeItem(KEY)
export const isAuthed  = ()      => !!getToken()

export async function login(username, password) {
  const body = new URLSearchParams({ username, password })
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
  if (!res.ok) throw new Error('Invalid credentials')
  const { access_token } = await res.json()
  setToken(access_token)
}

/** Authenticated fetch — attaches Bearer token, throws on 401 */
export async function apiFetch(url, opts = {}) {
  const token = getToken()
  const res = await fetch(url, {
    ...opts,
    headers: {
      ...opts.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  if (res.status === 401) {
    clearToken()
    window.location.reload()
  }
  return res
}

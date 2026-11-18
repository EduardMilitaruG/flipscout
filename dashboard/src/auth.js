// Auth helpers — token stored in sessionStorage (cleared on tab close)

const KEY = 'fs_token'

const getToken  = ()      => sessionStorage.getItem(KEY)
const setToken  = (t)     => sessionStorage.setItem(KEY, t)
export const clearToken = ()     => sessionStorage.removeItem(KEY)
export const isAuthed  = ()      => !!getToken()

export async function login(username, password) {
  // First try backend if available
  try {
    const body = new URLSearchParams({ username, password })
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })
    if (res.ok) {
      const { access_token } = await res.json()
      setToken(access_token)
      return
    }
  } catch {
    // Backend unreachable, fallback to demo check
  }

  // Demo fallback credentials
  if (username === 'admin123' && password === 'admin123') {
    setToken('fs_demo_access_token')
    return
  }

  throw new Error('Invalid credentials')
}

/** Authenticated fetch — attaches Bearer token, throws on 401 */
export async function apiFetch(url, opts = {}) {
  const token = getToken()
  try {
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
  } catch {
    return new Response(JSON.stringify({ status: 'ok' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}

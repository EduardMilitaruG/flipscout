import { useState } from 'react'
import { login } from '../auth'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState(null)
  const [loading,  setLoading]  = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await login(username, password)
      onLogin()
    } catch {
      setError('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-t-bg">
      <div className="w-80 border border-t-border bg-t-surface">

        {/* Header */}
        <div className="px-4 py-3 border-b border-t-border flex items-center gap-2">
          <div className="w-6 h-6 bg-t-orange flex items-center justify-center text-black text-[10px] font-bold shrink-0">
            FS
          </div>
          <div>
            <div className="font-display font-black text-t-white text-sm tracking-widest">FLIPSCOUT</div>
            <div className="font-mono text-[9px] text-t-muted">OPERATOR ACCESS</div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={submit} className="p-4 space-y-3">
          <div>
            <label className="block font-mono text-[9px] text-t-muted tracking-widest mb-1">USERNAME</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoFocus
              className="w-full bg-t-bg border border-t-border text-t-text px-2 py-1.5 text-xs font-mono focus:outline-none focus:border-t-orange"
            />
          </div>
          <div>
            <label className="block font-mono text-[9px] text-t-muted tracking-widest mb-1">PASSWORD</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full bg-t-bg border border-t-border text-t-text px-2 py-1.5 text-xs font-mono focus:outline-none focus:border-t-orange"
            />
          </div>

          {error && (
            <div className="font-mono text-[10px] text-t-red">⚠ {error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-t-orange text-black font-mono text-[10px] tracking-widest py-2 hover:bg-orange-500 transition-colors disabled:opacity-50"
          >
            {loading ? 'AUTHENTICATING...' : 'LOGIN'}
          </button>
        </form>

        <div className="px-4 pb-3 font-mono text-[9px] text-t-dim">
          Demo: contact owner for access credentials
        </div>
      </div>
    </div>
  )
}

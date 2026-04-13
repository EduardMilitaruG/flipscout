import { useState, useEffect } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Sniper from './pages/Sniper'
import Login from './pages/Login'
import { isAuthed, clearToken } from './auth'

const nav = [
  { to: '/',       label: 'DEALS',  num: '01' },
  { to: '/sniper', label: 'SNIPER', num: '02' },
]

function useJSTClock() {
  const [time, setTime] = useState('')
  useEffect(() => {
    const tick = () => {
      const jst = new Date(Date.now() + 9 * 3600 * 1000)
      setTime(jst.toISOString().slice(11, 19) + ' JST')
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])
  return time
}

export default function App() {
  const [authed, setAuthed] = useState(isAuthed())
  const time = useJSTClock()

  if (!authed) return <Login onLogin={() => setAuthed(true)} />

  return (
    <div className="flex flex-col h-screen bg-t-bg overflow-hidden font-body">

      {/* ── TOP STATUS BAR ──────────────────────────── */}
      <div className="flex items-center justify-between px-4 h-7 bg-black border-b border-t-border shrink-0">
        <div className="flex items-center gap-3 font-mono text-[10px] text-t-muted">
          <span className="text-t-orange font-bold">▶</span>
          <span className="text-t-sub tracking-wider">FS-TERMINAL</span>
          <span className="text-t-dim">│</span>
          <span>v2.4.1</span>
          <span className="text-t-dim">│</span>
          <span className="text-t-blue">{time}</span>
        </div>
        <div className="flex items-center gap-3 font-mono text-[10px] text-t-muted">
          <span>API<span className="text-t-green ml-1">●</span><span className="ml-1 text-t-sub">:8000</span></span>
          <span className="text-t-dim">│</span>
          <span>SCAN<span className="text-t-amber ml-1">■</span></span>
          <span className="text-t-dim">│</span>
          <span>JP-CLUSTER-A</span>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">

        {/* ── SIDEBAR ─────────────────────────────────── */}
        <aside className="w-44 bg-[#090909] border-r border-t-border flex flex-col shrink-0 overflow-y-auto cross-matrix">

          {/* Logo block */}
          <div className="px-3 py-3 border-b border-t-border flex items-center gap-2 bg-[#090909]">
            <div className="w-7 h-7 badge-orange flex items-center justify-center text-xs shrink-0">
              FS
            </div>
            <div>
              <div className="font-display font-black text-t-white text-sm tracking-[0.15em] leading-none uppercase">
                Flipscout
              </div>
              <div className="font-mono text-[9px] text-t-muted mt-0.5">JP-OPS v2.4</div>
            </div>
          </div>

          {/* Nav */}
          <nav className="flex flex-col pt-3 gap-0.5 px-2">
            <div className="font-mono text-[9px] text-t-dim tracking-widest px-2 pb-1">// MODULES</div>
            {nav.map(({ to, label, num }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-2 py-2 text-xs transition-colors border-l-2 font-mono ${
                    isActive
                      ? 'text-t-orange border-t-orange bg-t-orange/5'
                      : 'text-t-muted border-transparent hover:text-t-text hover:border-t-line'
                  }`
                }
              >
                <span className="text-[9px] text-t-dim w-4">{num}</span>
                {label}
              </NavLink>
            ))}
          </nav>

          {/* Rotated label (moodboard: rotated edge text) */}
          <div className="flex justify-center py-6">
            <span
              className="font-display font-black text-t-dim text-[40px] leading-none tracking-tighter select-none"
              style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}
            >
              FLIPSCOUT
            </span>
          </div>

          {/* Bottom system info */}
          <div className="mt-auto border-t border-t-border px-4 py-3 space-y-1 bg-[#090909]">
            <div className="font-mono text-[9px] text-t-dim">BUILD 2024.11.15</div>
            <div className="font-mono text-[9px] text-t-dim">HASH ac3a569</div>
            <div className="font-mono text-[9px] flex items-center gap-1 mb-2">
              <span className="text-t-green">●</span>
              <span className="text-t-muted">ONLINE</span>
            </div>
            <button
              onClick={() => { clearToken(); setAuthed(false) }}
              className="w-full font-mono text-[9px] text-t-dim hover:text-t-red border border-t-border px-2 py-1 transition-colors text-left tracking-widest"
            >
              LOGOUT
            </button>
          </div>
        </aside>

        {/* ── MAIN ─────────────────────────────────────── */}
        <main className="flex-1 overflow-y-auto bg-t-bg">
          <Routes>
            <Route path="/"       element={<Dashboard />} />
            <Route path="/sniper" element={<Sniper />} />
          </Routes>
        </main>

      </div>
    </div>
  )
}

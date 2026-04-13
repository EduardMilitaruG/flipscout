import { useState, useEffect } from 'react'
import { Plus, Pause, Play, RefreshCw } from 'lucide-react'
import SniperStatusStrip from '../components/SniperStatusStrip'
import TargetsTable from '../components/TargetsTable'
import EventLog from '../components/EventLog'
import { apiFetch } from '../auth'

const DEFAULT_FORM = {
  id: '', query: '', category: 'general',
  platform: ['wallapop'], max_buy_price_eur: '',
  min_margin_pct: 20, auto_buy: false, reserve_on_match: true,
}

const FORM_FIELDS = [
  { label: 'TARGET_ID',    key: 'id',                 ph: 'snipe_ps5' },
  { label: 'SEARCH_QUERY', key: 'query',              ph: 'PS5 slim' },
  { label: 'MAX_PRICE_EUR', key: 'max_buy_price_eur', ph: '350', type: 'number' },
  { label: 'MIN_MARGIN_%', key: 'min_margin_pct',     ph: '20',  type: 'number' },
]

export default function Sniper() {
  const [targets, setTargets] = useState([])
  const [events,  setEvents]  = useState([])
  const [status,  setStatus]  = useState(null)
  const [showAdd, setShowAdd] = useState(false)
  const [form,    setForm]    = useState(DEFAULT_FORM)
  const [error,   setError]   = useState(null)

  const fetchAll = async () => {
    try {
      setError(null)
      const [t, e, s] = await Promise.all([
        fetch('/api/sniper/targets').then(r => r.json()),
        fetch('/api/sniper/events?limit=30').then(r => r.json()),
        fetch('/api/sniper/status').then(r => r.json()),
      ])
      setTargets(t); setEvents(e); setStatus(s)
    } catch {
      setError('Cannot reach API — is the backend running?')
    }
  }

  useEffect(() => {
    fetchAll()
    const id = setInterval(fetchAll, 15_000)
    return () => clearInterval(id)
  }, [])

  const togglePause = async () => {
    const url = status?.paused ? '/api/sniper/resume-all' : '/api/sniper/pause-all'
    await apiFetch(url, { method: 'POST' })
    fetchAll()
  }

  const toggleTarget = async (id, active) => {
    await apiFetch(`/api/sniper/targets/${id}/toggle?active=${!active}`, { method: 'PATCH' })
    fetchAll()
  }

  const deleteTarget = async (id) => {
    await apiFetch(`/api/sniper/targets/${id}`, { method: 'DELETE' })
    fetchAll()
  }

  const createTarget = async () => {
    if (!form.id || !form.query || !form.max_buy_price_eur) return
    await apiFetch('/api/sniper/targets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, max_buy_price_eur: Number(form.max_buy_price_eur) }),
    })
    setShowAdd(false)
    setForm(DEFAULT_FORM)
    fetchAll()
  }

  const activeCount = targets.filter(t => t.active).length

  return (
    <div className="flex flex-col h-full">

      {/* ── PAGE HEADER ── */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-t-border bg-t-surface shrink-0">
        <div className="flex items-center gap-3 text-xs">
          <span className="text-t-amber tracking-widest">SNIPER</span>
          <span className="text-t-dim">│</span>
          <span className="text-t-muted">{activeCount}/{targets.length} ARMED</span>
          {status && (
            <>
              <span className="text-t-dim">│</span>
              <span className={status.paused ? 'text-t-amber' : 'text-t-green'}>
                {status.paused ? '■ PAUSED' : '● ACTIVE'}
              </span>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchAll}
            className="flex items-center gap-1.5 text-[10px] text-t-muted hover:text-t-text border border-t-border px-2 py-1 transition-colors hover:border-t-line"
          >
            <RefreshCw size={11} /> REFRESH
          </button>
          <button
            onClick={togglePause}
            className={`flex items-center gap-1.5 text-[10px] px-2 py-1 border transition-colors ${
              status?.paused
                ? 'border-t-green text-t-green hover:bg-t-green/5'
                : 'border-t-amber text-t-amber hover:bg-t-amber/5'
            }`}
          >
            {status?.paused
              ? <><Play size={11} /> RESUME ALL</>
              : <><Pause size={11} /> PAUSE ALL</>}
          </button>
          <button
            onClick={() => setShowAdd(v => !v)}
            className="flex items-center gap-1.5 text-[10px] px-2 py-1 border border-t-orange text-t-orange hover:bg-t-orange/5 transition-colors"
          >
            <Plus size={11} /> NEW TARGET
          </button>
        </div>
      </div>

      {/* ── ERROR BANNER ── */}
      {error && (
        <div className="px-4 py-2 bg-red-950/40 border-b border-t-red text-t-red text-[11px] flex items-center gap-2">
          <span>⚠</span> {error}
        </div>
      )}

      <div className="flex-1 overflow-y-auto">

        <SniperStatusStrip status={status} />

        {/* ── ADD TARGET FORM ── */}
        {showAdd && (
          <div className="border-b border-t-border bg-t-surface p-4">
            <div className="text-[9px] text-t-amber tracking-widest mb-3">// NEW_SNIPE_TARGET</div>
            <div className="grid grid-cols-4 gap-3 mb-3">
              {FORM_FIELDS.map(({ label, key, ph, type }) => (
                <div key={key}>
                  <label className="block text-[9px] text-t-muted tracking-widest mb-1">{label}</label>
                  <input
                    type={type ?? 'text'}
                    placeholder={ph}
                    value={form[key]}
                    onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
                    className="w-full bg-t-bg border border-t-border text-t-text px-2 py-1.5 text-xs focus:outline-none focus:border-t-orange placeholder:text-t-dim"
                  />
                </div>
              ))}
            </div>
            <div className="flex items-center gap-6 mb-3">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-t-sub">
                <input
                  type="checkbox"
                  checked={form.reserve_on_match}
                  onChange={e => setForm(p => ({ ...p, reserve_on_match: e.target.checked }))}
                />
                MESSAGE SELLER ON MATCH
              </label>
              <label className="flex items-center gap-2 cursor-pointer text-xs text-t-red">
                <input
                  type="checkbox"
                  checked={form.auto_buy}
                  onChange={e => setForm(p => ({ ...p, auto_buy: e.target.checked }))}
                />
                AUTO-BUY (VINTED ONLY)
              </label>
            </div>
            <div className="flex gap-2">
              <button
                onClick={createTarget}
                className="text-[10px] px-3 py-1.5 bg-t-orange text-black hover:bg-orange-500 transition-colors tracking-widest"
              >
                DEPLOY
              </button>
              <button
                onClick={() => setShowAdd(false)}
                className="text-[10px] px-3 py-1.5 border border-t-border text-t-muted hover:text-t-text transition-colors tracking-widest"
              >
                CANCEL
              </button>
            </div>
          </div>
        )}

        <div className="p-4 space-y-4">
          <TargetsTable targets={targets} onToggle={toggleTarget} onDelete={deleteTarget} />
          <EventLog events={events} />
        </div>

      </div>
    </div>
  )
}

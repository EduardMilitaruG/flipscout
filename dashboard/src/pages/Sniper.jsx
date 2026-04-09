import { useState, useEffect } from 'react'
import { Plus, Pause, Play, Trash2, Shield, ShieldOff, RefreshCw } from 'lucide-react'

function ActionBadge({ action }) {
  const map = {
    messaged: 'bg-blue-500/20 text-blue-300',
    auto_bought: 'bg-emerald-500/20 text-emerald-300',
    alert_only: 'bg-gray-500/20 text-gray-300',
    skipped: 'bg-gray-700/40 text-gray-500',
  }
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${map[action] ?? 'bg-gray-700 text-gray-400'}`}>
      {action.replace('_', ' ')}
    </span>
  )
}

export default function Sniper() {
  const [targets, setTargets] = useState([])
  const [events, setEvents] = useState([])
  const [status, setStatus] = useState(null)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({
    id: '', query: '', category: 'general',
    platform: ['wallapop'], max_buy_price_eur: '',
    min_margin_pct: 20, auto_buy: false, reserve_on_match: true,
  })

  const fetchAll = async () => {
    try {
      const [t, e, s] = await Promise.all([
        fetch('/api/sniper/targets').then(r => r.json()),
        fetch('/api/sniper/events?limit=30').then(r => r.json()),
        fetch('/api/sniper/status').then(r => r.json()),
      ])
      setTargets(t)
      setEvents(e)
      setStatus(s)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchAll()
    const id = setInterval(fetchAll, 15_000)
    return () => clearInterval(id)
  }, [])

  const togglePause = async () => {
    const endpoint = status?.paused ? '/api/sniper/resume-all' : '/api/sniper/pause-all'
    await fetch(endpoint, { method: 'POST' })
    fetchAll()
  }

  const toggleTarget = async (id, active) => {
    await fetch(`/api/sniper/targets/${id}/toggle?active=${!active}`, { method: 'PATCH' })
    fetchAll()
  }

  const deleteTarget = async (id) => {
    await fetch(`/api/sniper/targets/${id}`, { method: 'DELETE' })
    fetchAll()
  }

  const createTarget = async () => {
    if (!form.id || !form.query || !form.max_buy_price_eur) return
    await fetch('/api/sniper/targets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, max_buy_price_eur: Number(form.max_buy_price_eur) }),
    })
    setShowAdd(false)
    setForm({ id: '', query: '', category: 'general', platform: ['wallapop'], max_buy_price_eur: '', min_margin_pct: 20, auto_buy: false, reserve_on_match: true })
    fetchAll()
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white">Sniper</h1>
        <div className="flex gap-2">
          <button onClick={fetchAll} className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-white px-3 py-1.5 rounded-lg border border-gray-700 transition-colors">
            <RefreshCw size={13} /> Refresh
          </button>
          <button
            onClick={togglePause}
            className={`flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border transition-colors ${
              status?.paused
                ? 'border-emerald-500 text-emerald-400 hover:bg-emerald-500/10'
                : 'border-yellow-500 text-yellow-400 hover:bg-yellow-500/10'
            }`}
          >
            {status?.paused ? <><Play size={13} /> Resume all</> : <><Pause size={13} /> Pause all</>}
          </button>
          <button
            onClick={() => setShowAdd(v => !v)}
            className="flex items-center gap-1.5 text-sm bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-lg transition-colors"
          >
            <Plus size={13} /> Add target
          </button>
        </div>
      </div>

      {/* Status bar */}
      {status && (
        <div className="flex items-center gap-6 bg-gray-900 border border-gray-800 rounded-xl px-5 py-3 text-sm">
          <span className="flex items-center gap-2">
            {status.paused ? <ShieldOff size={14} className="text-yellow-400" /> : <Shield size={14} className="text-emerald-400" />}
            <span className={status.paused ? 'text-yellow-400' : 'text-emerald-400'}>
              {status.paused ? 'PAUSED' : 'ACTIVE'}
            </span>
          </span>
          <span className="text-gray-400">
            Daily spend: <span className="text-white font-medium">€{status.daily_spend_eur?.toFixed(2)}</span>
            <span className="text-gray-500"> / €{status.daily_limit_eur}</span>
          </span>
          {Object.entries(status.sessions ?? {}).map(([platform, s]) => (
            <span key={platform} className="text-gray-400">
              {platform}:{' '}
              <span className={s.valid ? 'text-emerald-400' : 'text-red-400'}>
                {s.valid ? '✓ ok' : '✗ expired'}
              </span>
            </span>
          ))}
        </div>
      )}

      {/* Add target form */}
      {showAdd && (
        <div className="bg-gray-900 border border-emerald-500/30 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-emerald-400">New snipe target</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {[
              { label: 'ID', key: 'id', placeholder: 'snipe_ps5' },
              { label: 'Search query', key: 'query', placeholder: 'PS5 slim' },
              { label: 'Max price (€)', key: 'max_buy_price_eur', placeholder: '350', type: 'number' },
              { label: 'Min margin (%)', key: 'min_margin_pct', placeholder: '20', type: 'number' },
            ].map(({ label, key, placeholder, type }) => (
              <div key={key}>
                <label className="block text-xs text-gray-400 mb-1">{label}</label>
                <input
                  type={type ?? 'text'}
                  placeholder={placeholder}
                  value={form[key]}
                  onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-emerald-500"
                />
              </div>
            ))}
          </div>
          <div className="flex gap-4 items-center text-sm">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={form.reserve_on_match} onChange={e => setForm(p => ({ ...p, reserve_on_match: e.target.checked }))} className="accent-emerald-400" />
              <span className="text-gray-300">Message seller on match</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={form.auto_buy} onChange={e => setForm(p => ({ ...p, auto_buy: e.target.checked }))} className="accent-red-400" />
              <span className="text-red-400 font-medium">Auto-buy (Vinted only)</span>
            </label>
          </div>
          <div className="flex gap-2">
            <button onClick={createTarget} className="bg-emerald-600 hover:bg-emerald-500 text-white text-sm px-4 py-2 rounded-lg transition-colors">Create</button>
            <button onClick={() => setShowAdd(false)} className="text-gray-400 hover:text-white text-sm px-4 py-2 rounded-lg border border-gray-700 transition-colors">Cancel</button>
          </div>
        </div>
      )}

      {/* Targets table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-gray-800 text-xs text-gray-400 uppercase tracking-wide font-medium">
          Active targets ({targets.filter(t => t.active).length} / {targets.length})
        </div>
        {targets.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-10">No snipe targets. Add one above.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
                <th className="py-2 pl-5 text-left">Query</th>
                <th className="py-2 px-3 text-left">Platform</th>
                <th className="py-2 px-3 text-left">Max €</th>
                <th className="py-2 px-3 text-left">Min margin</th>
                <th className="py-2 px-3 text-left">Auto-buy</th>
                <th className="py-2 px-3 text-left">Status</th>
                <th className="py-2 pr-5" />
              </tr>
            </thead>
            <tbody>
              {targets.map(t => (
                <tr key={t.id} className="border-t border-gray-800 hover:bg-gray-800/40 transition-colors">
                  <td className="py-3 pl-5 font-medium text-gray-100">{t.query}</td>
                  <td className="py-3 px-3 text-gray-400">
                    {(Array.isArray(t.platform) ? t.platform : JSON.parse(t.platform)).join(', ')}
                  </td>
                  <td className="py-3 px-3 text-gray-300">€{t.max_buy_price_eur}</td>
                  <td className="py-3 px-3 text-gray-300">{t.min_margin_pct}%</td>
                  <td className="py-3 px-3">
                    {t.auto_buy ? <span className="text-red-400 text-xs font-bold">ON</span> : <span className="text-gray-500 text-xs">off</span>}
                  </td>
                  <td className="py-3 px-3">
                    <span className={`text-xs font-medium ${t.active ? 'text-emerald-400' : 'text-gray-500'}`}>
                      {t.active ? '● active' : '○ paused'}
                    </span>
                  </td>
                  <td className="py-3 pr-5">
                    <div className="flex items-center gap-2 justify-end">
                      <button onClick={() => toggleTarget(t.id, t.active)} className="text-gray-400 hover:text-yellow-400 transition-colors">
                        {t.active ? <Pause size={14} /> : <Play size={14} />}
                      </button>
                      <button onClick={() => deleteTarget(t.id)} className="text-gray-400 hover:text-red-400 transition-colors">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Event history */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-gray-800 text-xs text-gray-400 uppercase tracking-wide font-medium">
          Recent snipe events
        </div>
        {events.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-8">No events yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
                <th className="py-2 pl-5 text-left">Item</th>
                <th className="py-2 px-3 text-left">Platform</th>
                <th className="py-2 px-3 text-left">Price</th>
                <th className="py-2 px-3 text-left">Margin</th>
                <th className="py-2 px-3 text-left">Action</th>
                <th className="py-2 pr-5 text-right text-left">Time</th>
              </tr>
            </thead>
            <tbody>
              {events.map(e => (
                <tr key={e.id} className="border-t border-gray-800 hover:bg-gray-800/30 transition-colors">
                  <td className="py-2.5 pl-5 max-w-xs">
                    <a href={e.listing_url} target="_blank" rel="noopener noreferrer"
                       className="text-gray-200 hover:text-emerald-400 truncate block transition-colors">
                      {e.listing_title?.slice(0, 60)}
                    </a>
                  </td>
                  <td className="py-2.5 px-3 text-gray-400 capitalize">{e.platform}</td>
                  <td className="py-2.5 px-3 text-gray-300">€{e.listing_price_eur?.toFixed(2)}</td>
                  <td className="py-2.5 px-3 text-gray-400">
                    {e.calc_margin_pct != null ? `${e.calc_margin_pct.toFixed(1)}%` : '—'}
                  </td>
                  <td className="py-2.5 px-3"><ActionBadge action={e.action} /></td>
                  <td className="py-2.5 pr-5 text-gray-500 text-xs text-right">
                    {new Date(e.occurred_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

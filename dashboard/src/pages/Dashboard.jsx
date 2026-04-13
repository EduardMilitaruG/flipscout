import { useState, useEffect, useCallback } from 'react'
import { RefreshCw } from 'lucide-react'
import StatsBar from '../components/StatsBar'
import FiltersSidebar from '../components/FiltersSidebar'
import DealsTable from '../components/DealsTable'

const POLL_MS = 60_000

export default function Dashboard() {
  const [deals,    setDeals]    = useState([])
  const [stats,    setStats]    = useState(null)
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState(null)
  const [lastSync, setLastSync] = useState(null)
  const [filters,  setFilters]  = useState({
    category: '', minMargin: 0, marketplace: '', highConfidence: false,
  })

  const fetchData = useCallback(async () => {
    try {
      setError(null)
      const params = new URLSearchParams()
      if (filters.category)       params.set('category',        filters.category)
      if (filters.minMargin > 0)  params.set('min_margin',      filters.minMargin)
      if (filters.marketplace)    params.set('marketplace',     filters.marketplace)
      if (filters.highConfidence) params.set('high_confidence', 'true')

      const [dealsRes, statsRes] = await Promise.all([
        fetch(`/api/deals?${params}`),
        fetch('/api/stats/today'),
      ])
      if (dealsRes.ok) setDeals(await dealsRes.json())
      if (statsRes.ok) setStats(await statsRes.json())
      setLastSync(new Date())
    } catch {
      setError('Cannot reach API — is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, POLL_MS)
    return () => clearInterval(id)
  }, [fetchData])

  return (
    <div className="flex flex-col h-full">

      {/* ── PAGE HEADER ───────────────────────────────── */}
      <div className="flex items-center justify-between px-5 py-2.5 border-b border-t-border bg-t-surface shrink-0">
        <div className="flex items-center gap-3">
          {/* Big condensed page title, moodboard-style */}
          <span className="font-display font-black text-2xl text-t-white tracking-tight leading-none">
            DEALS
          </span>
          <span className="font-mono text-[10px] text-t-dim">│</span>
          <span className="font-mono text-[10px] text-t-muted">{deals.length} ACTIVE</span>
          {lastSync && (
            <>
              <span className="font-mono text-[10px] text-t-dim">│</span>
              <span className="font-mono text-[10px] text-t-muted">
                SYNC {lastSync.toLocaleTimeString()}
              </span>
            </>
          )}
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 font-mono text-[10px] text-t-muted hover:text-t-text border border-t-border px-2 py-1 transition-colors hover:border-t-line"
        >
          <RefreshCw size={11} />
          REFRESH
        </button>
      </div>

      {/* ── STATS STRIP ───────────────────────────────── */}
      {stats && (
        <div className="shrink-0 border-b border-t-border">
          <StatsBar stats={stats} />
        </div>
      )}

      {/* ── ERROR BANNER ──────────────────────────────── */}
      {error && (
        <div className="px-4 py-2 bg-red-950/40 border-b border-t-red text-t-red text-[11px] flex items-center gap-2 shrink-0">
          <span>⚠</span> {error}
        </div>
      )}

      {/* ── BODY ──────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">

        {/* Filter panel */}
        <div className="shrink-0 overflow-y-auto">
          <FiltersSidebar filters={filters} onChange={setFilters} />
        </div>

        {/* Deals area */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              {/* Big number as graphic element — moodboard "3" style */}
              <div className="font-display font-black text-[120px] leading-none text-t-border select-none">
                …
              </div>
              <div className="font-mono text-[10px] text-t-muted tracking-widest">LOADING DATA</div>
            </div>
          ) : deals.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              <div className="font-display font-black text-[120px] leading-none text-t-border select-none">
                0
              </div>
              <div className="font-mono text-[10px] text-t-muted tracking-widest">NO DEALS FOUND</div>
              <div className="font-mono text-[9px] text-t-dim">ADJUST FILTERS OR WAIT FOR NEXT SCAN</div>
            </div>
          ) : (
            <DealsTable deals={deals} />
          )}
        </div>

      </div>
    </div>
  )
}

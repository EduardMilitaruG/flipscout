import { useState, useEffect, useCallback } from 'react'
import { TrendingUp, Package, Star, RefreshCw } from 'lucide-react'
import StatsBar from '../components/StatsBar'
import FiltersSidebar from '../components/FiltersSidebar'
import DealsTable from '../components/DealsTable'

const POLL_INTERVAL = 60_000 // 60 seconds

export default function Dashboard() {
  const [deals, setDeals] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    category: '',
    minMargin: 0,
    marketplace: '',
    highConfidence: false,
  })

  const fetchData = useCallback(async () => {
    try {
      const params = new URLSearchParams()
      if (filters.category) params.set('category', filters.category)
      if (filters.minMargin > 0) params.set('min_margin', filters.minMargin)
      if (filters.marketplace) params.set('marketplace', filters.marketplace)
      if (filters.highConfidence) params.set('high_confidence', 'true')

      const [dealsRes, statsRes] = await Promise.all([
        fetch(`/api/deals?${params}`),
        fetch('/api/stats/today'),
      ])

      if (dealsRes.ok) setDeals(await dealsRes.json())
      if (statsRes.ok) setStats(await statsRes.json())
    } catch (err) {
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, POLL_INTERVAL)
    return () => clearInterval(id)
  }, [fetchData])

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white">Active Deals</h1>
        <button
          onClick={fetchData}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {stats && <StatsBar stats={stats} />}

      <div className="flex gap-6">
        <FiltersSidebar filters={filters} onChange={setFilters} />
        <div className="flex-1 min-w-0">
          {loading ? (
            <div className="text-gray-500 text-sm py-12 text-center">Loading deals…</div>
          ) : deals.length === 0 ? (
            <div className="text-gray-500 text-sm py-12 text-center">No deals found. Try adjusting the filters.</div>
          ) : (
            <DealsTable deals={deals} />
          )}
        </div>
      </div>
    </div>
  )
}

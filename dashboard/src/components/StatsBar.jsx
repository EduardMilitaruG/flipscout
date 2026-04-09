import { TrendingUp, Package, Star } from 'lucide-react'

export default function StatsBar({ stats }) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <StatCard
        icon={Package}
        label="Deals today"
        value={stats.total_deals_today ?? '—'}
        color="text-blue-400"
      />
      <StatCard
        icon={TrendingUp}
        label="Avg margin"
        value={stats.avg_margin_pct != null ? `${stats.avg_margin_pct.toFixed(1)}%` : '—'}
        color="text-emerald-400"
      />
      <StatCard
        icon={Star}
        label="Best deal"
        value={
          stats.best_deal
            ? `€${stats.best_deal.gross_margin_eur?.toFixed(0)} (${stats.best_deal.margin_pct?.toFixed(1)}%)`
            : '—'
        }
        color="text-yellow-400"
        sub={stats.best_deal?.title?.slice(0, 40)}
      />
    </div>
  )
}

function StatCard({ icon: Icon, label, value, color, sub }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon size={15} className={color} />
        <span className="text-xs text-gray-400 uppercase tracking-wide">{label}</span>
      </div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-1 truncate">{sub}</div>}
    </div>
  )
}

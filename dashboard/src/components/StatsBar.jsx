export default function StatsBar({ stats }) {
  const dealsCount = stats?.total_deals_today ?? 21
  const avgMargin = stats?.avg_margin_pct != null ? `${stats.avg_margin_pct.toFixed(1)}%` : '33.4%'
  const bestDeal = stats?.best_deal

  return (
    <div className="grid grid-cols-4 bg-t-bg border-b border-t-border">
      {/* 01 DEALS TODAY */}
      <div className="bg-t-surface border-r border-t-border p-3.5 relative cross-matrix">
        <div className="font-mono text-[9px] text-t-dim mb-0.5">+ 01</div>
        <div className="font-mono text-[9px] text-t-muted tracking-widest uppercase">DEALS_TODAY</div>
        <div className="font-display font-black text-4xl text-t-orange tracking-tight my-1 leading-none">
          {dealsCount}
        </div>
        <div className="font-mono text-[9px] text-t-dim">! scanned today</div>
      </div>

      {/* 02 AVG MARGIN */}
      <div className="bg-t-surface border-r border-t-border p-3.5 relative">
        <div className="font-mono text-[9px] text-t-dim mb-0.5">+ 02</div>
        <div className="font-mono text-[9px] text-t-muted tracking-widest uppercase">AVG_MARGIN</div>
        <div className="font-display font-black text-4xl text-t-green tracking-tight my-1 leading-none">
          {avgMargin}
        </div>
        <div className="font-mono text-[9px] text-t-dim">gross pct all deals</div>
      </div>

      {/* 03 BEST DEAL (Solid royal blue card from original design) */}
      <div className="bg-[#1d4ed8] border-r border-blue-600 p-3.5 text-white relative">
        <div className="font-mono text-[9px] text-blue-200/60 mb-0.5">+ 03</div>
        <div className="font-mono text-[9px] text-blue-100 tracking-widest uppercase">BEST_DEAL</div>
        <div className="font-display font-black text-4xl text-white tracking-tight my-1 leading-none">
          {bestDeal ? `€${bestDeal.gross_margin_eur?.toFixed(0)}` : '€118'}
        </div>
        <div className="font-mono text-[9px] text-blue-200/90 truncate">
          {bestDeal
            ? `${bestDeal.margin_pct?.toFixed(1)}% · ${bestDeal.title}`
            : '42.1% · PSA10 リザードン VMAX SA 068/19'}
        </div>
      </div>

      {/* 04 TOP PLATFORM */}
      <div className="bg-t-surface p-3.5 relative">
        <div className="font-mono text-[9px] text-t-dim mb-0.5">+ 04</div>
        <div className="font-mono text-[9px] text-t-muted tracking-widest uppercase">TOP_PLATFORM</div>
        <div className="font-display font-black text-4xl text-white tracking-tight my-1 leading-none">
          MERCARI
        </div>
        <div className="font-mono text-[9px] text-t-dim">by deal count today</div>
      </div>
    </div>
  )
}

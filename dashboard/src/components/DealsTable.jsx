import { useState } from 'react'
import { ExternalLink, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'

function marginColor(pct) {
  if (pct >= 30) return 'text-emerald-400'
  if (pct >= 15) return 'text-yellow-400'
  return 'text-red-400'
}

function marginBg(pct) {
  if (pct >= 30) return 'bg-emerald-500/10 border-emerald-500/30'
  if (pct >= 15) return 'bg-yellow-500/10 border-yellow-500/30'
  return 'bg-red-500/10 border-red-500/30'
}

function ConfidenceDot({ confidence }) {
  const map = { high: 'bg-blue-400', medium: 'bg-yellow-400', low: 'bg-gray-500' }
  return (
    <span className="flex items-center gap-1 text-xs text-gray-400">
      <span className={`w-2 h-2 rounded-full inline-block ${map[confidence] ?? 'bg-gray-600'}`} />
      {confidence}
    </span>
  )
}

function DealRow({ deal }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <>
      <tr
        className="border-t border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors"
        onClick={() => setExpanded(v => !v)}
      >
        <td className="py-3 pl-4 pr-2 max-w-xs">
          <div className="flex items-start gap-2">
            {deal.thumbnail && (
              <img
                src={deal.thumbnail}
                alt=""
                className="w-10 h-10 rounded object-cover shrink-0 mt-0.5"
                onError={e => { e.target.style.display = 'none' }}
              />
            )}
            <div className="min-w-0">
              <div className="text-sm font-medium text-gray-100 truncate">{deal.title}</div>
              <div className="text-xs text-gray-500 mt-0.5">
                {deal.category} · {deal.marketplace?.replace('_', ' ')}
              </div>
            </div>
          </div>
        </td>
        <td className="py-3 px-3 text-sm text-gray-300 whitespace-nowrap">
          ¥{Number(deal.price_jpy).toLocaleString()}
          <div className="text-xs text-gray-500">€{deal.jp_price_eur?.toFixed(2)}</div>
        </td>
        <td className="py-3 px-3 text-sm text-gray-300">
          €{deal.spanish_resale_eur?.toFixed(2)}
          <div className="mt-0.5"><ConfidenceDot confidence={deal.confidence} /></div>
        </td>
        <td className="py-3 px-3">
          <span className={`inline-flex items-center gap-1 text-sm font-bold ${marginColor(deal.margin_pct)}`}>
            {deal.is_risky && <AlertTriangle size={12} className="text-yellow-500" />}
            {deal.margin_pct?.toFixed(1)}%
          </span>
          <div className="text-xs text-gray-400">€{deal.gross_margin_eur?.toFixed(2)}</div>
        </td>
        <td className="py-3 px-3">
          <a
            href={deal.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-emerald-400 hover:text-emerald-300 transition-colors"
            onClick={e => e.stopPropagation()}
          >
            <ExternalLink size={15} />
          </a>
        </td>
        <td className="py-3 pr-4 text-gray-600">
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </td>
      </tr>

      {expanded && (
        <tr className="border-t border-gray-800 bg-gray-900/60">
          <td colSpan={6} className="py-4 px-6">
            <div className={`rounded-lg border p-4 text-sm space-y-2 ${marginBg(deal.margin_pct)}`}>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <CostLine label="JP buy price" value={`€${deal.jp_price_eur?.toFixed(2)}`} />
                <CostLine label="Shipping (EMS)" value={`€${deal.shipping_eur?.toFixed(2)}`} />
                <CostLine label="Platform fee" value={`€${deal.platform_fee_eur?.toFixed(2)}`} />
                <CostLine label="ES resale (median)" value={`€${deal.spanish_resale_eur?.toFixed(2)}`} bold />
              </div>
              <div className={`font-bold mt-2 ${marginColor(deal.margin_pct)}`}>
                Gross profit: €{deal.gross_margin_eur?.toFixed(2)} ({deal.margin_pct?.toFixed(1)}%)
                {deal.is_risky && (
                  <span className="ml-2 text-yellow-400 font-normal text-xs">
                    ⚠️ Shipping exceeds 40% of gross margin
                  </span>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Found: {new Date(deal.seen_at).toLocaleString()} ·
                Comparables: {deal.comparable_count} ({deal.confidence} confidence)
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  )
}

function CostLine({ label, value, bold }) {
  return (
    <div>
      <div className="text-xs text-gray-400">{label}</div>
      <div className={`text-gray-100 ${bold ? 'font-bold' : ''}`}>{value}</div>
    </div>
  )
}

export default function DealsTable({ deals }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="text-xs text-gray-400 uppercase tracking-wide">
            <th className="py-3 pl-4 pr-2 text-left">Item</th>
            <th className="py-3 px-3 text-left">JP Price</th>
            <th className="py-3 px-3 text-left">ES Resale</th>
            <th className="py-3 px-3 text-left">Margin</th>
            <th className="py-3 px-3 text-left">Link</th>
            <th className="py-3 pr-4" />
          </tr>
        </thead>
        <tbody>
          {deals.map((deal, i) => <DealRow key={deal.url ?? i} deal={deal} />)}
        </tbody>
      </table>
    </div>
  )
}

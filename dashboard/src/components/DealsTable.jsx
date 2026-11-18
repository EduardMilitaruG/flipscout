import { useState } from 'react'
import { ExternalLink } from 'lucide-react'

// ── Margin tier ────────────────────────────────────────────────────────────

function tier(pct) {
  if (pct >= 30) return 'high'
  if (pct >= 15) return 'mid'
  return 'low'
}

const TIER_STYLE = {
  high: { leftBorder: 'border-l-2 border-l-t-orange', numColor: 'text-t-orange', dot: 'bg-t-orange' },
  mid:  { leftBorder: 'border-l-2 border-l-[#f59e0b]',  numColor: 'text-[#f59e0b]',  dot: 'bg-[#f59e0b]'  },
  low:  { leftBorder: 'border-l-2 border-l-t-dim',    numColor: 'text-t-red',    dot: 'bg-t-red'    },
}

const CONF_COLOR = {
  high:   'text-t-green',
  medium: 'text-[#f59e0b]',
  low:    'text-t-muted',
}

function fmt(n, d = 2) { return n != null ? n.toFixed(d) : '—' }

function getBadge(deal) {
  const kw = (deal.keyword || '').toLowerCase()
  const title = (deal.title || '').toLowerCase()
  if (kw.includes('airpods') || title.includes('airpods')) return 'APs'
  if (kw.includes('xm5') || title.includes('xm5') || title.includes('wh-1000')) return 'XM5'
  if (kw.includes('switch') || title.includes('switch')) return 'NSW'
  if (title.includes('anker')) return 'ANK'
  if (title.includes('x100')) return 'X100'
  if (kw.includes('ps5') || title.includes('ps5')) return 'PS5'
  if (title.includes('rog')) return 'ROG'
  if (title.includes('deck')) return 'SD'
  if (title.includes('quest')) return 'MQ3'
  if (title.includes('7c') || title.includes('alpha') || title.includes('α7')) return 'a7C'
  if (deal.category === 'pokemon') return 'PKM'
  return (deal.category || 'FS').slice(0, 3).toUpperCase()
}

// ── Deal Row ───────────────────────────────────────────────────────────────

function DealRow({ deal, index }) {
  const [open, setOpen] = useState(false)
  const t = tier(deal.margin_pct)
  const { leftBorder, numColor } = TIER_STYLE[t]
  const isHighValue = deal.margin_pct >= 30
  const badge = getBadge(deal)
  const marginStr = deal.margin_pct != null
    ? String(deal.margin_pct.toFixed(1)).padStart(5, '0') + '%'
    : '—'

  return (
    <>
      <tr
        className={`deal-row border-t border-t-border cursor-pointer transition-colors hover:bg-t-panel ${leftBorder} ${isHighValue ? 'bg-t-orange/[0.04]' : ''}`}
        onClick={() => setOpen(v => !v)}
      >
        {/* Row index + Tag Badge */}
        <td className="py-2.5 pl-3 pr-2 w-14 select-none">
          <div className="flex items-center gap-1.5 font-mono text-[9px]">
            <span className="text-t-dim">{String(index + 1).padStart(2, '0')}</span>
            <span className="bg-[#121212] border border-[#222] text-[#888] px-1 py-0.5 text-[8px] font-bold">
              {badge}
            </span>
          </div>
        </td>

        {/* Item */}
        <td className="py-2.5 pr-3">
          <div className="min-w-0 pr-4">
            <div className="text-xs text-t-text truncate max-w-[340px] font-mono font-medium leading-tight">
              {deal.title}
            </div>
            <div className="font-mono text-[9px] text-t-muted mt-0.5 uppercase tracking-wide">
              {deal.category} · {deal.marketplace?.replace('_', ' ')}
            </div>
          </div>
        </td>

        {/* JP Price */}
        <td className="py-2.5 px-3 text-right">
          <div className="font-mono text-xs text-t-text">¥{Number(deal.price_jpy).toLocaleString()}</div>
          <div className="font-mono text-[9px] text-t-muted">€{fmt(deal.jp_price_eur)}</div>
        </td>

        {/* ES Resale — cyan/blue accent */}
        <td className="py-2.5 px-3 text-right">
          <div className="font-mono text-xs text-t-blue font-medium">€{fmt(deal.spanish_resale_eur)}</div>
          <div className={`font-mono text-[9px] ${CONF_COLOR[deal.confidence] ?? 'text-t-muted'}`}>
            {deal.confidence?.toUpperCase() ?? '—'}
          </div>
        </td>

        {/* Margin — big Barlow display number */}
        <td className="py-2.5 px-3 text-right">
          <div className={`font-display font-black text-2xl leading-none tracking-tight ${numColor}`}>
            {deal.is_risky && <span className="text-[#f59e0b] text-sm mr-0.5">!</span>}
            {marginStr}
          </div>
          <div className="font-mono text-[9px] text-t-muted">€{fmt(deal.gross_margin_eur)}</div>
        </td>

        {/* Link */}
        <td className="py-2.5 px-2 w-6 text-center">
          <a
            href={deal.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-t-dim hover:text-t-blue transition-colors inline-block"
            onClick={e => e.stopPropagation()}
          >
            <ExternalLink size={12} />
          </a>
        </td>

        {/* Expand toggle */}
        <td className="py-2.5 pr-3 w-6 font-mono text-[8px] text-t-dim text-right select-none">
          {open ? '▲' : '▼'}
        </td>
      </tr>

      {/* Expanded row — ticket / pass aesthetic */}
      {open && (
        <tr className={`border-t border-t-border ${leftBorder}`}>
          <td colSpan={7} className="p-0">
            <div className="bg-t-surface border-b border-t-border flex">

              {/* Left: cost breakdown */}
              <div className="flex-1 px-8 py-3 grid grid-cols-5 gap-4">
                <CostLine label="JP BUY"        value={`€${fmt(deal.jp_price_eur)}`}           />
                <CostLine label="SHIPPING"      value={`€${fmt(deal.shipping_eur)}`}            />
                <CostLine label="PLATFORM FEE"  value={`€${fmt(deal.platform_fee_eur)}`}        />
                <CostLine label="ES RESALE"     value={`€${fmt(deal.spanish_resale_eur)}`} blue />
                <CostLine
                  label="NET PROFIT"
                  value={`€${fmt(deal.gross_margin_eur)}`}
                  sub={`${fmt(deal.margin_pct, 1)}%`}
                  orange={deal.margin_pct >= 30}
                />
              </div>

              {/* Right: ticket stub (perforated edge + serial) */}
              <div className="ticket-edge-l px-4 py-3 flex flex-col items-center justify-center gap-1 min-w-[100px] bg-t-bg">
                <div className="font-mono text-[9px] text-t-muted tracking-widest">COMPARABLES</div>
                <div className="font-display font-black text-3xl text-t-text leading-none">
                  {deal.comparable_count ?? '—'}
                </div>
                <div className={`font-mono text-[9px] ${CONF_COLOR[deal.confidence]}`}>
                  {deal.confidence?.toUpperCase()}
                </div>
                {deal.is_risky && (
                  <div className="font-mono text-[9px] text-[#f59e0b] mt-1">⚠ RISKY</div>
                )}
              </div>
            </div>

            {/* Meta strip */}
            <div className="px-8 py-1.5 border-b border-t-border bg-t-bg flex gap-6 font-mono text-[10px] text-t-muted">
              <span>SEEN {new Date(deal.seen_at).toLocaleString()}</span>
              <span className="text-t-dim">│</span>
              <span>SN: {deal.url?.slice(-12).toUpperCase().replace(/[^A-Z0-9]/g, '-')}</span>
            </div>
          </td>
        </tr>
      )}
    </>
  )
}

function CostLine({ label, value, sub, blue, orange }) {
  return (
    <div className="border-l border-t-border pl-3">
      <div className="font-mono text-[9px] text-t-muted tracking-widest mb-0.5">{label}</div>
      <div className={`font-mono text-xs ${blue ? 'text-t-blue' : orange ? 'text-t-orange' : 'text-t-text'}`}>
        {value}
      </div>
      {sub && <div className={`font-mono text-[10px] ${orange ? 'text-t-orange' : 'text-t-muted'}`}>{sub}</div>}
    </div>
  )
}

// ── Table ──────────────────────────────────────────────────────────────────

export default function DealsTable({ deals }) {
  return (
    <div className="border border-t-border bg-t-surface overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-t-border bg-t-panel select-none">
            <th className="py-2 pl-3 w-14" />
            <th className="py-2 pr-3 text-left font-mono text-[9px] text-t-muted tracking-widest">ITEM</th>
            <th className="py-2 px-3 text-right font-mono text-[9px] text-t-muted tracking-widest">JP PRICE</th>
            <th className="py-2 px-3 text-right font-mono text-[9px] text-t-blue tracking-widest">RESALE</th>
            <th className="py-2 px-3 text-right font-mono text-[9px] text-t-muted tracking-widest">MARGIN</th>
            <th className="py-2 px-2 w-6" />
            <th className="py-2 pr-3 w-6" />
          </tr>
        </thead>
        <tbody>
          {deals.map((deal, i) => (
            <DealRow key={deal.id ?? deal.url} deal={deal} index={i} />
          ))}
        </tbody>
      </table>
    </div>
  )
}

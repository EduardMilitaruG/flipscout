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
  mid:  { leftBorder: 'border-l-2 border-l-t-amber',  numColor: 'text-t-amber',  dot: 'bg-t-amber'  },
  low:  { leftBorder: 'border-l-2 border-l-t-dim',    numColor: 'text-t-red',    dot: 'bg-t-red'    },
}

const CONF_COLOR = {
  high:   'text-t-green',
  medium: 'text-t-amber',
  low:    'text-t-muted',
}

function fmt(n, d = 2) { return n != null ? n.toFixed(d) : '—' }

// ── Deal Row ───────────────────────────────────────────────────────────────

function DealRow({ deal, index }) {
  const [open, setOpen] = useState(false)
  const t = tier(deal.margin_pct)
  const { leftBorder, numColor, dot } = TIER_STYLE[t]
  const isHighValue = deal.margin_pct >= 30

  return (
    <>
      <tr
        className={`deal-row border-t border-t-border cursor-pointer ${leftBorder} ${isHighValue ? 'bg-t-orange/[0.03]' : ''}`}
        onClick={() => setOpen(v => !v)}
      >
        {/* Row index */}
        <td className="py-2 pl-3 pr-1 w-8">
          <span className="font-mono text-[10px] text-t-dim">{String(index + 1).padStart(2, '0')}</span>
        </td>

        {/* Item */}
        <td className="py-2 pr-3">
          <div className="flex items-center gap-2">
            {deal.thumbnail && (
              <img
                src={deal.thumbnail}
                alt=""
                className="w-7 h-7 object-cover shrink-0 grayscale opacity-70"
                onError={e => { e.target.style.display = 'none' }}
              />
            )}
            <div className="min-w-0">
              <div className="text-sm text-t-text truncate max-w-[240px] font-body font-medium leading-tight">
                {deal.title}
              </div>
              <div className="font-mono text-[10px] text-t-muted mt-0.5">
                {deal.category?.toUpperCase()} · {deal.marketplace?.replace('_', ' ').toUpperCase()}
              </div>
            </div>
          </div>
        </td>

        {/* JP Price */}
        <td className="py-2 px-3 text-right">
          <div className="font-mono text-xs text-t-text">¥{Number(deal.price_jpy).toLocaleString()}</div>
          <div className="font-mono text-[10px] text-t-muted">€{fmt(deal.jp_price_eur)}</div>
        </td>

        {/* ES Resale — blue accent (ARC-Division style) */}
        <td className="py-2 px-3 text-right">
          <div className="font-mono text-xs text-t-blue font-medium">€{fmt(deal.spanish_resale_eur)}</div>
          <div className={`font-mono text-[10px] ${CONF_COLOR[deal.confidence] ?? 'text-t-muted'}`}>
            {deal.confidence?.toUpperCase() ?? '—'}
          </div>
        </td>

        {/* Margin — big Barlow display number */}
        <td className="py-2 px-3 text-right">
          <div className={`font-display font-black text-2xl leading-none ${numColor}`}>
            {deal.is_risky && <span className="text-t-amber text-sm mr-0.5">!</span>}
            {fmt(deal.margin_pct, 1)}%
          </div>
          <div className="font-mono text-[10px] text-t-muted">€{fmt(deal.gross_margin_eur)}</div>
        </td>

        {/* Link */}
        <td className="py-2 px-2">
          <a
            href={deal.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-t-sub hover:text-t-blue transition-colors"
            onClick={e => e.stopPropagation()}
          >
            <ExternalLink size={13} />
          </a>
        </td>

        {/* Expand toggle */}
        <td className="py-2 pr-3 font-mono text-[10px] text-t-dim text-right">
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
                  <div className="font-mono text-[9px] text-t-amber mt-1">⚠ RISKY</div>
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
          <tr className="border-b border-t-border bg-t-panel">
            <th className="py-2 pl-3 w-8" />
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

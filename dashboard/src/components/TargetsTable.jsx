import { Pause, Play, Trash2 } from 'lucide-react'

function parsePlatform(raw) {
  if (Array.isArray(raw)) return raw
  try { return JSON.parse(raw) } catch { return [raw] }
}

export default function TargetsTable({ targets, onToggle, onDelete }) {
  const activeCount = targets.filter(t => t.active).length

  return (
    <div className="border border-t-border bg-t-surface">

      <div className="px-4 py-2 border-b border-t-border flex items-center justify-between">
        <span className="text-[9px] text-t-amber tracking-widest">// ACTIVE_TARGETS</span>
        <span className="text-[9px] text-t-muted">{activeCount} / {targets.length} ARMED</span>
      </div>

      {targets.length === 0 ? (
        <div className="text-t-muted text-xs text-center py-10 tracking-widest">
          NO TARGETS — ADD ONE ABOVE
        </div>
      ) : (
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-t-border">
              {['QUERY', 'PLATFORM', 'MAX €', 'MIN MARGIN', 'AUTO-BUY', 'STATUS', ''].map((h, i) => (
                <th key={i} className="py-1.5 px-3 first:pl-4 last:pr-4 text-[9px] text-t-muted tracking-widest text-left">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {targets.map(t => (
              <TargetRow
                key={t.id}
                target={t}
                onToggle={() => onToggle(t.id, t.active)}
                onDelete={() => onDelete(t.id)}
              />
            ))}
          </tbody>
        </table>
      )}

    </div>
  )
}

function TargetRow({ target: t, onToggle, onDelete }) {
  const platforms = parsePlatform(t.platform)

  return (
    <tr className="border-t border-t-border hover:bg-t-panel transition-colors">
      <td className="py-2 pl-4 pr-3 text-t-text">{t.query}</td>
      <td className="py-2 px-3 text-t-muted">{platforms.join(', ').toUpperCase()}</td>
      <td className="py-2 px-3 text-t-text">€{t.max_buy_price_eur}</td>
      <td className="py-2 px-3 text-t-muted">{t.min_margin_pct}%</td>
      <td className="py-2 px-3">
        {t.auto_buy
          ? <span className="text-t-red">ON</span>
          : <span className="text-t-dim">off</span>}
      </td>
      <td className="py-2 px-3">
        <span className={t.active ? 'text-t-green' : 'text-t-muted'}>
          {t.active ? '● active' : '○ paused'}
        </span>
      </td>
      <td className="py-2 pl-3 pr-4">
        <div className="flex items-center gap-3 justify-end">
          <button
            onClick={onToggle}
            className="text-t-muted hover:text-t-amber transition-colors"
            title={t.active ? 'Pause' : 'Resume'}
          >
            {t.active ? <Pause size={12} /> : <Play size={12} />}
          </button>
          <button
            onClick={onDelete}
            className="text-t-muted hover:text-t-red transition-colors"
            title="Delete"
          >
            <Trash2 size={12} />
          </button>
        </div>
      </td>
    </tr>
  )
}

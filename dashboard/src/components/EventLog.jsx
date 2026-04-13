const ACTION_STYLE = {
  messaged:    'text-t-cyan',
  auto_bought: 'text-t-green',
  alert_only:  'text-t-muted',
  skipped:     'text-t-dim',
}

function ActionLabel({ action }) {
  return (
    <span className={`text-[10px] uppercase tracking-wider ${ACTION_STYLE[action] ?? 'text-t-muted'}`}>
      {action?.replace('_', ' ') ?? '—'}
    </span>
  )
}

export default function EventLog({ events }) {
  return (
    <div className="border border-t-border bg-t-surface">

      <div className="px-4 py-2 border-b border-t-border">
        <span className="text-[9px] text-t-amber tracking-widest">// SNIPE_EVENT_LOG</span>
      </div>

      {events.length === 0 ? (
        <div className="text-t-muted text-xs text-center py-8 tracking-widest">
          NO EVENTS YET
        </div>
      ) : (
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-t-border">
              {['ITEM', 'PLATFORM', 'PRICE', 'MARGIN', 'ACTION', 'TIME'].map((h, i) => (
                <th
                  key={i}
                  className={`py-1.5 px-3 first:pl-4 last:pr-4 text-[9px] text-t-muted tracking-widest ${i === 5 ? 'text-right' : 'text-left'}`}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {events.map(e => (
              <tr key={e.id} className="border-t border-t-border hover:bg-t-panel transition-colors">
                <td className="py-2 pl-4 pr-3 max-w-[240px]">
                  <a
                    href={e.listing_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-t-text hover:text-t-cyan truncate block transition-colors"
                  >
                    {e.listing_title?.slice(0, 55)}
                  </a>
                </td>
                <td className="py-2 px-3 text-t-muted">{e.platform?.toUpperCase()}</td>
                <td className="py-2 px-3 text-t-text">€{e.listing_price_eur?.toFixed(2)}</td>
                <td className="py-2 px-3 text-t-muted">
                  {e.calc_margin_pct != null ? `${e.calc_margin_pct.toFixed(1)}%` : '—'}
                </td>
                <td className="py-2 px-3">
                  <ActionLabel action={e.action} />
                </td>
                <td className="py-2 pl-3 pr-4 text-t-muted text-[10px] text-right">
                  {new Date(e.occurred_at).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

    </div>
  )
}

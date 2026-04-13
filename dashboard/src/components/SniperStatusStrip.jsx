export default function SniperStatusStrip({ status }) {
  if (!status) return null

  const isRunning = !status.paused

  return (
    <div className="border-b border-t-border bg-t-surface grid grid-cols-4 divide-x divide-t-border text-xs">

      <StatusCell label="ENGINE">
        <span className={isRunning ? 'text-t-green' : 'text-t-amber'}>
          {isRunning ? '● RUNNING' : '■ PAUSED'}
        </span>
      </StatusCell>

      <StatusCell label="DAILY_SPEND">
        <span className="text-t-text">
          €{status.daily_spend_eur?.toFixed(2)}
          <span className="text-t-muted"> / €{status.daily_limit_eur}</span>
        </span>
      </StatusCell>

      {Object.entries(status.sessions ?? {}).map(([platform, s]) => (
        <StatusCell key={platform} label={`${platform.toUpperCase()}_SESSION`}>
          <span className={s.valid ? 'text-t-green' : 'text-t-red'}>
            {s.valid ? '✓ VALID' : '✗ EXPIRED'}
          </span>
        </StatusCell>
      ))}

    </div>
  )
}

function StatusCell({ label, children }) {
  return (
    <div className="px-4 py-2.5">
      <div className="text-[9px] text-t-muted tracking-widest mb-0.5">{label}</div>
      <div className="text-xs">{children}</div>
    </div>
  )
}

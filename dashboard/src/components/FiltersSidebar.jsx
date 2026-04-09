export default function FiltersSidebar({ filters, onChange }) {
  const set = (key, val) => onChange(prev => ({ ...prev, [key]: val }))

  return (
    <aside className="w-52 shrink-0 space-y-5">
      <div>
        <label className="block text-xs text-gray-400 uppercase tracking-wide mb-2">Category</label>
        <select
          value={filters.category}
          onChange={e => set('category', e.target.value)}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All</option>
          <option value="tech">Tech</option>
          <option value="fashion">Fashion</option>
          <option value="pokemon">Pokémon</option>
          <option value="general">General</option>
        </select>
      </div>

      <div>
        <label className="block text-xs text-gray-400 uppercase tracking-wide mb-2">
          Min margin: <span className="text-emerald-400 font-semibold">{filters.minMargin}%</span>
        </label>
        <input
          type="range"
          min={0}
          max={80}
          step={5}
          value={filters.minMargin}
          onChange={e => set('minMargin', Number(e.target.value))}
          className="w-full accent-emerald-400"
        />
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>0%</span><span>80%</span>
        </div>
      </div>

      <div>
        <label className="block text-xs text-gray-400 uppercase tracking-wide mb-2">Marketplace</label>
        <select
          value={filters.marketplace}
          onChange={e => set('marketplace', e.target.value)}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All</option>
          <option value="zenmarket">ZenMarket (Yahoo)</option>
          <option value="mercari_jp">Mercari Japan</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <input
          id="hc"
          type="checkbox"
          checked={filters.highConfidence}
          onChange={e => set('highConfidence', e.target.checked)}
          className="accent-emerald-400 w-4 h-4"
        />
        <label htmlFor="hc" className="text-sm text-gray-300 cursor-pointer">
          High confidence only
        </label>
      </div>
    </aside>
  )
}

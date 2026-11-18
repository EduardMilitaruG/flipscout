import { Plus } from 'lucide-react'

export default function FiltersSidebar({ filters, onChange }) {
  const set = (key, val) => onChange(prev => ({ ...prev, [key]: val }))

  return (
    <aside className="w-48 shrink-0 bg-[#090909] border-r border-t-border p-3.5 space-y-4.5 font-mono select-none min-h-full">
      {/* Header */}
      <div className="flex items-center justify-between text-t-orange pb-1">
        <span className="text-[10px] font-bold tracking-widest">// FILTERS</span>
        <Plus size={12} className="cursor-pointer hover:text-white transition-colors" />
      </div>

      {/* Category */}
      <div>
        <label className="block text-[9px] text-t-muted tracking-widest mb-1.5 uppercase">
          Category
        </label>
        <select
          value={filters.category}
          onChange={e => set('category', e.target.value)}
          className="w-full bg-[#111111] border border-t-border text-t-text px-2 py-1.5 text-xs font-mono focus:outline-none focus:border-t-orange cursor-pointer rounded-none"
        >
          <option value="">ALL</option>
          <option value="tech">TECH</option>
          <option value="fashion">FASHION</option>
          <option value="pokemon">POKÉMON</option>
          <option value="general">GENERAL</option>
        </select>
      </div>

      {/* Source / Marketplace */}
      <div>
        <label className="block text-[9px] text-t-muted tracking-widest mb-1.5 uppercase">
          Source
        </label>
        <select
          value={filters.marketplace}
          onChange={e => set('marketplace', e.target.value)}
          className="w-full bg-[#111111] border border-t-border text-t-text px-2 py-1.5 text-xs font-mono focus:outline-none focus:border-t-orange cursor-pointer rounded-none"
        >
          <option value="">ALL</option>
          <option value="zenmarket">YAHOO AUC.</option>
          <option value="mercari_jp">MERCARI JP</option>
        </select>
      </div>

      {/* Min Margin */}
      <div>
        <div className="flex items-center justify-between text-[9px] text-t-muted tracking-widest mb-1.5">
          <span>MIN MARGIN</span>
          <span className="text-t-orange font-bold">{filters.minMargin}%</span>
        </div>
        <input
          type="range"
          min={0}
          max={80}
          step={5}
          value={filters.minMargin}
          onChange={e => set('minMargin', Number(e.target.value))}
          className="w-full accent-[#ff5500] cursor-pointer"
        />
        <div className="flex justify-between text-[9px] text-t-dim mt-1">
          <span>0%</span>
          <span>80%</span>
        </div>
      </div>

      {/* High Confidence Only */}
      <div className="pt-1">
        <label
          htmlFor="hc"
          className="flex items-center gap-2 text-[9px] text-t-muted hover:text-t-text cursor-pointer tracking-wider"
        >
          <input
            id="hc"
            type="checkbox"
            checked={filters.highConfidence}
            onChange={e => set('highConfidence', e.target.checked)}
            className="accent-[#ff5500] w-3.5 h-3.5 rounded-none bg-[#111111] border-t-border"
          />
          <span>HIGH CONF. ONLY</span>
        </label>
      </div>

      {/* Decorative Barcode / Terminal Stamp */}
      <div className="pt-6 opacity-30 select-none">
        <div className="flex gap-[2px] h-6 items-end">
          <span className="w-1 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-1.5 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-2 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-1 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-2 bg-white h-full inline-block"></span>
          <span className="w-1 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-1.5 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-1 bg-white h-full inline-block"></span>
          <span className="w-2 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-1 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
          <span className="w-1.5 bg-white h-full inline-block"></span>
          <span className="w-0.5 bg-white h-full inline-block"></span>
        </div>
        <div className="text-[7px] text-t-dim tracking-[0.25em] mt-1 font-mono">
          JP-FLIP-SEC-098
        </div>
      </div>
    </aside>
  )
}

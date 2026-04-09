import { Routes, Route, NavLink } from 'react-router-dom'
import { LayoutDashboard, Crosshair, Activity } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Sniper from './pages/Sniper'

const nav = [
  { to: '/', label: 'Deals', icon: LayoutDashboard },
  { to: '/sniper', label: 'Sniper', icon: Crosshair },
]

export default function App() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col py-6 px-4 gap-1 shrink-0">
        <div className="flex items-center gap-2 mb-8 px-2">
          <Activity className="text-emerald-400" size={22} />
          <span className="font-bold text-lg tracking-tight text-white">FlipScout</span>
        </div>
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/sniper" element={<Sniper />} />
        </Routes>
      </main>
    </div>
  )
}

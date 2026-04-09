"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Search,
  Settings,
  Clock,
  Zap,
  X,
  Activity,
  SlidersHorizontal,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useArchiveStore } from "@/store/use-archive-store";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/keywords", label: "Keywords", icon: Search },
  { href: "/settings", label: "Search Settings", icon: SlidersHorizontal },
  { href: "/config", label: "Bot Config", icon: Settings },
  { href: "/history", label: "Deal History", icon: Clock },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { stats } = useArchiveStore();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-50 h-full w-60 flex-col border-r border-white/[0.07] bg-[#080810] transition-transform duration-300 md:translate-x-0 md:flex",
          open ? "translate-x-0 flex" : "-translate-x-full flex"
        )}
      >
        {/* Logo */}
        <div className="flex h-14 items-center justify-between px-4 border-b border-white/[0.07]">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-600 to-purple-900 flex items-center justify-center shadow-lg shadow-purple-500/30">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-white leading-none">Archive Scout</p>
              <p className="text-[10px] text-purple-400 leading-none mt-0.5">Control Panel</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="md:hidden p-1 rounded hover:bg-white/5 text-white/50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Bot status */}
        <div className="mx-3 mt-3 rounded-lg border border-white/[0.07] bg-white/[0.03] p-3">
          <div className="flex items-center gap-2">
            <div className={cn(
              "w-2 h-2 rounded-full",
              stats.botRunning
                ? "bg-green-400 shadow-[0_0_8px_2px_rgba(74,222,128,0.4)]"
                : "bg-red-400"
            )} />
            <span className="text-xs font-medium text-white/70">
              Bot {stats.botRunning ? "Running" : "Stopped"}
            </span>
          </div>
          <div className="mt-2 grid grid-cols-2 gap-1">
            <div className="text-center rounded-md bg-white/[0.03] px-1 py-1">
              <p className="text-xs font-bold text-purple-300">{stats.dealsFoundToday}</p>
              <p className="text-[10px] text-white/40">deals</p>
            </div>
            <div className="text-center rounded-md bg-white/[0.03] px-1 py-1">
              <p className="text-xs font-bold text-purple-300">{stats.alertsSentToday}</p>
              <p className="text-[10px] text-white/40">alerts</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-3 space-y-0.5">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 group",
                  isActive
                    ? "sidebar-item-active text-purple-300 font-medium"
                    : "text-white/50 hover:text-white/80 hover:bg-white/[0.04]"
                )}
              >
                <Icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive ? "text-purple-400" : "text-white/30 group-hover:text-white/60"
                  )}
                />
                {label}
                {isActive && (
                  <div className="ml-auto w-1 h-1 rounded-full bg-purple-400" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-white/[0.07]">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg bg-white/[0.02]">
            <Activity className="w-3 h-3 text-purple-400" />
            <span className="text-[11px] text-white/40">
              v1.0.0 · ZenMarket scraper
            </span>
          </div>
        </div>
      </aside>
    </>
  );
}

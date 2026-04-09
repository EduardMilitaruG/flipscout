"use client";

import { TrendingUp, Search, Bell, Zap } from "lucide-react";
import { Card } from "@/components/ui/card";
import { useArchiveStore } from "@/store/use-archive-store";
import { cn } from "@/lib/utils";

export function StatsGrid() {
  const { stats } = useArchiveStore();

  const items = [
    {
      label: "Keywords Tracked",
      value: stats.keywordsTracked,
      sub: "10 total configured",
      icon: Search,
      color: "text-purple-400",
      bg: "bg-purple-500/10",
    },
    {
      label: "Deals Found Today",
      value: stats.dealsFoundToday,
      sub: `${stats.listingsScrapedToday.toLocaleString()} listings scraped`,
      icon: TrendingUp,
      color: "text-green-400",
      bg: "bg-green-500/10",
    },
    {
      label: "Alerts Sent",
      value: stats.alertsSentToday,
      sub: "Telegram + Discord",
      icon: Bell,
      color: "text-sky-400",
      bg: "bg-sky-500/10",
    },
    {
      label: "Avg. Discount",
      value: `${stats.avgDiscountPct}%`,
      sub: "Below market value",
      icon: Zap,
      color: "text-orange-400",
      bg: "bg-orange-500/10",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <Card
            key={item.label}
            className="p-4 hover:border-white/[0.12] transition-all duration-200 hover:-translate-y-0.5 group cursor-default"
          >
            <div className="flex items-start justify-between">
              <div className="min-w-0">
                <p className="text-xs text-white/40 mb-1 truncate">{item.label}</p>
                <p className="text-2xl font-bold text-white leading-none">{item.value}</p>
                <p className="text-[11px] text-white/30 mt-1.5 truncate">{item.sub}</p>
              </div>
              <div className={cn("p-2 rounded-lg flex-shrink-0 ml-2", item.bg)}>
                <Icon className={cn("w-4 h-4", item.color)} />
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}

"use client";

import { useState } from "react";
import { useArchiveStore } from "@/store/use-archive-store";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { formatJpy, formatUsd, timeAgo } from "@/lib/utils";
import { Search, ExternalLink } from "lucide-react";

export function HistoryTable() {
  const alerts = useArchiveStore((s) => s.alerts);
  const [search, setSearch] = useState("");

  const filtered = alerts.filter(
    (a) =>
      a.title.toLowerCase().includes(search.toLowerCase()) ||
      a.keyword.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
        <Input
          placeholder="Search deals by title or keyword…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.06]">
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40">Item</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40 hidden sm:table-cell">Price</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40 hidden md:table-cell">Discount</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40 hidden sm:table-cell">Source</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40">Platforms</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40 hidden lg:table-cell">Time</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-white/40">Link</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((alert) => (
                <tr key={alert.id} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-white/90 font-medium leading-snug max-w-xs truncate">
                        {alert.title}
                      </p>
                      <p className="text-[11px] text-white/35 mt-0.5 truncate">{alert.keyword}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden sm:table-cell">
                    <p className="text-white/80 font-medium">{formatJpy(alert.priceJpy)}</p>
                    <p className="text-[11px] text-white/35">{formatUsd(alert.priceUsd)}</p>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <Badge
                      variant={alert.dealScore === "fire" ? "fire" : alert.dealScore === "hot" ? "hot" : "good"}
                    >
                      -{alert.discountPct}%
                    </Badge>
                  </td>
                  <td className="px-4 py-3 hidden sm:table-cell">
                    <Badge variant={alert.source === "mercari" ? "mercari" : "yahoo"}>
                      {alert.source === "mercari" ? "Mercari" : "Yahoo"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      {alert.platforms.includes("telegram") && (
                        <Badge variant="telegram">TG</Badge>
                      )}
                      {alert.platforms.includes("discord") && (
                        <Badge variant="discord">DC</Badge>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell text-white/35 text-xs">
                    {timeAgo(alert.sentAt)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <a
                      href={alert.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded-md hover:bg-white/5 text-white/25 hover:text-purple-400 transition-colors inline-flex"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-white/25 text-sm">
                    No deals found matching your search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

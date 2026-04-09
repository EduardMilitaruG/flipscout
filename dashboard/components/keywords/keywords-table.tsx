"use client";

import { useState } from "react";
import { useArchiveStore } from "@/store/use-archive-store";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Trash2, Clock, TrendingUp, TestTube } from "lucide-react";
import { formatUsd, timeAgo } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { KeywordCategory, Keyword } from "@/types";
import toast from "react-hot-toast";

const CATEGORIES: { value: KeywordCategory | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "undercover", label: "Undercover" },
  { value: "number-nine", label: "Number Nine" },
  { value: "kapital", label: "Kapital" },
  { value: "issey", label: "Issey Miyake" },
  { value: "yohji", label: "Yohji" },
  { value: "cdg", label: "CDG" },
  { value: "other", label: "Other" },
];

export function KeywordsTable() {
  const { keywords, toggleKeyword, removeKeyword, simulateNewDeal } = useArchiveStore();
  const [filter, setFilter] = useState<KeywordCategory | "all">("all");
  const [testing, setTesting] = useState<string | null>(null);

  const filtered =
    filter === "all" ? keywords : keywords.filter((k) => k.category === filter);

  async function handleTestScrape(kw: Keyword) {
    setTesting(kw.id);
    await new Promise((r) => setTimeout(r, 1500));
    simulateNewDeal();
    toast.success(`Test scrape for "${kw.term}" found a deal!`, {
      style: {
        background: "#0d0d14",
        color: "#fff",
        border: "1px solid rgba(147,51,234,0.3)",
      },
    });
    setTesting(null);
  }

  return (
    <div className="space-y-4">
      {/* Filter */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setFilter(cat.value)}
            className={cn(
              "px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 border",
              filter === cat.value
                ? "bg-purple-600/30 text-purple-300 border-purple-500/40"
                : "bg-white/[0.03] text-white/40 border-white/[0.06] hover:bg-white/[0.06] hover:text-white/70"
            )}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.06]">
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40">Keyword</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40 hidden sm:table-cell">Market Value</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40 hidden md:table-cell">Deals Found</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-white/40 hidden lg:table-cell">Last Scraped</th>
                <th className="text-center px-4 py-3 text-xs font-medium text-white/40">Active</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-white/40">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((kw) => (
                <tr
                  key={kw.id}
                  className={cn(
                    "border-b border-white/[0.04] transition-colors",
                    kw.enabled ? "hover:bg-white/[0.02]" : "opacity-50"
                  )}
                >
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-white/90 text-sm">{kw.term}</p>
                      <Badge variant="purple" className="mt-1 text-[10px]">
                        {kw.category}
                      </Badge>
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden sm:table-cell">
                    <div>
                      <p className="text-white/70">{formatUsd(kw.marketValueUsd)}</p>
                      <p className="text-[11px] text-white/30">
                        max {formatUsd(kw.maxPriceUsd)} · -{kw.dealThresholdPct}% threshold
                      </p>
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <div className="flex items-center gap-1.5">
                      <TrendingUp className="w-3 h-3 text-purple-400" />
                      <span className="text-white/70">{kw.dealsFound}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    <div className="flex items-center gap-1.5 text-white/40 text-xs">
                      <Clock className="w-3 h-3" />
                      {kw.lastScraped ? timeAgo(kw.lastScraped) : "Never"}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Switch
                      checked={kw.enabled}
                      onCheckedChange={() => toggleKeyword(kw.id)}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleTestScrape(kw)}
                        disabled={testing === kw.id}
                        className="h-7 text-xs px-2"
                      >
                        {testing === kw.id ? (
                          <span className="animate-pulse">Testing…</span>
                        ) : (
                          <>
                            <TestTube className="w-3 h-3 mr-1" />
                            Test
                          </>
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeKeyword(kw.id)}
                        className="h-7 w-7 text-white/20 hover:text-red-400 hover:bg-red-500/10"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

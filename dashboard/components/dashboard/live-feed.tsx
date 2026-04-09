"use client";

import { useArchiveStore } from "@/store/use-archive-store";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { formatJpy, formatUsd, timeAgo } from "@/lib/utils";
import { ExternalLink, Flame, Zap, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DealAlert } from "@/types";

function DealScoreIcon({ score }: { score: DealAlert["dealScore"] }) {
  if (score === "fire") return <Flame className="w-3.5 h-3.5 text-orange-400" />;
  if (score === "hot") return <Zap className="w-3.5 h-3.5 text-yellow-400" />;
  return <CheckCircle className="w-3.5 h-3.5 text-green-400" />;
}

export function LiveFeed() {
  const alerts = useArchiveStore((s) => s.alerts);

  return (
    <Card>
      <CardHeader className="pb-0 flex-row items-center justify-between">
        <CardTitle className="text-sm font-semibold text-white/80">
          Live Deal Feed
        </CardTitle>
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-[11px] text-white/30">Live</span>
        </div>
      </CardHeader>
      <CardContent className="pt-3">
        <div className="space-y-2 max-h-[340px] overflow-y-auto pr-0.5">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={cn(
                "rounded-xl border p-3 transition-all duration-300",
                alert.isNew
                  ? "border-purple-500/40 bg-purple-500/5 animate-fade-in"
                  : "border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04]"
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2 min-w-0">
                  <DealScoreIcon score={alert.dealScore} />
                  <div className="min-w-0">
                    <p className="text-sm text-white font-medium leading-snug truncate">
                      {alert.title}
                    </p>
                    <p className="text-[11px] text-white/40 mt-0.5">
                      {alert.keyword}
                    </p>
                  </div>
                </div>
                <a
                  href={alert.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 p-1 rounded hover:bg-white/5 text-white/20 hover:text-white/60 transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              <div className="flex items-center justify-between mt-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-bold text-white">
                    {formatJpy(alert.priceJpy)}
                  </span>
                  <span className="text-[11px] text-white/30">
                    ~{formatUsd(alert.priceUsd)}
                  </span>
                  <Badge variant={alert.dealScore === "fire" ? "fire" : alert.dealScore === "hot" ? "hot" : "good"}>
                    -{alert.discountPct}%
                  </Badge>
                </div>
                <span className="text-[10px] text-white/25 flex-shrink-0">
                  {timeAgo(alert.sentAt)}
                </span>
              </div>

              <div className="flex items-center gap-1.5 mt-2">
                <Badge variant={alert.source === "mercari" ? "mercari" : "yahoo"}>
                  {alert.source === "mercari" ? "Mercari" : "Yahoo"}
                </Badge>
                {alert.platforms.includes("telegram") && (
                  <Badge variant="telegram">TG</Badge>
                )}
                {alert.platforms.includes("discord") && (
                  <Badge variant="discord">DC</Badge>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

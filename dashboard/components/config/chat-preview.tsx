"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { generateDemoAlert } from "@/lib/fake-data";
import { formatJpy, formatUsd } from "@/lib/utils";
import type { DealAlert } from "@/types";
import { cn } from "@/lib/utils";

interface ChatPreviewProps {
  platform: "telegram" | "discord";
  triggerKey: number;
}

export function ChatPreview({ platform, triggerKey }: ChatPreviewProps) {
  const [messages, setMessages] = useState<DealAlert[]>([]);
  const [typing, setTyping] = useState(false);

  useEffect(() => {
    if (triggerKey === 0) return;
    setTyping(true);
    const t = setTimeout(() => {
      setTyping(false);
      setMessages((prev) => [generateDemoAlert(), ...prev].slice(0, 5));
    }, 1200);
    return () => clearTimeout(t);
  }, [triggerKey]);

  const isTG = platform === "telegram";

  return (
    <Card className={cn("overflow-hidden", isTG ? "border-sky-500/10" : "border-indigo-500/10")}>
      {/* Header */}
      <div className={cn(
        "px-4 py-3 border-b",
        isTG ? "bg-sky-950/30 border-sky-500/10" : "bg-indigo-950/30 border-indigo-500/10"
      )}>
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold",
            isTG ? "bg-sky-500" : "bg-indigo-500"
          )}>
            {isTG ? "✈" : "⚡"}
          </div>
          <div>
            <p className="text-xs font-semibold text-white">
              {isTG ? "Archive Scout Bot" : "archive-scout"}
            </p>
            <p className={cn("text-[10px]", isTG ? "text-sky-400" : "text-indigo-400")}>
              {isTG ? "Telegram" : "Discord"} Preview
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="p-3 space-y-2 min-h-[200px] max-h-[280px] overflow-y-auto bg-black/20">
        {messages.length === 0 && !typing && (
          <div className="flex items-center justify-center h-32 text-white/20 text-xs">
            Press &quot;Send Test Message&quot; →
          </div>
        )}

        {typing && (
          <div className={cn(
            "rounded-xl p-3 text-xs max-w-[85%] animate-fade-in",
            isTG ? "bg-sky-950/60 border border-sky-500/20" : "bg-indigo-950/60 border border-indigo-500/20"
          )}>
            <div className="flex gap-1 items-center">
              <div className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: "0ms" }} />
              <div className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: "150ms" }} />
              <div className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              "rounded-xl p-3 text-xs max-w-[90%] animate-fade-in",
              isTG ? "bg-sky-950/50 border border-sky-500/15" : "bg-indigo-950/50 border border-indigo-500/15"
            )}
          >
            <p className={cn("font-semibold mb-1 text-[11px]", isTG ? "text-sky-300" : "text-indigo-300")}>
              {isTG ? "🔍 Archive Scout Deal" : "**Archive Scout Deal** 🔍"}
            </p>
            <p className="text-white/80 font-medium leading-snug">{msg.title}</p>
            <p className="text-white/50 mt-1">
              💴 {formatJpy(msg.priceJpy)} · ~{formatUsd(msg.priceUsd)}
            </p>
            <p className="text-green-400 text-[11px]">
              📉 {msg.discountPct}% below market
            </p>
            <p className={cn("text-[10px] mt-1 truncate", isTG ? "text-sky-500/70" : "text-indigo-500/70")}>
              zenmarket.jp/en/auction.aspx?...
            </p>
          </div>
        ))}
      </div>
    </Card>
  );
}

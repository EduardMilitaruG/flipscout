"use client";

import { Menu, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useArchiveStore } from "@/store/use-archive-store";
import toast from "react-hot-toast";
import { formatJpy } from "@/lib/utils";

interface TopbarProps {
  onMenuClick: () => void;
  title: string;
}

export function Topbar({ onMenuClick, title }: TopbarProps) {
  const simulateNewDeal = useArchiveStore((s) => s.simulateNewDeal);

  function handleDemo() {
    const deal = simulateNewDeal();
    toast.custom(
      () => (
        <div className="animate-fade-in rounded-xl border border-purple-500/30 bg-[#0d0d14] p-4 shadow-2xl shadow-purple-500/20 max-w-sm w-full">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-purple-900 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-purple-300 mb-0.5">New Deal Found!</p>
              <p className="text-sm text-white font-medium leading-snug truncate">
                {deal.title}
              </p>
              <p className="text-xs text-white/50 mt-1">
                {formatJpy(deal.priceJpy)} · {deal.discountPct}% below market
              </p>
              <div className="flex gap-1.5 mt-2">
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/20">TG</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/20">DC</span>
              </div>
            </div>
          </div>
        </div>
      ),
      { duration: 5000, position: "bottom-right" }
    );
  }

  return (
    <header className="sticky top-0 z-30 h-14 border-b border-white/[0.07] bg-[#080810]/80 backdrop-blur-xl flex items-center justify-between px-4">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-lg hover:bg-white/5 text-white/50 hover:text-white transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h1 className="text-sm font-semibold text-white/80">{title}</h1>
      </div>

      <Button
        onClick={handleDemo}
        className="gap-2 bg-gradient-to-r from-purple-700 to-purple-500 hover:from-purple-600 hover:to-purple-400 text-white text-xs font-semibold px-4 py-2 h-8 rounded-lg shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-200 border border-purple-400/20"
      >
        <Sparkles className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Simulate Deal</span>
        <span className="sm:hidden">Demo</span>
      </Button>
    </header>
  );
}

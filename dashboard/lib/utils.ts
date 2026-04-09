import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { DealScore } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatJpy(amount: number): string {
  return new Intl.NumberFormat("ja-JP", {
    style: "currency",
    currency: "JPY",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatUsd(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function timeAgo(dateString: string): string {
  const now = Date.now();
  const then = new Date(dateString).getTime();
  const diff = Math.floor((now - then) / 1000);

  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function dealScoreLabel(score: DealScore): string {
  switch (score) {
    case "fire": return "🔥 Fire Deal";
    case "hot": return "⚡ Hot Deal";
    case "good": return "✅ Good Deal";
  }
}

export function discountToDealScore(pct: number): DealScore {
  if (pct >= 60) return "fire";
  if (pct >= 40) return "hot";
  return "good";
}

export function randomId(): string {
  return Math.random().toString(36).substring(2, 10);
}

export function subMinutes(minutes: number): string {
  return new Date(Date.now() - minutes * 60 * 1000).toISOString();
}

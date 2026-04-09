"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  DealAlert,
  Keyword,
  BotConfig,
  DashboardStats,
  SearchSettings,
} from "@/types";
import {
  INITIAL_KEYWORDS,
  INITIAL_ALERTS,
  INITIAL_BOT_CONFIG,
  INITIAL_STATS,
  INITIAL_SEARCH_SETTINGS,
  generateDemoAlert,
} from "@/lib/fake-data";

interface ArchiveStore {
  // State
  keywords: Keyword[];
  alerts: DealAlert[];
  botConfig: BotConfig;
  searchSettings: SearchSettings;
  stats: DashboardStats;
  lastDemoAlert: DealAlert | null;

  // Keywords
  addKeyword: (kw: Omit<Keyword, "id" | "lastScraped" | "dealsFound">) => void;
  toggleKeyword: (id: string) => void;
  removeKeyword: (id: string) => void;
  updateKeyword: (id: string, updates: Partial<Keyword>) => void;

  // Bot config
  updateBotConfig: (config: Partial<BotConfig>) => void;

  // Search settings
  updateSearchSettings: (settings: Partial<SearchSettings>) => void;

  // Demo
  simulateNewDeal: () => DealAlert;

  // Stats
  refreshStats: () => void;
}

export const useArchiveStore = create<ArchiveStore>()(
  persist(
    (set, get) => ({
      keywords: INITIAL_KEYWORDS,
      alerts: INITIAL_ALERTS,
      botConfig: INITIAL_BOT_CONFIG,
      searchSettings: INITIAL_SEARCH_SETTINGS,
      stats: INITIAL_STATS,
      lastDemoAlert: null,

      addKeyword: (kw) => {
        const newKw: Keyword = {
          ...kw,
          id: `kw_${Date.now()}`,
          lastScraped: null,
          dealsFound: 0,
        };
        set((s) => ({ keywords: [...s.keywords, newKw] }));
      },

      toggleKeyword: (id) => {
        set((s) => ({
          keywords: s.keywords.map((k) =>
            k.id === id ? { ...k, enabled: !k.enabled } : k
          ),
        }));
      },

      removeKeyword: (id) => {
        set((s) => ({ keywords: s.keywords.filter((k) => k.id !== id) }));
      },

      updateKeyword: (id, updates) => {
        set((s) => ({
          keywords: s.keywords.map((k) =>
            k.id === id ? { ...k, ...updates } : k
          ),
        }));
      },

      updateBotConfig: (config) => {
        set((s) => ({
          botConfig: {
            telegram: { ...s.botConfig.telegram, ...config.telegram },
            discord: { ...s.botConfig.discord, ...config.discord },
          },
        }));
      },

      updateSearchSettings: (settings) => {
        set((s) => ({
          searchSettings: { ...s.searchSettings, ...settings },
        }));
      },

      simulateNewDeal: () => {
        const newAlert = generateDemoAlert();
        set((s) => ({
          alerts: [newAlert, ...s.alerts].slice(0, 50),
          lastDemoAlert: newAlert,
          stats: {
            ...s.stats,
            dealsFoundToday: s.stats.dealsFoundToday + 1,
            alertsSentToday: s.stats.alertsSentToday + 1,
          },
        }));
        return newAlert;
      },

      refreshStats: () => {
        const { alerts, keywords } = get();
        const today = new Date().toDateString();
        const todayAlerts = alerts.filter(
          (a) => new Date(a.sentAt).toDateString() === today
        );
        const avgDiscount =
          todayAlerts.length > 0
            ? Math.round(
                todayAlerts.reduce((sum, a) => sum + a.discountPct, 0) /
                  todayAlerts.length
              )
            : 0;

        set((s) => ({
          stats: {
            ...s.stats,
            keywordsTracked: keywords.filter((k) => k.enabled).length,
            dealsFoundToday: todayAlerts.length,
            alertsSentToday: todayAlerts.length,
            avgDiscountPct: avgDiscount || s.stats.avgDiscountPct,
          },
        }));
      },
    }),
    {
      name: "archive-scout-store",
      partialize: (s) => ({
        keywords: s.keywords,
        alerts: s.alerts,
        botConfig: s.botConfig,
        searchSettings: s.searchSettings,
        stats: s.stats,
      }),
    }
  )
);

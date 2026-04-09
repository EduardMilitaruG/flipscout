export type Platform = "telegram" | "discord";

export type DealScore = "fire" | "hot" | "good";

export type KeywordCategory =
  | "all"
  | "undercover"
  | "number-nine"
  | "kapital"
  | "issey"
  | "yohji"
  | "cdg"
  | "other";

export interface Keyword {
  id: string;
  term: string;
  category: KeywordCategory;
  marketValueUsd: number;
  dealThresholdPct: number;
  enabled: boolean;
  lastScraped: string | null;
  dealsFound: number;
  maxPriceUsd: number;
}

export interface DealAlert {
  id: string;
  title: string;
  keyword: string;
  priceJpy: number;
  priceUsd: number;
  marketValueUsd: number;
  discountPct: number;
  dealScore: DealScore;
  url: string;
  thumbnail: string | null;
  source: "mercari" | "yahoo";
  platforms: Platform[];
  sentAt: string;
  isNew?: boolean;
}

export interface BotConfig {
  telegram: {
    enabled: boolean;
    botToken: string;
    chatId: string;
    messageTemplate: string;
  };
  discord: {
    enabled: boolean;
    botToken: string;
    channelId: string;
    messageTemplate: string;
  };
}

export interface SearchSettings {
  maxPriceUsd: number;
  dealThresholdPct: number;
  checkIntervalMinutes: number;
  maxPages: number;
  excludeTerms: string[];
}

export interface DashboardStats {
  keywordsTracked: number;
  dealsFoundToday: number;
  alertsSentToday: number;
  avgDiscountPct: number;
  listingsScrapedToday: number;
  botRunning: boolean;
}

export interface ChartDataPoint {
  day: string;
  deals: number;
  alerts: number;
  scraped: number;
}

export interface BrandShare {
  name: string;
  value: number;
  color: string;
}

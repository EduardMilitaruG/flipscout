"use client";

import { Shell } from "@/components/layout/shell";
import { KeywordsTable } from "@/components/keywords/keywords-table";
import { AddKeywordModal } from "@/components/keywords/add-keyword-modal";
import { useArchiveStore } from "@/store/use-archive-store";

export default function KeywordsPage() {
  const keywords = useArchiveStore((s) => s.keywords);
  const enabled = keywords.filter((k) => k.enabled).length;

  return (
    <Shell title="Keywords">
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white">Search Keywords</h2>
            <p className="text-sm text-white/40 mt-0.5">
              {enabled} of {keywords.length} keywords active · ZenMarket (Yahoo Auctions JP + Mercari JP)
            </p>
          </div>
          <AddKeywordModal />
        </div>
        <KeywordsTable />
      </div>
    </Shell>
  );
}

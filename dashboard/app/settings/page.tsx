"use client";

import { Shell } from "@/components/layout/shell";
import { SearchSettingsForm } from "@/components/settings/search-settings-form";

export default function SettingsPage() {
  return (
    <Shell title="Search Settings">
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white">Search Settings</h2>
          <p className="text-sm text-white/40 mt-0.5">
            Configure the global scraper behaviour — price limits, deal thresholds, and exclusion filters
          </p>
        </div>

        <SearchSettingsForm />
      </div>
    </Shell>
  );
}

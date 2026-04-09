"use client";

import { useState } from "react";
import { Plus, X, Save, RotateCcw } from "lucide-react";
import { useArchiveStore } from "@/store/use-archive-store";
import { INITIAL_SEARCH_SETTINGS } from "@/lib/fake-data";

export function SearchSettingsForm() {
  const { searchSettings, updateSearchSettings } = useArchiveStore();

  const [form, setForm] = useState(searchSettings);
  const [newTerm, setNewTerm] = useState("");
  const [saved, setSaved] = useState(false);

  const isDirty = JSON.stringify(form) !== JSON.stringify(searchSettings);

  function handleSave() {
    updateSearchSettings(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function handleReset() {
    const defaults = INITIAL_SEARCH_SETTINGS;
    setForm(defaults);
    updateSearchSettings(defaults);
  }

  function addExcludeTerm() {
    const trimmed = newTerm.trim().toLowerCase();
    if (!trimmed || form.excludeTerms.includes(trimmed)) return;
    setForm((f) => ({ ...f, excludeTerms: [...f.excludeTerms, trimmed] }));
    setNewTerm("");
  }

  function removeExcludeTerm(term: string) {
    setForm((f) => ({ ...f, excludeTerms: f.excludeTerms.filter((t) => t !== term) }));
  }

  return (
    <div className="space-y-6">
      {/* Numeric settings */}
      <div className="rounded-xl border border-white/[0.07] bg-white/[0.03] p-5">
        <h3 className="text-sm font-semibold text-white/80 mb-4">Scraper Parameters</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <NumericField
            label="Max Price (USD)"
            description="Skip listings above this price"
            value={form.maxPriceUsd}
            min={0}
            max={5000}
            step={10}
            prefix="$"
            onChange={(v) => setForm((f) => ({ ...f, maxPriceUsd: v }))}
          />
          <NumericField
            label="Deal Threshold"
            description="Alert when discount exceeds this %"
            value={form.dealThresholdPct}
            min={5}
            max={90}
            step={5}
            suffix="%"
            onChange={(v) => setForm((f) => ({ ...f, dealThresholdPct: v }))}
          />
          <NumericField
            label="Check Interval"
            description="How often to run the scraper"
            value={form.checkIntervalMinutes}
            min={5}
            max={120}
            step={5}
            suffix=" min"
            onChange={(v) => setForm((f) => ({ ...f, checkIntervalMinutes: v }))}
          />
          <NumericField
            label="Pages Per Keyword"
            description="Pages scraped per search (~48 results each)"
            value={form.maxPages}
            min={1}
            max={10}
            step={1}
            onChange={(v) => setForm((f) => ({ ...f, maxPages: v }))}
          />
        </div>
      </div>

      {/* Exclude terms */}
      <div className="rounded-xl border border-white/[0.07] bg-white/[0.03] p-5">
        <h3 className="text-sm font-semibold text-white/80 mb-1">Exclude Terms</h3>
        <p className="text-xs text-white/40 mb-4">Listings containing any of these words are ignored</p>

        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={newTerm}
            onChange={(e) => setNewTerm(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addExcludeTerm()}
            placeholder="e.g. replica"
            className="flex-1 h-9 rounded-lg bg-white/[0.05] border border-white/[0.10] px-3 text-sm text-white placeholder-white/30 focus:outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/30"
          />
          <button
            onClick={addExcludeTerm}
            className="h-9 w-9 flex items-center justify-center rounded-lg bg-purple-600/20 border border-purple-500/30 text-purple-400 hover:bg-purple-600/30 transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {form.excludeTerms.map((term) => (
            <span
              key={term}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-red-500/10 border border-red-500/20 text-red-300"
            >
              {term}
              <button
                onClick={() => removeExcludeTerm(term)}
                className="hover:text-red-200 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          {form.excludeTerms.length === 0 && (
            <p className="text-xs text-white/30 italic">No exclusion terms set</p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={!isDirty}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
        >
          <Save className="w-4 h-4" />
          {saved ? "Saved!" : "Save Changes"}
        </button>
        <button
          onClick={handleReset}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-white/[0.10] text-white/50 hover:text-white/80 hover:border-white/20 text-sm transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          Reset to Defaults
        </button>
      </div>
    </div>
  );
}

interface NumericFieldProps {
  label: string;
  description: string;
  value: number;
  min: number;
  max: number;
  step: number;
  prefix?: string;
  suffix?: string;
  onChange: (v: number) => void;
}

function NumericField({ label, description, value, min, max, step, prefix, suffix, onChange }: NumericFieldProps) {
  return (
    <div className="space-y-2">
      <div>
        <label className="text-sm text-white/70 font-medium">{label}</label>
        <p className="text-xs text-white/30 mt-0.5">{description}</p>
      </div>
      <div className="flex items-center gap-3">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="flex-1 accent-purple-500"
        />
        <div className="w-20 h-8 flex items-center justify-center rounded-lg bg-white/[0.05] border border-white/[0.10] text-sm text-white font-mono">
          {prefix}{value}{suffix}
        </div>
      </div>
    </div>
  );
}

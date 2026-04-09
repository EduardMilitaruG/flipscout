"use client";

import { useState } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useArchiveStore } from "@/store/use-archive-store";
import { Plus } from "lucide-react";
import type { KeywordCategory } from "@/types";
import toast from "react-hot-toast";

const CATEGORIES: { value: KeywordCategory; label: string }[] = [
  { value: "undercover", label: "Undercover" },
  { value: "number-nine", label: "Number Nine" },
  { value: "kapital", label: "Kapital" },
  { value: "issey", label: "Issey Miyake" },
  { value: "yohji", label: "Yohji Yamamoto" },
  { value: "cdg", label: "Comme des Garçons" },
  { value: "other", label: "Other" },
];

export function AddKeywordModal() {
  const addKeyword = useArchiveStore((s) => s.addKeyword);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    term: "",
    category: "other" as KeywordCategory,
    marketValueUsd: "",
    maxPriceUsd: "350",
    dealThresholdPct: "30",
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.term.trim()) return;
    addKeyword({
      term: form.term.toLowerCase().trim(),
      category: form.category,
      marketValueUsd: Number(form.marketValueUsd) || 300,
      maxPriceUsd: Number(form.maxPriceUsd) || 350,
      dealThresholdPct: Number(form.dealThresholdPct) || 30,
      enabled: true,
    });
    toast.success(`Keyword "${form.term}" added!`, {
      style: { background: "#0d0d14", color: "#fff", border: "1px solid rgba(147,51,234,0.3)" },
    });
    setOpen(false);
    setForm({ term: "", category: "other", marketValueUsd: "", maxPriceUsd: "350", dealThresholdPct: "30" });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          Add Keyword
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Search Keyword</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label>Search Term</Label>
            <Input
              placeholder="e.g. undercover jacket"
              value={form.term}
              onChange={(e) => setForm((f) => ({ ...f, term: e.target.value }))}
              autoFocus
            />
            <p className="text-[11px] text-white/30">Used as-is in ZenMarket search query</p>
          </div>

          <div className="space-y-1.5">
            <Label>Brand Category</Label>
            <Select value={form.category} onValueChange={(v) => setForm((f) => ({ ...f, category: v as KeywordCategory }))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((c) => (
                  <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <Label>Market Value (USD)</Label>
              <Input
                type="number"
                placeholder="400"
                value={form.marketValueUsd}
                onChange={(e) => setForm((f) => ({ ...f, marketValueUsd: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Max Price (USD)</Label>
              <Input
                type="number"
                placeholder="350"
                value={form.maxPriceUsd}
                onChange={(e) => setForm((f) => ({ ...f, maxPriceUsd: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Deal % Threshold</Label>
              <Input
                type="number"
                placeholder="30"
                value={form.dealThresholdPct}
                onChange={(e) => setForm((f) => ({ ...f, dealThresholdPct: e.target.value }))}
              />
            </div>
          </div>

          <Button type="submit" className="w-full">Add Keyword</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

"use client";

// Playwright test: "should send test notification to Telegram"
import { useState } from "react";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useArchiveStore } from "@/store/use-archive-store";
import { Send, Eye, EyeOff } from "lucide-react";
import toast from "react-hot-toast";

const TEMPLATE_VARS = ["{{title}}", "{{price_jpy}}", "{{price_usd}}", "{{discount}}", "{{market_value}}", "{{keyword}}", "{{source}}", "{{url}}"];

interface PlatformConfigProps {
  platform: "telegram" | "discord";
  onTestSend: () => void;
}

export function PlatformConfig({ platform, onTestSend }: PlatformConfigProps) {
  const { botConfig, updateBotConfig } = useArchiveStore();
  const [showToken, setShowToken] = useState(false);
  const [sending, setSending] = useState(false);
  const cfg = botConfig[platform];

  function handleChange(key: string, value: string | boolean) {
    updateBotConfig({ [platform]: { ...cfg, [key]: value } });
  }

  async function handleTestSend() {
    setSending(true);
    await new Promise((r) => setTimeout(r, 1200));
    onTestSend();
    toast.success(`Test message sent to ${platform === "telegram" ? "Telegram" : "Discord"}!`, {
      style: { background: "#0d0d14", color: "#fff", border: "1px solid rgba(147,51,234,0.3)" },
    });
    setSending(false);
  }

  const isTelegram = platform === "telegram";
  const label = isTelegram ? "Telegram" : "Discord";
  const idLabel = isTelegram ? "Chat ID" : "Channel ID";
  const idKey = isTelegram ? "chatId" : "channelId";

  return (
    <Card className="p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={isTelegram ? "telegram" : "discord"} className="text-xs px-2 py-0.5">
            {label}
          </Badge>
          <span className="text-sm text-white/60">Notifications</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-white/40">{cfg.enabled ? "Enabled" : "Disabled"}</span>
          <Switch checked={cfg.enabled} onCheckedChange={(v) => handleChange("enabled", v)} />
        </div>
      </div>

      <div className="space-y-3">
        <div className="space-y-1.5">
          <Label>Bot Token</Label>
          <div className="relative">
            <Input
              type={showToken ? "text" : "password"}
              placeholder={isTelegram ? "1234567890:ABCdef..." : "MTIz..."}
              value={cfg.botToken}
              onChange={(e) => handleChange("botToken", e.target.value)}
              className="pr-9"
            />
            <button
              type="button"
              onClick={() => setShowToken(!showToken)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/70 transition-colors"
            >
              {showToken ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{idLabel}</Label>
          <Input
            placeholder={isTelegram ? "-100123456789" : "123456789012345678"}
            value={cfg[idKey as keyof typeof cfg] as string}
            onChange={(e) => handleChange(idKey, e.target.value)}
          />
        </div>

        <div className="space-y-1.5">
          <Label>Message Template</Label>
          <Textarea
            rows={5}
            value={cfg.messageTemplate}
            onChange={(e) => handleChange("messageTemplate", e.target.value)}
            className="font-mono text-xs"
          />
          <div className="flex flex-wrap gap-1 mt-1">
            {TEMPLATE_VARS.map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => handleChange("messageTemplate", cfg.messageTemplate + v)}
                className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 hover:bg-purple-500/20 transition-colors font-mono"
              >
                {v}
              </button>
            ))}
          </div>
        </div>
      </div>

      <Button
        onClick={handleTestSend}
        disabled={sending}
        className="w-full gap-2"
        variant="outline"
      >
        {sending ? (
          <span className="animate-pulse">Sending…</span>
        ) : (
          <>
            <Send className="w-3.5 h-3.5" />
            Send Test Message
          </>
        )}
      </Button>
    </Card>
  );
}

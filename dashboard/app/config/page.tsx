"use client";

import { useState } from "react";
import { Shell } from "@/components/layout/shell";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { PlatformConfig } from "@/components/config/platform-config";
import { ChatPreview } from "@/components/config/chat-preview";

export default function ConfigPage() {
  const [tgTrigger, setTgTrigger] = useState(0);
  const [dcTrigger, setDcTrigger] = useState(0);

  return (
    <Shell title="Bot Config">
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white">Bot Configuration</h2>
          <p className="text-sm text-white/40 mt-0.5">
            Manage Telegram and Discord notification settings
          </p>
        </div>

        <Tabs defaultValue="telegram">
          <TabsList>
            <TabsTrigger value="telegram">✈ Telegram</TabsTrigger>
            <TabsTrigger value="discord">⚡ Discord</TabsTrigger>
          </TabsList>

          <TabsContent value="telegram">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-2">
              <PlatformConfig platform="telegram" onTestSend={() => setTgTrigger((n) => n + 1)} />
              <ChatPreview platform="telegram" triggerKey={tgTrigger} />
            </div>
          </TabsContent>

          <TabsContent value="discord">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-2">
              <PlatformConfig platform="discord" onTestSend={() => setDcTrigger((n) => n + 1)} />
              <ChatPreview platform="discord" triggerKey={dcTrigger} />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Shell>
  );
}

import { Shell } from "@/components/layout/shell";
import { HistoryTable } from "@/components/history/history-table";

export default function HistoryPage() {
  return (
    <Shell title="Deal History">
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white">Deal History</h2>
          <p className="text-sm text-white/40 mt-0.5">
            All deals found and alerts sent by the bot
          </p>
        </div>
        <HistoryTable />
      </div>
    </Shell>
  );
}

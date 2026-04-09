import { Shell } from "@/components/layout/shell";
import { StatsGrid } from "@/components/dashboard/stats-grid";
import { DealsChart } from "@/components/dashboard/deals-chart";
import { BrandPieChart } from "@/components/dashboard/brand-pie-chart";
import { LiveFeed } from "@/components/dashboard/live-feed";

export default function DashboardPage() {
  return (
    <Shell title="Dashboard">
      <div className="space-y-5">
        <StatsGrid />

        <div className="flex flex-col lg:flex-row gap-4">
          <DealsChart />
          <BrandPieChart />
        </div>

        <LiveFeed />
      </div>
    </Shell>
  );
}

import type { MarketDashboardMockData } from "../types";
import { DashboardTopNav } from "./dashboard-top-nav";
import { IndexStrip } from "./index-strip";
import { MarketDashboardShell } from "./market-dashboard-shell";

type DashboardPageProps = {
  data: MarketDashboardMockData;
};

export function DashboardPage({ data }: DashboardPageProps) {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <DashboardTopNav />
      <IndexStrip indexes={data.indexes} />
      <MarketDashboardShell data={data} />
    </main>
  );
}

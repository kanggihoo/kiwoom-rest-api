import type { MarketDashboardMockData } from "../types";
import { DashboardIconRail } from "./dashboard-icon-rail";
import { MarketDetailGrid } from "./market-detail-grid";
import { MarketTablePanel } from "./market-table-panel";
import { PersonalInfoPanel } from "./personal-info-panel";
import { SelectedMarketPanel } from "./selected-market-panel";

type MarketDashboardShellProps = {
  data: MarketDashboardMockData;
};

export function MarketDashboardShell({ data }: MarketDashboardShellProps) {
  return (
    <section className="grid gap-3 px-5 py-3 xl:grid-cols-[minmax(640px,1.45fr)_minmax(420px,0.9fr)_304px_56px]">
      <MarketTablePanel markets={data.markets} />
      <SelectedMarketPanel
        market={data.selectedMarket}
        candles={data.candles}
        activeCandleUnit={data.activeCandleUnit}
      />
      <PersonalInfoPanel markets={data.markets} />
      <DashboardIconRail />
      <div className="xl:col-span-2">
        <MarketDetailGrid orderbook={data.orderbook} trades={data.trades} />
      </div>
    </section>
  );
}

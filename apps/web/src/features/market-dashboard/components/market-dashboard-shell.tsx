import type { MarketDashboardMockData } from "../types";
import { MarketDetailGrid } from "./market-detail-grid";
import { MarketDiscoveryPanel } from "./market-discovery-panel";
import { MarketTablePanel } from "./market-table-panel";
import { SelectedMarketPanel } from "./selected-market-panel";

type MarketDashboardShellProps = {
  data: MarketDashboardMockData;
};

export function MarketDashboardShell({ data }: MarketDashboardShellProps) {
  return (
    <section className="grid gap-3 px-5 py-3 xl:grid-cols-[minmax(0,74%)_minmax(360px,26%)]">
      <div className="flex min-w-0 flex-col gap-3">
        <SelectedMarketPanel
          market={data.selectedMarket}
          candles={data.candles}
          activeCandleUnit={data.activeCandleUnit}
        />
        <MarketDetailGrid orderbook={data.orderbook} trades={data.trades} />
        <MarketTablePanel markets={data.markets} />
      </div>
      <MarketDiscoveryPanel markets={data.markets} activeCategory={data.activeCategory} />
    </section>
  );
}

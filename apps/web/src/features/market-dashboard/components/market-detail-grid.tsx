import type { OrderbookRow, TradeRow } from "../types";
import { OrderbookPanel } from "./orderbook-panel";
import { RecentTradesPanel } from "./recent-trades-panel";

type MarketDetailGridProps = {
  orderbook: OrderbookRow[];
  trades: TradeRow[];
};

export function MarketDetailGrid({ orderbook, trades }: MarketDetailGridProps) {
  return (
    <section className="grid gap-3 lg:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.8fr)]">
      <OrderbookPanel rows={orderbook} />
      <RecentTradesPanel trades={trades} />
    </section>
  );
}

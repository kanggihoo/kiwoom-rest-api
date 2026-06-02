import type { MarketDashboardMockData } from "../types";
import { mockCandles } from "./candles";
import { mockIndexes } from "./indexes";
import { mockMarkets, mockSelectedMarket } from "./markets";
import { mockOrderbook } from "./orderbook";
import { mockTrades } from "./trades";

export const mockMarketDashboardData: MarketDashboardMockData = {
  selectedMarket: mockSelectedMarket,
  activeCandleUnit: "1d",
  activeCategory: "interest",
  indexes: mockIndexes,
  markets: mockMarkets,
  candles: mockCandles,
  orderbook: mockOrderbook,
  trades: mockTrades,
};

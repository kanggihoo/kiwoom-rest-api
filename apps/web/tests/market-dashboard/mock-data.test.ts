import { describe, expect, it } from "vitest";

import { mockMarketDashboardData } from "../../src/features/market-dashboard/mock/dashboard";

describe("market dashboard mock data", () => {
  it("contains one selected market that matches the selected summary", () => {
    const selectedRows = mockMarketDashboardData.markets.filter((market) => market.selected);

    expect(selectedRows).toHaveLength(1);
    expect(selectedRows[0].market).toBe(mockMarketDashboardData.selectedMarket.market);
  });

  it("contains ascending candle timestamps", () => {
    const times = mockMarketDashboardData.candles.map((candle) => candle.time);
    const sortedTimes = [...times].sort((a, b) => a - b);

    expect(times).toEqual(sortedTimes);
  });

  it("keeps orderbook depth ratios in percent bounds", () => {
    for (const row of mockMarketDashboardData.orderbook) {
      expect(row.depthRatio).toBeGreaterThanOrEqual(0);
      expect(row.depthRatio).toBeLessThanOrEqual(100);
    }
  });
});

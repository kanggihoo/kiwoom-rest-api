import { describe, expect, it } from "vitest";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
  formatMarketSize,
} from "../../src/features/market-dashboard/lib/formatters";

describe("market dashboard formatters", () => {
  it("formats KRW prices without decimals", () => {
    expect(formatKrwPrice(103_500_000)).toBe("103,500,000");
    expect(formatKrwPrice(81.2)).toBe("81.2");
  });

  it("formats signed change rates", () => {
    expect(formatChangeRate(-0.0061)).toBe("-0.61%");
    expect(formatChangeRate(0.0315)).toBe("+3.15%");
    expect(formatChangeRate(0)).toBe("0.00%");
  });

  it("formats Korean compact trade values", () => {
    expect(formatCompactKoreanAmount(301_975_000_000)).toBe("3,020억원");
    expect(formatCompactKoreanAmount(7_924_000_000)).toBe("79억원");
  });

  it("formats market size with four decimals", () => {
    expect(formatMarketSize(0.0312)).toBe("0.0312");
    expect(formatMarketSize(12.3)).toBe("12.3000");
  });
});

import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../../src/app/api/candles/route";
import type { CandlesListResponse } from "../../src/lib/contracts/rest";

const candlesResponse: CandlesListResponse = {
  type: "candles:list",
  timestamp: "2026-06-01T03:00:00Z",
  data: {
    market: "KRW-BTC",
    candleUnit: "1m",
    candles: [
      {
        candleDateTimeUtc: "2026-06-01T00:00:00",
        candleDateTimeKst: "2026-06-01T09:00:00",
        openingPrice: 100,
        highPrice: 110,
        lowPrice: 90,
        tradePrice: 105,
        candleAccTradeVolume: 1.5,
        candleAccTradePrice: 150000,
      },
    ],
  },
};

describe("GET /api/candles", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    delete process.env.FASTAPI_BASE_URL;
  });

  it("preserves search params when proxying to FastAPI", async () => {
    process.env.FASTAPI_BASE_URL = "http://backend.test";
    const fetchMock = vi.fn(async () => Response.json(candlesResponse));
    vi.stubGlobal("fetch", fetchMock);

    const request = new Request(
      "http://localhost:3000/api/candles?market=KRW-BTC&unit=1m&count=200&to=2026-06-01T00%3A00%3A00Z",
    );
    const response = await GET(request);

    await expect(response.json()).resolves.toEqual(candlesResponse);
    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://backend.test/api/candles?market=KRW-BTC&unit=1m&count=200&to=2026-06-01T00%3A00%3A00Z",
      expect.objectContaining({
        headers: {
          Accept: "application/json",
        },
      }),
    );
  });
});

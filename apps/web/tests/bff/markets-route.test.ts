import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../../src/app/api/markets/route";
import type { MarketsListResponse } from "../../src/lib/contracts/rest";

const marketsResponse: MarketsListResponse = {
  type: "markets:list",
  timestamp: "2026-06-01T03:00:00Z",
  data: {
    markets: [
      {
        market: "KRW-BTC",
        koreanName: "비트코인",
        englishName: "Bitcoin",
        quoteCurrency: "KRW",
        baseCurrency: "BTC",
      },
    ],
  },
};

describe("GET /api/markets", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    delete process.env.FASTAPI_BASE_URL;
  });

  it("proxies the markets request through FASTAPI_BASE_URL", async () => {
    process.env.FASTAPI_BASE_URL = "http://backend.test/";
    const fetchMock = vi.fn(async () => Response.json(marketsResponse));
    vi.stubGlobal("fetch", fetchMock);

    const response = await GET();

    await expect(response.json()).resolves.toEqual(marketsResponse);
    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://backend.test/api/markets",
      expect.objectContaining({
        headers: {
          Accept: "application/json",
        },
      }),
    );
  });
});

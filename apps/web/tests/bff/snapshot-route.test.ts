import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "../../src/app/api/snapshot/route";
import type { MarketStateSnapshotResponse } from "../../src/lib/contracts/rest";

const snapshotResponse: MarketStateSnapshotResponse = {
  type: "market-state:snapshot",
  timestamp: "2026-06-01T03:00:00Z",
  data: {
    generatedAt: "2026-06-01T03:00:00Z",
    tickers: [
      {
        market: "KRW-BTC",
        openingPrice: 1,
        highPrice: 2,
        lowPrice: 0.5,
        tradePrice: 1.5,
        signedChangePrice: 0.1,
        signedChangeRate: 0.01,
        tradeVolume: 1,
        accTradeVolume24h: 2,
        accTradePrice24h: 3,
        tradeTimestampMs: 1,
        timestampMs: 2,
        streamType: "REALTIME",
      },
    ],
  },
};

describe("GET /api/snapshot", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    delete process.env.FASTAPI_BASE_URL;
  });

  it("proxies the snapshot request through FASTAPI_BASE_URL", async () => {
    process.env.FASTAPI_BASE_URL = "http://backend.test/";
    const fetchMock = vi.fn(async () => Response.json(snapshotResponse));
    vi.stubGlobal("fetch", fetchMock);

    const response = await GET();

    await expect(response.json()).resolves.toEqual(snapshotResponse);
    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://backend.test/api/snapshot",
      expect.objectContaining({
        headers: {
          Accept: "application/json",
        },
      }),
    );
  });

  it("returns the shared BFF error envelope when upstream fails", async () => {
    process.env.FASTAPI_BASE_URL = "http://backend.test";
    const fetchMock = vi.fn(
      async () =>
        new Response("Bad Gateway", {
          status: 502,
        }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await GET();
    const body = await response.json();

    expect(response.status).toBe(502);
    expect(body).toMatchObject({
      type: "error",
      data: {
        code: "UPBIT_ERROR",
        message: "Upstream responded with HTTP 502",
        details: {
          rawBody: "Bad Gateway",
        },
      },
    });
  });
});

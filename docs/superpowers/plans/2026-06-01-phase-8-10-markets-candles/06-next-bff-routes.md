# 06 Next.js BFF Routes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Browser가 같은 origin에서 `GET /api/markets`, `GET /api/candles`를 호출할 수 있도록 Next.js BFF Route Handler를 추가한다.

**Architecture:** 새 Route Handler는 기존 `fetchBackendJson()`과 `toNextResponse()`를 사용한다. `/api/candles`는 incoming request URL의 query string을 FastAPI upstream path에 그대로 붙이고, BFF cache/revalidation은 설정하지 않는다.

**Tech Stack:** Next.js Route Handlers, TypeScript, Vitest, pnpm, RTK.

---

**순서:** 06 / 07  
**이전 단계:** [05-all-krw-ticker-wiring.md](./05-all-krw-ticker-wiring.md)  
**다음 단계:** [07-verification.md](./07-verification.md)

### Task 01: BFF route 테스트 작성

**Files:**
- Create: `apps/web/tests/bff/markets-route.test.ts`
- Create: `apps/web/tests/bff/candles-route.test.ts`
- Create: `apps/web/src/app/api/markets/route.ts`
- Create: `apps/web/src/app/api/candles/route.ts`

- [ ] **Step 1: markets BFF 테스트 작성**

`apps/web/tests/bff/markets-route.test.ts`를 만든다.

```ts
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
```

- [ ] **Step 2: candles BFF 테스트 작성**

`apps/web/tests/bff/candles-route.test.ts`를 만든다.

```ts
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
```

- [ ] **Step 3: 테스트 실패 확인**

Run:

```bash
rtk test pnpm --dir apps/web test -- markets-route.test.ts candles-route.test.ts
```

Expected:

```text
Cannot find module '../../src/app/api/markets/route' 또는 '../../src/app/api/candles/route'
```

### Task 02: BFF route 구현

**Files:**
- Create: `apps/web/src/app/api/markets/route.ts`
- Create: `apps/web/src/app/api/candles/route.ts`

- [ ] **Step 1: markets route 작성**

`apps/web/src/app/api/markets/route.ts`를 만든다.

```ts
import type { MarketsListResponse } from "@/lib/contracts/rest";
import { fetchBackendJson, toNextResponse } from "@/lib/upstream/client";

export const dynamic = "force-dynamic";

export async function GET() {
  const result = await fetchBackendJson<MarketsListResponse>("/api/markets");
  return toNextResponse(result);
}
```

- [ ] **Step 2: candles route 작성**

`apps/web/src/app/api/candles/route.ts`를 만든다.

```ts
import type { CandlesListResponse } from "@/lib/contracts/rest";
import { fetchBackendJson, toNextResponse } from "@/lib/upstream/client";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const path = `/api/candles${url.search}`;
  const result = await fetchBackendJson<CandlesListResponse>(path);
  return toNextResponse(result);
}
```

- [ ] **Step 3: BFF 테스트 통과 확인**

Run:

```bash
rtk test pnpm --dir apps/web test -- markets-route.test.ts candles-route.test.ts
```

Expected:

```text
2 test files passed
```

- [ ] **Step 4: frontend type/lint 확인**

Run:

```bash
rtk test pnpm --dir apps/web lint
```

Expected:

```text
lint 통과
```

- [ ] **Step 5: 단계 커밋**

Run:

```bash
rtk proxy git add apps/web/src/app/api/markets/route.ts apps/web/src/app/api/candles/route.ts apps/web/tests/bff/markets-route.test.ts apps/web/tests/bff/candles-route.test.ts
rtk proxy git commit -m "feat: add markets and candles bff routes"
```

Expected:

```text
커밋 생성
```

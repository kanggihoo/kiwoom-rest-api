# Market Dashboard Mock Stage 2 Data Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 실제 API 연결 없이 Market dashboard 전체 화면을 렌더링할 수 있는 mock 데이터, view model 타입, 숫자 formatter, 단위 테스트를 준비한다.

**Architecture:** Mock 데이터는 `src/features/market-dashboard/mock`에 두고 UI가 직접 쓰는 view model shape로 제공한다. formatter는 `src/features/market-dashboard/lib`에 분리해 모든 panel이 같은 KRW, percent, volume 표기를 사용하게 한다.

**Tech Stack:** TypeScript strict mode, Vitest, Next.js path alias `@`, Tailwind/shadcn과 독립된 pure data utilities.

---

## 파일 구조

- Create: `apps/web/src/features/market-dashboard/types.ts`
- Create: `apps/web/src/features/market-dashboard/lib/formatters.ts`
- Create: `apps/web/src/features/market-dashboard/mock/indexes.ts`
- Create: `apps/web/src/features/market-dashboard/mock/markets.ts`
- Create: `apps/web/src/features/market-dashboard/mock/candles.ts`
- Create: `apps/web/src/features/market-dashboard/mock/orderbook.ts`
- Create: `apps/web/src/features/market-dashboard/mock/trades.ts`
- Create: `apps/web/src/features/market-dashboard/mock/dashboard.ts`
- Create: `apps/web/tests/market-dashboard/formatters.test.ts`
- Create: `apps/web/tests/market-dashboard/mock-data.test.ts`

## Task 1: dashboard view model 타입 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/types.ts`

- [ ] **Step 1: 타입 파일 생성**

Create `apps/web/src/features/market-dashboard/types.ts`:

```ts
export type MovementSide = "rise" | "fall" | "flat";

export type MarketCategory = "interest" | "KRW" | "BTC" | "USDT" | "holding";

export type CandleUnit = "1m" | "5m" | "15m" | "1h" | "1d" | "1w";

export type IndexStripItem = {
  label: string;
  value: string;
  changeRate: number;
  side: MovementSide;
  sparkline: number[];
};

export type MarketRow = {
  market: string;
  koreanName: string;
  englishName: string;
  baseCurrency: string;
  quoteCurrency: string;
  currentPrice: number;
  changeRate: number;
  changePrice: number;
  tradeVolume24h: number;
  tradeValue24h: number;
  openPrice: number;
  highPrice: number;
  lowPrice: number;
  favorite: boolean;
  selected: boolean;
  sparkline: number[];
};

export type SelectedMarketSummary = MarketRow & {
  high24h: number;
  low24h: number;
};

export type CandlePoint = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type OrderbookRow = {
  price: number;
  size: number;
  total: number;
  side: "ask" | "bid";
  depthRatio: number;
};

export type TradeRow = {
  time: string;
  price: number;
  size: number;
  side: "rise" | "fall";
};

export type MarketDashboardMockData = {
  selectedMarket: SelectedMarketSummary;
  activeCandleUnit: CandleUnit;
  activeCategory: MarketCategory;
  indexes: IndexStripItem[];
  markets: MarketRow[];
  candles: CandlePoint[];
  orderbook: OrderbookRow[];
  trades: TradeRow[];
};
```

- [ ] **Step 2: typecheck로 타입 파일 검증**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm exec tsc --noEmit
```

Expected:

```text
No TypeScript errors
```

## Task 2: formatter utility와 테스트 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/lib/formatters.ts`
- Create: `apps/web/tests/market-dashboard/formatters.test.ts`

- [ ] **Step 1: formatter 테스트 작성**

Create `apps/web/tests/market-dashboard/formatters.test.ts`:

```ts
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
```

- [ ] **Step 2: 실패 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm test tests/market-dashboard/formatters.test.ts
```

Expected:

```text
FAIL Cannot find module '../../src/features/market-dashboard/lib/formatters'
```

- [ ] **Step 3: formatter 구현**

Create `apps/web/src/features/market-dashboard/lib/formatters.ts`:

```ts
const krwFormatter = new Intl.NumberFormat("ko-KR", {
  maximumFractionDigits: 0,
});

const decimalPriceFormatter = new Intl.NumberFormat("ko-KR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 4,
});

export function formatKrwPrice(value: number): string {
  if (Math.abs(value) >= 1_000) {
    return krwFormatter.format(value);
  }

  return decimalPriceFormatter.format(value);
}

export function formatChangeRate(value: number): string {
  if (value === 0) {
    return "0.00%";
  }

  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(2)}%`;
}

export function formatCompactKoreanAmount(value: number): string {
  const eok = Math.round(value / 100_000_000);
  return `${krwFormatter.format(eok)}억원`;
}

export function formatMarketSize(value: number): string {
  return value.toFixed(4);
}
```

- [ ] **Step 4: formatter 테스트 통과 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm test tests/market-dashboard/formatters.test.ts
```

Expected:

```text
PASS tests/market-dashboard/formatters.test.ts
```

## Task 3: mock fixture 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/mock/indexes.ts`
- Create: `apps/web/src/features/market-dashboard/mock/markets.ts`
- Create: `apps/web/src/features/market-dashboard/mock/candles.ts`
- Create: `apps/web/src/features/market-dashboard/mock/orderbook.ts`
- Create: `apps/web/src/features/market-dashboard/mock/trades.ts`
- Create: `apps/web/src/features/market-dashboard/mock/dashboard.ts`

- [ ] **Step 1: index strip mock 작성**

Create `apps/web/src/features/market-dashboard/mock/indexes.ts`:

```ts
import type { IndexStripItem } from "../types";

export const mockIndexes: IndexStripItem[] = [
  {
    label: "KOSPI",
    value: "2,728.34",
    changeRate: 0.0041,
    side: "rise",
    sparkline: [20, 22, 21, 24, 25, 23, 27, 28, 26, 30, 31, 29],
  },
  {
    label: "KOSDAQ",
    value: "867.15",
    changeRate: -0.0032,
    side: "fall",
    sparkline: [30, 28, 29, 27, 26, 25, 27, 24, 23, 25, 22, 21],
  },
  {
    label: "USD/KRW",
    value: "1,370.50",
    changeRate: 0.0023,
    side: "rise",
    sparkline: [22, 21, 23, 22, 24, 25, 23, 24, 26, 25, 27, 26],
  },
  {
    label: "NASDAQ",
    value: "16,892.20",
    changeRate: 0.0075,
    side: "rise",
    sparkline: [15, 17, 16, 18, 21, 20, 23, 24, 22, 25, 27, 28],
  },
  {
    label: "S&P 500",
    value: "5,315.59",
    changeRate: 0.0058,
    side: "rise",
    sparkline: [18, 18, 19, 20, 21, 23, 22, 24, 25, 26, 28, 29],
  },
  {
    label: "BTC 도미넌스",
    value: "52.31%",
    changeRate: -0.0042,
    side: "fall",
    sparkline: [27, 26, 28, 25, 26, 24, 23, 22, 23, 21, 20, 19],
  },
];
```

- [ ] **Step 2: market mock 작성**

Create `apps/web/src/features/market-dashboard/mock/markets.ts`:

```ts
import type { MarketRow, SelectedMarketSummary } from "../types";

export const mockMarkets: MarketRow[] = [
  {
    market: "KRW-BTC",
    koreanName: "비트코인",
    englishName: "Bitcoin",
    baseCurrency: "BTC",
    quoteCurrency: "KRW",
    currentPrice: 103_500_000,
    changeRate: -0.0061,
    changePrice: -637_000,
    tradeVolume24h: 2_855.618,
    tradeValue24h: 301_974_657_977,
    openPrice: 104_140_000,
    highPrice: 104_140_000,
    lowPrice: 103_210_000,
    favorite: true,
    selected: true,
    sparkline: [52, 50, 51, 49, 48, 47, 49, 46, 45, 44, 43, 42],
  },
  {
    market: "KRW-ETH",
    koreanName: "이더리움",
    englishName: "Ethereum",
    baseCurrency: "ETH",
    quoteCurrency: "KRW",
    currentPrice: 2_903_000,
    changeRate: -0.0082,
    changePrice: -24_000,
    tradeVolume24h: 35_556.184,
    tradeValue24h: 103_239_456_000,
    openPrice: 2_928_000,
    highPrice: 2_960_000,
    lowPrice: 2_872_000,
    favorite: true,
    selected: false,
    sparkline: [42, 43, 41, 40, 39, 41, 38, 37, 39, 36, 35, 34],
  },
  {
    market: "KRW-XRP",
    koreanName: "리플",
    englishName: "XRP",
    baseCurrency: "XRP",
    quoteCurrency: "KRW",
    currentPrice: 1_877,
    changeRate: -0.0079,
    changePrice: -15,
    tradeVolume24h: 212_285_000,
    tradeValue24h: 212_285_000_000,
    openPrice: 1_892,
    highPrice: 1_914,
    lowPrice: 1_862,
    favorite: false,
    selected: false,
    sparkline: [30, 31, 30, 28, 29, 27, 28, 26, 25, 26, 24, 23],
  },
  {
    market: "KRW-SOL",
    koreanName: "솔라나",
    englishName: "Solana",
    baseCurrency: "SOL",
    quoteCurrency: "KRW",
    currentPrice: 117_800,
    changeRate: -0.0067,
    changePrice: -800,
    tradeVolume24h: 291_200,
    tradeValue24h: 34_300_000_000,
    openPrice: 118_600,
    highPrice: 120_100,
    lowPrice: 116_900,
    favorite: false,
    selected: false,
    sparkline: [38, 37, 39, 36, 35, 34, 33, 35, 32, 31, 30, 29],
  },
  {
    market: "KRW-DOGE",
    koreanName: "도지코인",
    englishName: "Dogecoin",
    baseCurrency: "DOGE",
    quoteCurrency: "KRW",
    currentPrice: 81.2,
    changeRate: 0.0315,
    changePrice: 2.5,
    tradeVolume24h: 817_044_335,
    tradeValue24h: 66_364_000_000,
    openPrice: 78.7,
    highPrice: 82.1,
    lowPrice: 77.5,
    favorite: false,
    selected: false,
    sparkline: [12, 14, 13, 16, 19, 20, 22, 21, 24, 26, 27, 29],
  },
  {
    market: "KRW-ADA",
    koreanName: "에이다",
    englishName: "Cardano",
    baseCurrency: "ADA",
    quoteCurrency: "KRW",
    currentPrice: 528,
    changeRate: -0.0055,
    changePrice: -3,
    tradeVolume24h: 42_011_412,
    tradeValue24h: 22_814_000_000,
    openPrice: 531,
    highPrice: 538,
    lowPrice: 522,
    favorite: false,
    selected: false,
    sparkline: [26, 25, 24, 25, 23, 22, 23, 21, 20, 19, 20, 18],
  },
];

export const mockSelectedMarket: SelectedMarketSummary = {
  ...mockMarkets[0],
  high24h: 104_140_000,
  low24h: 103_210_000,
};
```

- [ ] **Step 3: candle mock 작성**

Create `apps/web/src/features/market-dashboard/mock/candles.ts`:

```ts
import type { CandlePoint } from "../types";

const start = Math.floor(Date.UTC(2026, 5, 2, 0, 0, 0) / 1000);

export const mockCandles: CandlePoint[] = Array.from({ length: 96 }, (_, index) => {
  const wave = Math.sin(index / 6) * 1_800_000;
  const drift = index * 42_000;
  const base = 100_800_000 + wave + drift;
  const open = Math.round(base + Math.sin(index) * 420_000);
  const close = Math.round(base + Math.cos(index / 2) * 520_000);
  const high = Math.max(open, close) + 430_000 + (index % 5) * 52_000;
  const low = Math.min(open, close) - 390_000 - (index % 4) * 48_000;

  return {
    time: start + index * 3600,
    open,
    high,
    low,
    close,
    volume: 120 + (index % 12) * 18 + Math.abs(Math.sin(index / 4)) * 140,
  };
});
```

- [ ] **Step 4: orderbook mock 작성**

Create `apps/web/src/features/market-dashboard/mock/orderbook.ts`:

```ts
import type { OrderbookRow } from "../types";

const askPrices = [103_506_000, 103_507_000, 103_508_000, 103_509_000, 103_510_000, 103_511_000, 103_512_000, 103_513_000];
const bidPrices = [103_505_000, 103_504_000, 103_503_000, 103_502_000, 103_501_000, 103_500_000, 103_499_000, 103_498_000];

export const mockOrderbook: OrderbookRow[] = [
  ...askPrices.map((price, index) => ({
    price,
    size: Number((0.876 + index * 0.417).toFixed(3)),
    total: Number((0.876 + index * 1.216).toFixed(3)),
    side: "ask" as const,
    depthRatio: Math.min(100, 18 + index * 9),
  })),
  ...bidPrices.map((price, index) => ({
    price,
    size: Number((0.842 + index * 0.383).toFixed(3)),
    total: Number((0.842 + index * 1.087).toFixed(3)),
    side: "bid" as const,
    depthRatio: Math.min(100, 22 + index * 8),
  })),
];
```

- [ ] **Step 5: trades mock 작성**

Create `apps/web/src/features/market-dashboard/mock/trades.ts`:

```ts
import type { TradeRow } from "../types";

export const mockTrades: TradeRow[] = [
  { time: "09:41:23", price: 103_500_000, size: 0.0312, side: "rise" },
  { time: "09:41:22", price: 103_501_000, size: 0.052, side: "rise" },
  { time: "09:41:21", price: 103_500_000, size: 0.0105, side: "rise" },
  { time: "09:41:20", price: 103_499_000, size: 0.025, side: "fall" },
  { time: "09:41:19", price: 103_500_000, size: 0.002, side: "rise" },
  { time: "09:41:18", price: 103_501_000, size: 0.113, side: "rise" },
  { time: "09:41:17", price: 103_500_000, size: 0.045, side: "rise" },
  { time: "09:41:16", price: 103_501_000, size: 0.008, side: "rise" },
  { time: "09:41:15", price: 103_500_000, size: 0.1201, side: "rise" },
  { time: "09:41:14", price: 103_499_000, size: 0.03, side: "fall" },
];
```

- [ ] **Step 6: dashboard mock aggregate 작성**

Create `apps/web/src/features/market-dashboard/mock/dashboard.ts`:

```ts
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
```

## Task 4: mock 데이터 테스트 작성

**Files:**
- Create: `apps/web/tests/market-dashboard/mock-data.test.ts`

- [ ] **Step 1: mock 데이터 테스트 작성**

Create `apps/web/tests/market-dashboard/mock-data.test.ts`:

```ts
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
```

- [ ] **Step 2: mock 데이터 테스트 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm test tests/market-dashboard/mock-data.test.ts
```

Expected:

```text
PASS tests/market-dashboard/mock-data.test.ts
```

## Task 5: Stage 2 전체 검증과 커밋

**Files:**
- Verify: `apps/web/src/features/market-dashboard`
- Verify: `apps/web/tests/market-dashboard`

- [ ] **Step 1: market-dashboard 테스트 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm test tests/market-dashboard
```

Expected:

```text
PASS tests/market-dashboard/formatters.test.ts
PASS tests/market-dashboard/mock-data.test.ts
```

- [ ] **Step 2: typecheck 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm exec tsc --noEmit
```

Expected:

```text
No TypeScript errors
```

- [ ] **Step 3: Stage 2 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/features/market-dashboard apps/web/tests/market-dashboard
git commit -m "feat(web): add market dashboard mock data"
```

Expected:

```text
[branch commit] feat(web): add market dashboard mock data
```

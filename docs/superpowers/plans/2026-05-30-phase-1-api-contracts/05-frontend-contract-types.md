# 05 Frontend Contract Types Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 백엔드 Pydantic JSON 출력 구조와 같은 TypeScript 계약 타입을 프론트에 추가한다.

**Architecture:** 프론트 타입은 `apps/web/src/lib/contracts/` 아래에 events/rest/errors로 나눈다. 타입 파일은 runtime 코드가 아니라 계약 표현이므로 `export type` 중심으로 작성한다. 필드명은 모두 JSON 계약 기준 camelCase다.

**Tech Stack:** Next.js, TypeScript, pnpm, RTK.

---

**순서:** 05 / 06
**이전 단계:** [04-upbit-ticker-raw-and-mapper.md](./04-upbit-ticker-raw-and-mapper.md)
**다음 단계:** [06-docs-and-verification.md](./06-docs-and-verification.md)

### Task 05: 프론트 TypeScript 계약 타입 추가

**Files:**
- Create: `apps/web/src/lib/contracts/events.ts`
- Create: `apps/web/src/lib/contracts/rest.ts`
- Create: `apps/web/src/lib/contracts/errors.ts`

- [ ] **Step 1: events 타입 파일 작성**

`apps/web/src/lib/contracts/events.ts`를 만든다.

```ts
export type StreamType = "SNAPSHOT" | "REALTIME";

export type AskBid = "ASK" | "BID";

export type CandleUnit = "1m" | "5m" | "15m" | "30m" | "1h" | "1d" | "1w";

export type RealtimeCandleUnit = "1m" | "5m" | "15m" | "30m" | "1h";

export type AlertKind = "dailyRise" | "dailyDrop" | "shortTermRise" | "shortTermDrop";

export type Severity = "info" | "warning";

export type TickerData = {
  /** Market 코드. Upbit ticker.code 기준. */
  market: string;
  /** 시가. Upbit ticker.opening_price 기준. */
  openingPrice: number;
  /** 고가. Upbit ticker.high_price 기준. */
  highPrice: number;
  /** 저가. Upbit ticker.low_price 기준. */
  lowPrice: number;
  /** 현재가. Upbit ticker.trade_price 기준. */
  tradePrice: number;
  /** 전일 대비 가격 변동 값. Upbit ticker.signed_change_price 기준. */
  signedChangePrice: number;
  /** 전일 대비 등락률. Upbit ticker.signed_change_rate 기준. */
  signedChangeRate: number;
  /** 최근 거래량. Upbit ticker.trade_volume 기준. */
  tradeVolume: number;
  /** 최근 24시간 누적 거래량. Upbit ticker.acc_trade_volume_24h 기준. */
  accTradeVolume24h: number;
  /** 최근 24시간 누적 거래대금. Upbit ticker.acc_trade_price_24h 기준. */
  accTradePrice24h: number;
  /** 체결 타임스탬프(ms). Upbit ticker.trade_timestamp 기준. */
  tradeTimestampMs: number;
  /** Upbit 이벤트 타임스탬프(ms). Upbit ticker.timestamp 기준. */
  timestampMs: number;
  /** Upbit stream_type. */
  streamType: StreamType;
};

export type TradeData = {
  market: string;
  tradePrice: number;
  tradeVolume: number;
  askBid: AskBid;
  tradeTimestampMs: number;
  sequentialId: number;
  timestampMs: number;
  streamType: StreamType;
};

export type OrderbookUnit = {
  askPrice: number;
  bidPrice: number;
  askSize: number;
  bidSize: number;
};

export type OrderbookData = {
  market: string;
  totalAskSize: number;
  totalBidSize: number;
  level: number;
  units: OrderbookUnit[];
  timestampMs: number;
  streamType: StreamType;
};

export type Candle = {
  candleDateTimeUtc: string;
  candleDateTimeKst: string;
  openingPrice: number;
  highPrice: number;
  lowPrice: number;
  tradePrice: number;
  candleAccTradeVolume: number;
  candleAccTradePrice: number;
};

export type CandleUpdateData = {
  market: string;
  candleUnit: RealtimeCandleUnit;
  candle: Candle;
  timestampMs: number;
  streamType: StreamType;
};

export type AlertData = {
  id: string;
  market: string;
  alertKind: AlertKind;
  title: string;
  message: string;
  severity: Severity;
  basisRate: number;
  basisWindow: "24h" | "1m";
  createdAt: string;
};

export type TickerUpdateEvent = {
  type: "ticker:update";
  timestamp: string;
  data: TickerData;
};

export type TradeUpdateEvent = {
  type: "trade:update";
  timestamp: string;
  data: TradeData;
};

export type OrderbookUpdateEvent = {
  type: "orderbook:update";
  timestamp: string;
  data: OrderbookData;
};

export type CandleUpdateEvent = {
  type: "candle:update";
  timestamp: string;
  data: CandleUpdateData;
};

export type AlertNewEvent = {
  type: "alert:new";
  timestamp: string;
  data: AlertData;
};

export type BackendEvent =
  | TickerUpdateEvent
  | TradeUpdateEvent
  | OrderbookUpdateEvent
  | CandleUpdateEvent
  | AlertNewEvent;
```

- [ ] **Step 2: REST 타입 파일 작성**

`apps/web/src/lib/contracts/rest.ts`를 만든다.

```ts
import type { Candle, CandleUnit, TickerData } from "./events";

export type RestEnvelope<TType extends string, TData> = {
  type: TType;
  timestamp: string;
  data: TData;
};

export type MarketSummary = {
  market: string;
  koreanName: string;
  englishName: string;
  quoteCurrency: string;
  baseCurrency: string;
};

export type MarketsListResponse = RestEnvelope<
  "markets:list",
  {
    markets: MarketSummary[];
  }
>;

export type MarketStateSnapshotResponse = RestEnvelope<
  "market-state:snapshot",
  {
    generatedAt: string;
    tickers: TickerData[];
  }
>;

export type CandlesListResponse = RestEnvelope<
  "candles:list",
  {
    market: string;
    candleUnit: CandleUnit;
    candles: Candle[];
  }
>;

export type RestSuccessResponse =
  | MarketsListResponse
  | MarketStateSnapshotResponse
  | CandlesListResponse;
```

- [ ] **Step 3: 에러 타입 파일 작성**

`apps/web/src/lib/contracts/errors.ts`를 만든다.

```ts
export type RestErrorCode =
  | "BAD_REQUEST"
  | "NOT_FOUND"
  | "TEMPORARILY_BLOCKED"
  | "VALIDATION_ERROR"
  | "RATE_LIMITED"
  | "UPBIT_BAD_REQUEST"
  | "UPBIT_ERROR"
  | "UPBIT_TIMEOUT"
  | "INTERNAL_ERROR";

export type WebSocketErrorCode =
  | "INVALID_MESSAGE"
  | "UNSUPPORTED_MESSAGE_TYPE"
  | "INVALID_MARKET"
  | "BAD_REQUEST"
  | "VALIDATION_ERROR"
  | "RATE_LIMITED"
  | "TEMPORARILY_BLOCKED"
  | "UPBIT_WS_ERROR"
  | "INTERNAL_ERROR";

export type ErrorData = {
  code: RestErrorCode | WebSocketErrorCode;
  message: string;
  details?: Record<string, unknown> | null;
};

export type ErrorEnvelope = {
  type: "error";
  timestamp: string;
  data: ErrorData;
};
```

- [ ] **Step 4: 프론트 lint/build 검증**

Run:

```bash
rtk test make lint-web
rtk test make build-web
```

Expected:

```text
lint 성공
build 성공
```

- [ ] **Step 5: 단계 커밋**

Run:

```bash
rtk git add apps/web/src/lib/contracts/events.ts apps/web/src/lib/contracts/rest.ts apps/web/src/lib/contracts/errors.ts
rtk git commit -m "feat: add frontend api contract types"
```

Expected:

```text
커밋 생성
```

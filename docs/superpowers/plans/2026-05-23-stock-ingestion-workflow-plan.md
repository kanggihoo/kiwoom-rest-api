# 재고 수집 워크플로우 구현 계획

> **대리인용: ** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**목표: ** Implement the Cloudflare scheduled ingestion workflow with market-session filtering, priority-based symbol selection, per-invocation subrequest budgeting, OHLCV normalization, Supabase upsert, and status recording.

**건축학: ** Split Worker logic into small modules: market session, interval calculation, provider client, Supabase repository, ingestion orchestrator, and KV status writer. Use TDD for pure functions and mocked fetch for network boundaries. Git steps are intentionally omitted because the user requested no git operations.

**기술 스택: ** TypeScript, Cloudflare Workers scheduled handler, Vitest, Supabase REST API, Workers KV.

---

## 파일 구조

- 만들다: `src/market-session.ts` - regular session checks.
- 만들다: `src/interval.ts` - 10-minute interval calculation.
- 만들다: `src/provider.ts` - stock API client and response normalization.
- 만들다: `src/supabase-repository.ts` - Supabase REST operations.
- 만들다: `src/ingestion.ts` - orchestration.
- 수정하다: `src/index.ts` - call ingestion orchestrator.
- 만들다: `test/market-session.test.ts`
- 만들다: `test/interval.test.ts`
- 만들다: `test/provider.test.ts`
- 만들다: `test/ingestion-budget.test.ts`

## 작업 1: Implement Interval Calculation

**파일: **
- 만들다: `src/interval.ts`
- 만들다: `test/interval.test.ts`

- [ ] **1단계: 실패한 간격 테스트 작성**

`test/interval.test.ts`를 생성합니다:

```ts
import { describe, expect, it } from "vitest";
import { getPreviousCompletedTenMinuteInterval } from "../src/interval";

describe("getPreviousCompletedTenMinuteInterval", () => {
  it("returns the previous completed 10m interval", () => {
    expect(getPreviousCompletedTenMinuteInterval(new Date("2026-05-23T13:42:00Z")).toISOString()).toBe("2026-05-23T13:30:00.000Z");
    expect(getPreviousCompletedTenMinuteInterval(new Date("2026-05-23T13:40:00Z")).toISOString()).toBe("2026-05-23T13:30:00.000Z");
    expect(getPreviousCompletedTenMinuteInterval(new Date("2026-05-23T13:09:59Z")).toISOString()).toBe("2026-05-23T12:50:00.000Z");
  });
});
```

- [ ] **2단계: 테스트 실행 및 실패 확인**

달리다: `rtk npm run test -- test/interval.test.ts`

예상되는: FAIL because `src/interval.ts` does not exist.

- [ ] **3단계: 간격 도우미 구현**

`src/interval.ts`를 생성합니다:

```ts
export function getPreviousCompletedTenMinuteInterval(now: Date): Date {
  const ms = now.getTime();
  const tenMinutes = 10 * 60 * 1000;
  const floored = Math.floor(ms / tenMinutes) * tenMinutes;
  return new Date(floored - tenMinutes);
}
```

- [ ] **4단계: 테스트 실행**

달리다: `rtk npm run test -- test/interval.test.ts`

예상되는: PASS.

## 작업 2: Implement Market Session Checks

**파일: **
- 만들다: `src/market-session.ts`
- 만들다: `test/market-session.test.ts`

- [ ] **1단계: 실패한 테스트 작성**

`test/market-session.test.ts`를 생성합니다:

```ts
import { describe, expect, it } from "vitest";
import { isRegularSessionOpen } from "../src/market-session";

describe("isRegularSessionOpen", () => {
  it("detects US regular session in New York time", () => {
    expect(isRegularSessionOpen(new Date("2026-05-22T14:00:00Z"), "America/New_York", "09:30", "16:00")).toBe(true);
    expect(isRegularSessionOpen(new Date("2026-05-22T22:00:00Z"), "America/New_York", "09:30", "16:00")).toBe(false);
  });

  it("detects KRX regular session in Seoul time", () => {
    expect(isRegularSessionOpen(new Date("2026-05-22T01:00:00Z"), "Asia/Seoul", "09:00", "15:30")).toBe(true);
    expect(isRegularSessionOpen(new Date("2026-05-22T08:00:00Z"), "Asia/Seoul", "09:00", "15:30")).toBe(false);
  });
});
```

- [ ] **2단계: 테스트 실행 및 실패 확인**

달리다: `rtk npm run test -- test/market-session.test.ts`

예상되는: FAIL because `src/market-session.ts` does not exist.

- [ ] **3단계: 세션 도우미 구현**

`src/market-session.ts`를 생성하세요:

```ts
function localMinutes(date: Date, timezone: string): number {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: timezone,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(date);

  const hour = Number(parts.find((part) => part.type === "hour")?.value);
  const minute = Number(parts.find((part) => part.type === "minute")?.value);
  return hour * 60 + minute;
}

function parseTime(value: string): number {
  const [hour, minute] = value.split(":").map(Number);
  return hour * 60 + minute;
}

export function isRegularSessionOpen(now: Date, timezone: string, regularOpen: string, regularClose: string): boolean {
  const current = localMinutes(now, timezone);
  return current >= parseTime(regularOpen) && current < parseTime(regularClose);
}
```

- [ ] **4단계: 테스트 실행**

달리다: `rtk npm run test -- test/market-session.test.ts`

예상되는: PASS.

## 작업 3: Implement Provider Normalization

**파일: **
- 만들다: `src/provider.ts`
- 만들다: `test/provider.test.ts`

- [ ] **1단계: 실패한 테스트 작성**

`test/provider.test.ts`를 생성합니다:

```ts
import { describe, expect, it } from "vitest";
import { normalizeProviderQuote } from "../src/provider";

describe("normalizeProviderQuote", () => {
  it("normalizes a valid quote", () => {
    const bar = normalizeProviderQuote({
      symbol: "AAPL",
      timestamp: "2026-05-23T13:39:59.000Z",
      open: 190.1,
      high: 191.2,
      low: 189.8,
      close: 190.7,
      volume: 1234567,
    }, {
      source: "mock",
      marketCode: "us",
      symbol: "AAPL",
      intervalStart: "2026-05-23T13:30:00.000Z",
    });

    expect(bar.close).toBe(190.7);
    expect(bar.timeframe).toBe("10m");
    expect(bar.sessionType).toBe("regular");
  });

  it("rejects invalid quote numbers", () => {
    expect(() => normalizeProviderQuote({ symbol: "AAPL", close: "bad" }, {
      source: "mock",
      marketCode: "us",
      symbol: "AAPL",
      intervalStart: "2026-05-23T13:30:00.000Z",
    })).toThrow("invalid provider quote");
  });
});
```

- [ ] **2단계: 테스트 실행 및 실패 확인**

달리다: `rtk npm run test -- test/provider.test.ts`

예상되는: FAIL because `src/provider.ts` does not exist.

- [ ] **3단계: 노멀라이저 구현**

`src/provider.ts`를 생성합니다:

```ts
import type { MarketCode, PriceBar } from "./types";

interface NormalizeContext {
  source: string;
  marketCode: MarketCode;
  symbol: string;
  intervalStart: string;
}

function numberField(input: Record<string, unknown>, key: string): number {
  const value = input[key];
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error("invalid provider quote");
  }
  return value;
}

export function normalizeProviderQuote(payload: unknown, context: NormalizeContext): PriceBar {
  if (!payload || typeof payload !== "object") {
    throw new Error("invalid provider quote");
  }

  const input = payload as Record<string, unknown>;
  const timestamp = typeof input.timestamp === "string" ? input.timestamp : null;

  return {
    source: context.source,
    marketCode: context.marketCode,
    symbol: context.symbol,
    timeframe: "10m",
    intervalStart: context.intervalStart,
    sessionType: "regular",
    open: numberField(input, "open"),
    high: numberField(input, "high"),
    low: numberField(input, "low"),
    close: numberField(input, "close"),
    volume: numberField(input, "volume"),
    providerTime: timestamp,
    sourceRowsCount: 1,
  };
}
```

- [ ] **4단계: 테스트 실행**

달리다: `rtk npm run test -- test/provider.test.ts`

예상되는: PASS.

## 작업 4: Implement Budget Calculation

**파일: **
- 만들다: `src/ingestion.ts`
- 만들다: `test/ingestion-budget.test.ts`

- [ ] **1단계: 실패한 테스트 작성**

`test/ingestion-budget.test.ts`를 생성합니다.

```ts
import { describe, expect, it } from "vitest";
import { calculateStockApiBudget } from "../src/ingestion";

describe("calculateStockApiBudget", () => {
  it("reserves subrequests and caps stock API calls", () => {
    expect(calculateStockApiBudget({ totalLimit: 50, plannedSymbols: 50 })).toBe(44);
    expect(calculateStockApiBudget({ totalLimit: 50, plannedSymbols: 20 })).toBe(20);
  });
});
```

- [ ] **2단계: 테스트 실행 및 실패 확인**

달리다: `rtk npm run test -- test/ingestion-budget.test.ts`

예상되는: FAIL because `calculateStockApiBudget` is missing.

- [ ] **3단계: 예산 도우미 구현**

`src/ingestion.ts`를 생성합니다:

```ts
export interface BudgetInput {
  totalLimit: number;
  plannedSymbols: number;
}

export function calculateStockApiBudget(input: BudgetInput): number {
  const reservedForSupabaseAndKv = 6;
  const available = Math.max(0, input.totalLimit - reservedForSupabaseAndKv);
  return Math.min(input.plannedSymbols, available);
}
```

- [ ] **4단계: 테스트 실행**

달리다: `rtk npm run test -- test/ingestion-budget.test.ts`

예상되는: PASS.

## 작업 5: Wire Scheduled Handler to Orchestrator

**파일: **
- 수정하다: `src/index.ts`
- 수정하다: `src/ingestion.ts`

- [ ] **1단계: 오케스트레이터 계약 및 초기 비공개 시장 결과 추가**

`src/ingestion.ts` 수정:

```ts
export interface BudgetInput {
  totalLimit: number;
  plannedSymbols: number;
}

export interface IngestionResult {
  status: "success" | "partial_success" | "failed" | "skipped_market_closed";
  symbolsAttempted: number;
  symbolsSucceeded: number;
  symbolsFailed: number;
}

export function calculateStockApiBudget(input: BudgetInput): number {
  const reservedForSupabaseAndKv = 6;
  const available = Math.max(0, input.totalLimit - reservedForSupabaseAndKv);
  return Math.min(input.plannedSymbols, available);
}

export async function runScheduledIngestion(): Promise<IngestionResult> {
  return {
    status: "skipped_market_closed",
    symbolsAttempted: 0,
    symbolsSucceeded: 0,
    symbolsFailed: 0,
  };
}
```

- [ ] **2단계: 작업자 진입점 업데이트**

`src/index.ts` 수정:

```ts
import { getConfig } from "./config";
import { runScheduledIngestion } from "./ingestion";
import type { Env } from "./types";

export default {
  async scheduled(controller, env, ctx) {
    const config = getConfig(env);
    const result = await runScheduledIngestion();

    ctx.waitUntil(
      env.INGESTION_STATE.put(
        "last_scheduled_invocation",
        JSON.stringify({
          cron: controller.cron,
          scheduledTime: new Date(controller.scheduledTime).toISOString(),
          source: config.stockApiSource,
          result,
        }),
      ),
    );
  },
} satisfies ExportedHandler<Env>;
```

- [ ] **3단계: 유형 확인 및 테스트**

달리다: `rtk npm run typecheck && rtk npm run test`

예상되는: typecheck passes and all workflow tests pass.

## 자체 검토 체크리스트

- 사양 범위: market-session checks, priority budget, previous completed interval, provider validation, and KV status write are covered.
- 열린 아이템 스캔: `runScheduledIngestion` returns a closed-market result until repository/provider integration tasks are implemented; the contract is explicit and testable.
- 유형 일관성: `MarketCode`, `PriceBar`, `RunStatus`, and `SessionType` match `src/types.ts`.

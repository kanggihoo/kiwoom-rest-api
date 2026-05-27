# 주식 수집 개요 구성

> **에이전트 수출용: ** 필수 하위 스킬: 이 계획을 작업 단위로 구현할 때 `superpowers:subagent-driven-development`(권장) 또는 `superpowers:executing-plans`를 사용한다. 단계 추적은 체크박스(`- [ ]`) 문법을 사용한다.

**목표: ** Cloudflare Free + Supabase Free 기반 주식 수집 시스템의 프로젝트 골격과 공용 계약을 만든다.

**아키텍처: ** 설정, 시장 세션, 제공자 계약, Supabase 접근, 로깅을 분리한 TypeScript Cloudflare Worker 프로젝트로 구성한다. 첫 커밋부터 local-first와 quota 인지를 반영한다. 사용자가 git 작업을 원하지 않아 git 단계는 의도적으로 제외했다.

**기술 그리드: ** TypeScript, Cloudflare Workers, Wrangler, Vitest, Supabase REST/Postgres migrations, Workers KV.

---

## 파일구조

- 생성: `package.json` - npm 스크립트와 개발 의존성.
- 생성: `tsconfig.json` - strict TypeScript 설정.
- 생성: `vitest.config.ts` - 테스트 설정.
- 생성: `wrangler.jsonc` - Worker vars와 Cron 설정. KV binding은 namespace 생성 후 추가.
- 생성: `src/types.ts` - 공용 도메인 타입과 status enum.
- 생성: `src/config.ts` - 환경 파싱과 상수.
- 생성: `src/index.ts` - scheduled handler 연결이 포함된 Worker 진입점.
- 생성: `test/types.test.ts` - 계약 스모크 테스트.

## 작업 1: TypeScript Worker 프로젝트 부트스트랩

**파일: **
- 생성: `package.json`
- 생성: `tsconfig.json`
- 생성: `vitest.config.ts`

- [ ] **단계 1: npm 프로젝트에서 데이터 생성**

`package.json`을 포함합니다.

```json
{
  "name": "stock-ingestion-worker",
  "private": true,
  "type": "module",
  "scripts": {
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "dev": "wrangler dev --test-scheduled",
    "deploy": "wrangler deploy"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20260522.0",
    "typescript": "^5.9.0",
    "vitest": "^3.0.0",
    "wrangler": "^4.0.0"
  }
}
```

- [ ] **단계 2: 깐 TypeScript 설정 생성**

`tsconfig.json`을 입력합니다.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "types": ["@cloudflare/workers-types", "vitest/globals"],
    "skipLibCheck": true
  },
  "include": ["src", "test"]
}
```

- [ ] **단계 3: Vitest 설정 생성**

`vitest.config.ts`를 생성합니다:

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
  },
});
```

- [ ] **단계 4: 의존성 설치**

실행: `rtk npm install`

예상 결과: `node_modules`가 생성되고 lock 파일이 만들어진다.

## 작업 2: Worker 설정 정의

**파일: **
- 생성: `wrangler.jsonc`

- [ ] **단계 1: 출력 파일 생성**

'wrangler.jsonc'를 등록합니다.

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "stock-ingestion-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-05-23",
  "observability": {
    "enabled": true,
    "head_sampling_rate": 1
  },
  "triggers": {
    "crons": ["*/10 * * * *"]
  },
  "vars": {
    "SUPABASE_URL": "http://127.0.0.1:54321",
    "STOCK_API_BASE_URL": "http://127.0.0.1:8788",
    "STOCK_API_SOURCE": "mock"
  },
  "secrets": {
    "required": ["SUPABASE_SECRET_KEY", "STOCK_API_TOKEN"]
  }
}
```

- [ ] **단계 2: 운영 배포 전 KV 마커스페이스 생성**

실행: `rtk proxy npx wrangler kv namespace create INGESTION_STATE`

예상 결과: Wrangler가 운영 namespace binding 블록을 출력한다. 해당 블록을 `wrangler.jsonc`에 추가한다.

실행: `rtk proxy npx wrangler kv namespace create INGESTION_STATE --preview`

예상 결과: Wrangler가 preview namespace binding 블록을 출력한다. 동일한 `kv_namespaces` 항목에 `preview_id`를 추가한다.

- [ ] ** 단계 3: 의존성 설치 후 설정 인증**

실행: `rtk proxy npx wrangler types --experimental-include-runtime`

예상 결과: 실제 KV namespace ID 반영 후 Worker 타입이 생성된다.

## 작업 3: 공용 도메인 계약 정의

**파일: **
- 생성: `src/types.ts`
- 생성: `test/types.test.ts`

- [ ] **단계 1: 공용 타입 추가**

`src/types.ts`를 생성합니다:

```ts
export type MarketCode = "krx" | "us";
export type SessionType = "regular" | "pre_market" | "after_hours";
export type Timeframe = "10m" | "30m" | "1h" | "1d";
export type RunStatus = "success" | "partial_success" | "failed" | "skipped_market_closed";
export type SymbolResultStatus = "success" | "failed" | "skipped_budget";

export interface Env {
  SUPABASE_URL: string;
  SUPABASE_SECRET_KEY: string;
  STOCK_API_BASE_URL: string;
  STOCK_API_TOKEN: string;
  STOCK_API_SOURCE: string;
  INGESTION_STATE: KVNamespace;
}

export interface WatchlistSymbol {
  symbol: string;
  marketCode: MarketCode;
  sourceSymbol: string;
  priority: number;
}

export interface PriceBar {
  source: string;
  marketCode: MarketCode;
  symbol: string;
  timeframe: Timeframe;
  intervalStart: string;
  sessionType: SessionType;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  providerTime: string | null;
  sourceRowsCount: number;
}
```

- [ ] **단계 2: 계약 스모크 테스트 추가**

`test/types.test.ts`를 생성합니다:

```ts
import { describe, expect, it } from "vitest";
import type { PriceBar } from "../src/types";

describe("PriceBar contract", () => {
  it("represents a 10m regular-session OHLCV bar", () => {
    const bar: PriceBar = {
      source: "mock",
      marketCode: "us",
      symbol: "AAPL",
      timeframe: "10m",
      intervalStart: "2026-05-23T13:30:00.000Z",
      sessionType: "regular",
      open: 100,
      high: 101,
      low: 99,
      close: 100.5,
      volume: 1000,
      providerTime: "2026-05-23T13:39:59.000Z",
      sourceRowsCount: 1,
    };

    expect(bar.timeframe).toBe("10m");
    expect(bar.sourceRowsCount).toBe(1);
  });
});
```

- [ ] **단계 3: 테스트 실행**

실행: `rtk npm run test`

예상 결과: 테스트 1개 PASS.

## 작업 4: 최소 Worker 진입점 추가

**파일: **
- 생성: `src/config.ts`
- 생성: `src/index.ts`

- [ ] **단계 1: 설정 파서 추가**

`src/config.ts`를 생성합니다:

```ts
import type { Env } from "./types";

export interface AppConfig {
  supabaseUrl: string;
  stockApiBaseUrl: string;
  stockApiSource: string;
}

export function getConfig(env: Env): AppConfig {
  return {
    supabaseUrl: env.SUPABASE_URL.replace(/\/$/, ""),
    stockApiBaseUrl: env.STOCK_API_BASE_URL.replace(/\/$/, ""),
    stockApiSource: env.STOCK_API_SOURCE,
  };
}
```

- [ ] **단계 2: 향후점 추가**

`src/index.ts`를 생성합니다:

```ts
import { getConfig } from "./config";
import type { Env } from "./types";

export default {
  async scheduled(controller, env, ctx) {
    const config = getConfig(env);
    ctx.waitUntil(
      env.INGESTION_STATE.put(
        "last_scheduled_invocation",
        JSON.stringify({
          cron: controller.cron,
          scheduledTime: new Date(controller.scheduledTime).toISOString(),
          source: config.stockApiSource,
        }),
      ),
    );
  },
} satisfies ExportedHandler<Env>;
```

- [ ] **단계 3: 타입 검사**

실행: `rtk npm run typecheck`

예상 결과: PASS.

##인증활성화리스트

- 장비정보: 개요 제약, 무과금 정책, Worker/Supabase/KV 역할, 10분 Cron 반영 완료.
- 미해결 ​​항목 확인: 남은 설계 이슈 없음. KV namespace ID는 구현 중 Wrangler로 생성해 설정에 반영.
- 일관성이 있다: `MarketCode`, `Timeframe`, `SessionType`, `PriceBar`, `Env`는 이후 계획에서 재사용.

# Market Dashboard Mock Stage 4 Chart Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Selected Market header, candle unit control, Lightweight Charts 기반 mock candle/volume chart를 main column 상단에 배치한다.

**Architecture:** `LightweightCandleChart`는 chart library lifecycle을 내부에 가두는 client component다. `SelectedMarketPanel`은 shadcn panel/header/control만 알고 chart adapter의 내부 API를 알지 않는다.

**Tech Stack:** React Client Component, lightweight-charts, shadcn/ui Card/Button/Badge/ToggleGroup/Tooltip/Separator, lucide-react.

---

## 파일 구조

- Modify: `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx`
- Create: `apps/web/src/features/market-dashboard/components/selected-market-panel.tsx`
- Create: `apps/web/src/features/market-dashboard/components/selected-market-header.tsx`
- Create: `apps/web/src/features/market-dashboard/components/candle-unit-toggle.tsx`
- Create: `apps/web/src/features/market-dashboard/components/lightweight-candle-chart.tsx`

## Task 1: Candle unit toggle 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/candle-unit-toggle.tsx`

- [ ] **Step 1: Candle unit toggle component 작성**

Create `apps/web/src/features/market-dashboard/components/candle-unit-toggle.tsx`:

```tsx
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group";

import type { CandleUnit } from "../types";

const candleUnits: Array<{ value: CandleUnit; label: string }> = [
  { value: "1m", label: "1분" },
  { value: "5m", label: "5분" },
  { value: "15m", label: "15분" },
  { value: "1h", label: "1시간" },
  { value: "1d", label: "1일" },
  { value: "1w", label: "1주" },
];

type CandleUnitToggleProps = {
  value: CandleUnit;
};

export function CandleUnitToggle({ value }: CandleUnitToggleProps) {
  return (
    <ToggleGroup type="single" value={value} aria-label="Candle unit" className="gap-1">
      {candleUnits.map((unit) => (
        <ToggleGroupItem key={unit.value} value={unit.value} className="h-8 px-3 text-[13px]">
          {unit.label}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
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

## Task 2: Selected Market header 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/selected-market-header.tsx`

- [ ] **Step 1: Selected Market header component 작성**

Create `apps/web/src/features/market-dashboard/components/selected-market-header.tsx`:

```tsx
import { ChevronDown, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
  formatMarketSize,
} from "../lib/formatters";
import type { SelectedMarketSummary } from "../types";

type SelectedMarketHeaderProps = {
  market: SelectedMarketSummary;
};

export function SelectedMarketHeader({ market }: SelectedMarketHeaderProps) {
  const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

  return (
    <header className="grid gap-5 border-b border-border p-5 lg:grid-cols-[minmax(280px,1fr)_auto]">
      <div className="flex min-w-0 flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="flex size-8 items-center justify-center rounded-full bg-[#f7931a] text-[15px] font-bold text-white">
            ₿
          </div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] font-bold leading-none">
              {market.baseCurrency}
              <span className="text-[15px] font-semibold text-muted-foreground">/{market.quoteCurrency}</span>
            </h1>
            <Button variant="ghost" size="icon" aria-label="Selected Market menu">
              <ChevronDown data-icon="icon" />
            </Button>
          </div>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="icon" aria-label="관심 Market">
                <Star data-icon="icon" className={market.favorite ? "fill-primary text-primary" : undefined} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>관심 Market</TooltipContent>
          </Tooltip>
        </div>

        <div className="flex flex-wrap items-end gap-x-4 gap-y-2">
          <strong className="font-sans text-[40px] font-bold leading-[44px] tabular-nums text-primary">
            {formatKrwPrice(market.currentPrice)}
            <span className="ml-1 text-[15px] font-bold">KRW</span>
          </strong>
          <div className="flex items-center gap-2 pb-1">
            <Badge variant="secondary" data-side={side} className="data-[side=fall]:text-fall data-[side=rise]:text-rise">
              {formatChangeRate(market.changeRate)}
            </Badge>
            <span className="text-[15px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise" data-side={side}>
              {market.changePrice > 0 ? "+" : ""}
              {formatKrwPrice(market.changePrice)}
            </span>
          </div>
        </div>
      </div>

      <dl className="grid min-w-[520px] grid-cols-2 gap-x-10 gap-y-3 text-[13px]">
        <div className="grid grid-cols-[96px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">고가</dt>
          <dd className="font-semibold tabular-nums text-rise">{formatKrwPrice(market.high24h)}</dd>
        </div>
        <div className="grid grid-cols-[120px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">거래량(24H)</dt>
          <dd className="font-semibold tabular-nums">
            {formatMarketSize(market.tradeVolume24h)} {market.baseCurrency}
          </dd>
        </div>
        <div className="grid grid-cols-[96px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">저가</dt>
          <dd className="font-semibold tabular-nums text-fall">{formatKrwPrice(market.low24h)}</dd>
        </div>
        <div className="grid grid-cols-[120px_1fr] items-center gap-3">
          <dt className="text-muted-foreground">거래대금(24H)</dt>
          <dd className="font-semibold tabular-nums">
            {formatCompactKoreanAmount(market.tradeValue24h)}
          </dd>
        </div>
      </dl>

      <Separator className="lg:hidden" />
    </header>
  );
}
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

## Task 3: Lightweight chart adapter 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/lightweight-candle-chart.tsx`

- [ ] **Step 1: Lightweight chart client component 작성**

Create `apps/web/src/features/market-dashboard/components/lightweight-candle-chart.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  createChart,
  HistogramSeries,
  type IChartApi,
  type ISeriesApi,
  type Time,
} from "lightweight-charts";

import type { CandlePoint } from "../types";

type LightweightCandleChartProps = {
  candles: CandlePoint[];
};

function readCssVariable(name: string, fallback: string) {
  if (typeof window === "undefined") {
    return fallback;
  }

  const value = window.getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

export function LightweightCandleChart({ candles }: LightweightCandleChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const foreground = readCssVariable("--foreground", "#151b2d");
    const muted = readCssVariable("--muted-foreground", "#7b8494");
    const border = readCssVariable("--border", "#e3e8f0");
    const background = readCssVariable("--card", "#ffffff");
    const rise = readCssVariable("--chart-3", "#f04452");
    const fall = readCssVariable("--chart-2", "#1d6fff");

    const chart = createChart(container, {
      autoSize: true,
      height: 430,
      layout: {
        background: { color: background },
        textColor: muted,
        fontFamily: "var(--font-pretendard), Pretendard, system-ui, sans-serif",
        fontSize: 12,
      },
      grid: {
        vertLines: { color: border },
        horzLines: { color: border },
      },
      rightPriceScale: {
        borderColor: border,
      },
      timeScale: {
        borderColor: border,
        timeVisible: true,
      },
      crosshair: {
        horzLine: { color: foreground, labelBackgroundColor: foreground },
        vertLine: { color: foreground, labelBackgroundColor: foreground },
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: rise,
      downColor: fall,
      borderUpColor: rise,
      borderDownColor: fall,
      wickUpColor: rise,
      wickDownColor: fall,
      priceFormat: {
        type: "price",
        precision: 0,
        minMove: 1,
      },
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: "volume",
      },
      priceScaleId: "",
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    candleSeries.setData(
      candles.map((candle) => ({
        time: candle.time as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      })),
    );

    volumeSeries.setData(
      candles.map((candle) => ({
        time: candle.time as Time,
        value: candle.volume,
        color: candle.close >= candle.open ? `${rise}55` : `${fall}55`,
      })),
    );

    chart.timeScale().fitContent();

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    return () => {
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, [candles]);

  return (
    <div className="relative min-h-[430px] border-t border-border">
      <div ref={containerRef} className="h-[430px] w-full" aria-label="Mock candle chart" />
    </div>
  );
}
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

## Task 4: Selected Market panel 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/selected-market-panel.tsx`

- [ ] **Step 1: Selected Market panel component 작성**

Create `apps/web/src/features/market-dashboard/components/selected-market-panel.tsx`:

```tsx
import { Activity, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import type { CandlePoint, CandleUnit, SelectedMarketSummary } from "../types";
import { CandleUnitToggle } from "./candle-unit-toggle";
import { LightweightCandleChart } from "./lightweight-candle-chart";
import { SelectedMarketHeader } from "./selected-market-header";

type SelectedMarketPanelProps = {
  market: SelectedMarketSummary;
  candles: CandlePoint[];
  activeCandleUnit: CandleUnit;
};

export function SelectedMarketPanel({
  market,
  candles,
  activeCandleUnit,
}: SelectedMarketPanelProps) {
  return (
    <Card className="overflow-hidden rounded-md border-border bg-card p-0 shadow-none">
      <SelectedMarketHeader market={market} />
      <div className="flex min-h-[48px] items-center justify-between gap-4 px-5">
        <CandleUnitToggle value={activeCandleUnit} />
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Activity data-icon="inline-start" />
            기본차트
          </Button>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="차트 지표">
                <SlidersHorizontal data-icon="icon" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>차트 지표</TooltipContent>
          </Tooltip>
        </div>
      </div>
      <LightweightCandleChart candles={candles} />
    </Card>
  );
}
```

- [ ] **Step 2: shell에 Selected Market panel 연결**

Replace `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx` with:

```tsx
import type { MarketDashboardMockData } from "../types";
import { SelectedMarketPanel } from "./selected-market-panel";

type MarketDashboardShellProps = {
  data: MarketDashboardMockData;
};

export function MarketDashboardShell({ data }: MarketDashboardShellProps) {
  return (
    <section className="grid gap-3 px-5 py-3 xl:grid-cols-[minmax(0,74%)_minmax(360px,26%)]">
      <div className="flex min-w-0 flex-col gap-3">
        <SelectedMarketPanel
          market={data.selectedMarket}
          candles={data.candles}
          activeCandleUnit={data.activeCandleUnit}
        />
      </div>
      <aside className="min-h-[520px] rounded-md border border-border bg-card p-4">
        <p className="text-sm font-semibold text-muted-foreground">Market List</p>
      </aside>
    </section>
  );
}
```

- [ ] **Step 3: build 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm build
```

Expected:

```text
Compiled successfully
```

## Task 5: Stage 4 검증과 커밋

**Files:**
- Verify: `apps/web/src/features/market-dashboard/components`

- [ ] **Step 1: lint 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm lint
```

Expected:

```text
No ESLint warnings or errors
```

- [ ] **Step 2: test 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm test
```

Expected:

```text
Test Files  pass
Tests  pass
```

- [ ] **Step 3: Stage 4 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/features/market-dashboard/components
git commit -m "feat(web): add mock selected market chart"
```

Expected:

```text
[branch commit] feat(web): add mock selected market chart
```

# Market Dashboard Mock Stage 5 Panels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 오른쪽 Market List, chart 아래 Orderbook/Recent Trades, 하단 Market Table을 mock 데이터로 렌더링해 데스크톱 풀 레이아웃을 완성한다.

**Architecture:** Market discovery, orderbook, trades, bottom table은 각각 독립 panel component로 분리한다. 모든 panel은 Stage 2의 mock view model과 formatter를 사용하고 실제 click/search/filter 동작은 만들지 않는다.

**Tech Stack:** shadcn/ui Tabs/Table/ScrollArea/Card/InputGroup/Select/Button/Badge/Tooltip, lucide-react Star/Search, Tailwind v4 semantic tokens.

---

## 파일 구조

- Modify: `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx`
- Create: `apps/web/src/features/market-dashboard/components/market-discovery-panel.tsx`
- Create: `apps/web/src/features/market-dashboard/components/orderbook-panel.tsx`
- Create: `apps/web/src/features/market-dashboard/components/recent-trades-panel.tsx`
- Create: `apps/web/src/features/market-dashboard/components/market-detail-grid.tsx`
- Create: `apps/web/src/features/market-dashboard/components/market-table-panel.tsx`

## Task 1: 오른쪽 Market Discovery panel 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/market-discovery-panel.tsx`

- [ ] **Step 1: Market Discovery panel component 작성**

Create `apps/web/src/features/market-dashboard/components/market-discovery-panel.tsx`:

```tsx
import { MoreHorizontal, Plus, Star } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
} from "../lib/formatters";
import type { MarketCategory, MarketRow } from "../types";

const categories: Array<{ value: MarketCategory; label: string }> = [
  { value: "interest", label: "관심" },
  { value: "KRW", label: "KRW" },
  { value: "BTC", label: "BTC" },
  { value: "USDT", label: "USDT" },
  { value: "holding", label: "보유" },
];

type MarketDiscoveryPanelProps = {
  markets: MarketRow[];
  activeCategory: MarketCategory;
};

export function MarketDiscoveryPanel({ markets, activeCategory }: MarketDiscoveryPanelProps) {
  return (
    <Card className="flex h-[calc(100vh-148px)] min-h-[640px] flex-col overflow-hidden rounded-md border-border bg-card p-0 shadow-none">
      <div className="flex h-14 items-center justify-between border-b border-border px-4">
        <Tabs value={activeCategory}>
          <TabsList className="h-10 bg-transparent p-0">
            {categories.map((category) => (
              <TabsTrigger key={category.value} value={category.value} className="h-10 px-4">
                {category.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Market 추가">
                <Plus data-icon="icon" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Market 추가</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Market list 옵션">
                <MoreHorizontal data-icon="icon" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Market list 옵션</TooltipContent>
          </Tooltip>
        </div>
      </div>

      <div className="grid grid-cols-[40px_minmax(110px,1fr)_96px_78px_104px] border-b border-border px-4 py-2 text-[12px] font-semibold text-muted-foreground">
        <span />
        <span>Market</span>
        <span className="text-right">현재가</span>
        <span className="text-right">전일대비</span>
        <span className="text-right">거래대금(24H)</span>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col">
          {markets.map((market) => {
            const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

            return (
              <div
                key={market.market}
                className={cn(
                  "grid min-h-14 grid-cols-[40px_minmax(110px,1fr)_96px_78px_104px] items-center border-b border-border px-4 text-[13px]",
                  market.selected && "bg-accent",
                )}
              >
                <Button variant="ghost" size="icon" aria-label={`${market.market} 관심`}>
                  <Star
                    data-icon="icon"
                    className={market.favorite ? "fill-primary text-primary" : "text-muted-foreground"}
                  />
                </Button>
                <div className="min-w-0">
                  <div className="truncate font-bold">{market.market}</div>
                  <div className="truncate text-[12px] font-medium text-muted-foreground">{market.koreanName}</div>
                </div>
                <div className="text-right font-bold tabular-nums text-primary">
                  {formatKrwPrice(market.currentPrice)}
                </div>
                <div className="text-right font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise" data-side={side}>
                  {formatChangeRate(market.changeRate)}
                </div>
                <div className="text-right text-[12px] font-semibold tabular-nums">
                  {formatCompactKoreanAmount(market.tradeValue24h)}
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
      <div className="border-t border-border px-4 py-3">
        <Badge variant="secondary">Mock Market List</Badge>
      </div>
    </Card>
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

## Task 2: Orderbook panel 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/orderbook-panel.tsx`

- [ ] **Step 1: Orderbook panel component 작성**

Create `apps/web/src/features/market-dashboard/components/orderbook-panel.tsx`:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { formatKrwPrice, formatMarketSize } from "../lib/formatters";
import type { OrderbookRow } from "../types";

type OrderbookPanelProps = {
  rows: OrderbookRow[];
};

export function OrderbookPanel({ rows }: OrderbookPanelProps) {
  return (
    <Card className="rounded-md border-border bg-card shadow-none">
      <CardHeader className="border-b border-border px-4 py-3">
        <CardTitle className="text-[17px]">호가</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-0 p-0">
        <div className="border-r border-border">
          <div className="grid grid-cols-3 px-4 py-2 text-[12px] font-semibold text-muted-foreground">
            <span>수량(BTC)</span>
            <span className="text-right">매수호가</span>
            <span className="text-right">누적</span>
          </div>
          {rows
            .filter((row) => row.side === "bid")
            .map((row) => (
              <div key={`${row.side}-${row.price}`} className="relative grid h-8 grid-cols-3 items-center px-4 text-[12px]">
                <div
                  className="absolute inset-y-0 right-0 bg-fall/10"
                  style={{ width: `${row.depthRatio}%` }}
                />
                <span className="relative tabular-nums">{formatMarketSize(row.size)}</span>
                <span className="relative text-right font-semibold tabular-nums text-fall">
                  {formatKrwPrice(row.price)}
                </span>
                <span className="relative text-right tabular-nums text-muted-foreground">
                  {formatMarketSize(row.total)}
                </span>
              </div>
            ))}
        </div>
        <div>
          <div className="grid grid-cols-3 px-4 py-2 text-[12px] font-semibold text-muted-foreground">
            <span className="text-right">누적</span>
            <span className="text-right">매도호가</span>
            <span className="text-right">수량(BTC)</span>
          </div>
          {rows
            .filter((row) => row.side === "ask")
            .map((row) => (
              <div key={`${row.side}-${row.price}`} className="relative grid h-8 grid-cols-3 items-center px-4 text-[12px]">
                <div
                  className="absolute inset-y-0 left-0 bg-rise/10"
                  style={{ width: `${row.depthRatio}%` }}
                />
                <span className="relative text-right tabular-nums text-muted-foreground">
                  {formatMarketSize(row.total)}
                </span>
                <span className="relative text-right font-semibold tabular-nums text-rise">
                  {formatKrwPrice(row.price)}
                </span>
                <span className="relative text-right tabular-nums">{formatMarketSize(row.size)}</span>
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  );
}
```

## Task 3: Recent Trades panel 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/recent-trades-panel.tsx`

- [ ] **Step 1: Recent Trades panel component 작성**

Create `apps/web/src/features/market-dashboard/components/recent-trades-panel.tsx`:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

import { formatKrwPrice, formatMarketSize } from "../lib/formatters";
import type { TradeRow } from "../types";

type RecentTradesPanelProps = {
  trades: TradeRow[];
};

export function RecentTradesPanel({ trades }: RecentTradesPanelProps) {
  return (
    <Card className="rounded-md border-border bg-card shadow-none">
      <CardHeader className="border-b border-border px-4 py-3">
        <CardTitle className="text-[17px]">체결</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="h-9 px-4 text-[12px]">시간</TableHead>
              <TableHead className="h-9 px-4 text-right text-[12px]">체결가(KRW)</TableHead>
              <TableHead className="h-9 px-4 text-right text-[12px]">수량(BTC)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trades.map((trade) => (
              <TableRow key={`${trade.time}-${trade.price}-${trade.size}`} className="h-8">
                <TableCell className="px-4 py-1 text-[12px] text-muted-foreground">{trade.time}</TableCell>
                <TableCell className="px-4 py-1 text-right text-[12px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise" data-side={trade.side}>
                  {formatKrwPrice(trade.price)}
                </TableCell>
                <TableCell className="px-4 py-1 text-right text-[12px] tabular-nums">
                  {formatMarketSize(trade.size)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
```

## Task 4: Market detail grid 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/market-detail-grid.tsx`

- [ ] **Step 1: detail grid component 작성**

Create `apps/web/src/features/market-dashboard/components/market-detail-grid.tsx`:

```tsx
import type { OrderbookRow, TradeRow } from "../types";
import { OrderbookPanel } from "./orderbook-panel";
import { RecentTradesPanel } from "./recent-trades-panel";

type MarketDetailGridProps = {
  orderbook: OrderbookRow[];
  trades: TradeRow[];
};

export function MarketDetailGrid({ orderbook, trades }: MarketDetailGridProps) {
  return (
    <section className="grid gap-3 lg:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.8fr)]">
      <OrderbookPanel rows={orderbook} />
      <RecentTradesPanel trades={trades} />
    </section>
  );
}
```

## Task 5: 하단 Market Table panel 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/market-table-panel.tsx`

- [ ] **Step 1: Market Table panel component 작성**

Create `apps/web/src/features/market-dashboard/components/market-table-panel.tsx`:

```tsx
import { Search, Star } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import {
  formatChangeRate,
  formatCompactKoreanAmount,
  formatKrwPrice,
  formatMarketSize,
} from "../lib/formatters";
import type { MarketRow } from "../types";
import { Sparkline } from "./sparkline";

type MarketTablePanelProps = {
  markets: MarketRow[];
};

export function MarketTablePanel({ markets }: MarketTablePanelProps) {
  return (
    <Card className="rounded-md border-border bg-card shadow-none">
      <CardHeader className="flex-row items-center justify-between border-b border-border px-4 py-3">
        <Tabs value="all">
          <TabsList className="h-9 bg-transparent p-0">
            <TabsTrigger value="all">전체</TabsTrigger>
            <TabsTrigger value="KRW">KRW</TabsTrigger>
            <TabsTrigger value="BTC">BTC</TabsTrigger>
            <TabsTrigger value="USDT">USDT</TabsTrigger>
            <TabsTrigger value="holding">보유</TabsTrigger>
            <TabsTrigger value="interest">관심</TabsTrigger>
          </TabsList>
        </Tabs>
        <div className="flex items-center gap-2">
          <Select value="all">
            <SelectTrigger className="h-9 w-[140px]">
              <SelectValue placeholder="전체 Market" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">전체 Market</SelectItem>
              <SelectItem value="krw">KRW Market</SelectItem>
              <SelectItem value="favorites">관심 Market</SelectItem>
            </SelectContent>
          </Select>
          <InputGroup className="h-9 w-[220px] bg-muted">
            <InputGroupAddon>
              <Search data-icon="inline-start" />
            </InputGroupAddon>
            <InputGroupInput placeholder="Market 검색" aria-label="Market table search" />
          </InputGroup>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[220px] px-4">Market</TableHead>
              <TableHead className="text-right">현재가</TableHead>
              <TableHead className="text-right">전일대비</TableHead>
              <TableHead className="text-right">거래량(24H)</TableHead>
              <TableHead className="text-right">거래대금(24H)</TableHead>
              <TableHead className="text-right">시가</TableHead>
              <TableHead className="text-right">고가</TableHead>
              <TableHead className="text-right">저가</TableHead>
              <TableHead className="w-[110px] text-right">차트(1일)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {markets.map((market) => {
              const side = market.changeRate > 0 ? "rise" : market.changeRate < 0 ? "fall" : "flat";

              return (
                <TableRow key={market.market} className="h-[56px]">
                  <TableCell className="px-4">
                    <div className="flex items-center gap-3">
                      <Button variant="ghost" size="icon" aria-label={`${market.market} 관심`}>
                        <Star
                          data-icon="icon"
                          className={market.favorite ? "fill-primary text-primary" : "text-muted-foreground"}
                        />
                      </Button>
                      <div className="min-w-0">
                        <div className="truncate font-bold">{market.market}</div>
                        <div className="truncate text-[12px] text-muted-foreground">{market.koreanName}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-bold tabular-nums text-primary">
                    {formatKrwPrice(market.currentPrice)}
                  </TableCell>
                  <TableCell className="text-right font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise" data-side={side}>
                    {formatChangeRate(market.changeRate)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{formatMarketSize(market.tradeVolume24h)}</TableCell>
                  <TableCell className="text-right tabular-nums">{formatCompactKoreanAmount(market.tradeValue24h)}</TableCell>
                  <TableCell className="text-right tabular-nums text-rise">{formatKrwPrice(market.openPrice)}</TableCell>
                  <TableCell className="text-right tabular-nums text-rise">{formatKrwPrice(market.highPrice)}</TableCell>
                  <TableCell className="text-right tabular-nums text-fall">{formatKrwPrice(market.lowPrice)}</TableCell>
                  <TableCell className="pr-4">
                    <div className="flex justify-end">
                      <Sparkline values={market.sparkline} variant={side === "rise" ? "rise" : side === "fall" ? "fall" : "muted"} />
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
```

## Task 6: shell에 모든 panel 연결

**Files:**
- Modify: `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx`

- [ ] **Step 1: Shell component 교체**

Replace `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx` with:

```tsx
import type { MarketDashboardMockData } from "../types";
import { MarketDetailGrid } from "./market-detail-grid";
import { MarketDiscoveryPanel } from "./market-discovery-panel";
import { MarketTablePanel } from "./market-table-panel";
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
        <MarketDetailGrid orderbook={data.orderbook} trades={data.trades} />
        <MarketTablePanel markets={data.markets} />
      </div>
      <MarketDiscoveryPanel markets={data.markets} activeCategory={data.activeCategory} />
    </section>
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

## Task 7: Stage 5 검증과 커밋

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

- [ ] **Step 2: build 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm build
```

Expected:

```text
Compiled successfully
```

- [ ] **Step 3: Stage 5 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/features/market-dashboard/components
git commit -m "feat(web): complete mock market dashboard panels"
```

Expected:

```text
[branch commit] feat(web): complete mock market dashboard panels
```

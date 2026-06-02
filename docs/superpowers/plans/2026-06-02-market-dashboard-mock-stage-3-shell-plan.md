# Market Dashboard Mock Stage 3 Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mock 데이터 기반 dashboard의 top navigation, index strip, desktop shell 구조를 렌더링한다.

**Architecture:** `src/app/page.tsx`는 mock data를 feature component로 전달하는 얇은 entrypoint로 유지한다. shell, top navigation, index strip은 `src/features/market-dashboard/components` 아래의 focused component로 분리한다.

**Tech Stack:** Next.js Server Component entrypoint, shadcn/ui Button/InputGroup/Tooltip/Separator, lucide-react icons, Tailwind v4 semantic tokens.

---

## 파일 구조

- Modify: `apps/web/src/app/page.tsx`
- Create: `apps/web/src/features/market-dashboard/components/dashboard-page.tsx`
- Create: `apps/web/src/features/market-dashboard/components/dashboard-top-nav.tsx`
- Create: `apps/web/src/features/market-dashboard/components/index-strip.tsx`
- Create: `apps/web/src/features/market-dashboard/components/sparkline.tsx`
- Create: `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx`

## Task 1: dashboard page entrypoint 작성

**Files:**
- Modify: `apps/web/src/app/page.tsx`
- Create: `apps/web/src/features/market-dashboard/components/dashboard-page.tsx`

- [ ] **Step 1: feature page component 생성**

Create `apps/web/src/features/market-dashboard/components/dashboard-page.tsx`:

```tsx
import type { MarketDashboardMockData } from "../types";
import { DashboardTopNav } from "./dashboard-top-nav";
import { IndexStrip } from "./index-strip";
import { MarketDashboardShell } from "./market-dashboard-shell";

type DashboardPageProps = {
  data: MarketDashboardMockData;
};

export function DashboardPage({ data }: DashboardPageProps) {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <DashboardTopNav />
      <IndexStrip indexes={data.indexes} />
      <MarketDashboardShell data={data} />
    </main>
  );
}
```

- [ ] **Step 2: app page를 mock dashboard로 교체**

Replace `apps/web/src/app/page.tsx` with:

```tsx
import { DashboardPage } from "@/features/market-dashboard/components/dashboard-page";
import { mockMarketDashboardData } from "@/features/market-dashboard/mock/dashboard";

export default function Home() {
  return <DashboardPage data={mockMarketDashboardData} />;
}
```

- [ ] **Step 3: typecheck 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm exec tsc --noEmit
```

Expected:

```text
FAIL Cannot find module './dashboard-top-nav'
```

## Task 2: Top Navigation 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/dashboard-top-nav.tsx`

- [ ] **Step 1: Top Navigation component 작성**

Create `apps/web/src/features/market-dashboard/components/dashboard-top-nav.tsx`:

```tsx
import {
  Bell,
  ChevronDown,
  Globe,
  Moon,
  Search,
  Sun,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = ["마켓", "거래", "입출금", "투자내역", "코인동향", "서비스"];

export function DashboardTopNav() {
  return (
    <TooltipProvider>
      <header className="sticky top-0 z-10 border-b border-border bg-card">
        <div className="grid h-[60px] grid-cols-[auto_1fr_auto] items-center gap-6 px-5">
          <div className="flex items-center gap-5">
            <Button className="size-8 rounded-[10px]" size="icon" aria-label="Upbit dashboard">
              <span className="size-3 rounded-[4px] border border-primary-foreground/60" />
            </Button>
            <nav className="flex items-center gap-1" aria-label="Primary">
              {navItems.map((item) => (
                <Button
                  key={item}
                  variant="ghost"
                  className="h-[60px] rounded-none border-b-2 border-transparent px-4 text-[15px] font-semibold data-[active=true]:border-primary data-[active=true]:text-foreground"
                  data-active={item === "마켓"}
                >
                  {item}
                </Button>
              ))}
            </nav>
          </div>

          <div className="mx-auto w-full max-w-[420px]">
            <InputGroup className="h-10 rounded-full bg-muted">
              <InputGroupAddon>
                <Search data-icon="inline-start" />
              </InputGroupAddon>
              <InputGroupInput placeholder="코인명 또는 심볼 검색" aria-label="Market search" />
              <InputGroupAddon>
                <ChevronDown data-icon="inline-end" />
              </InputGroupAddon>
            </InputGroup>
          </div>

          <div className="flex items-center gap-3">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="밝은 테마">
                  <Sun data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>밝은 테마</TooltipContent>
            </Tooltip>
            <Switch aria-label="테마 전환" checked />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="어두운 테마">
                  <Moon data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>어두운 테마</TooltipContent>
            </Tooltip>
            <Separator orientation="vertical" className="h-5" />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="알림">
                  <Bell data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>알림</TooltipContent>
            </Tooltip>
            <Button variant="ghost" className="gap-1 px-2">
              <Globe data-icon="inline-start" />
              KO
              <ChevronDown data-icon="inline-end" />
            </Button>
          </div>
        </div>
      </header>
    </TooltipProvider>
  );
}
```

- [ ] **Step 2: typecheck로 다음 누락 component 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm exec tsc --noEmit
```

Expected:

```text
FAIL Cannot find module './index-strip'
```

## Task 3: Sparkline과 Index Strip 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/sparkline.tsx`
- Create: `apps/web/src/features/market-dashboard/components/index-strip.tsx`

- [ ] **Step 1: Sparkline component 작성**

Create `apps/web/src/features/market-dashboard/components/sparkline.tsx`:

```tsx
import { cn } from "@/lib/utils";

type SparklineProps = {
  values: number[];
  className?: string;
  variant?: "rise" | "fall" | "muted";
};

function toPath(values: number[]) {
  const width = 72;
  const height = 28;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export function Sparkline({ values, className, variant = "muted" }: SparklineProps) {
  const strokeClass =
    variant === "rise"
      ? "stroke-rise"
      : variant === "fall"
        ? "stroke-fall"
        : "stroke-muted-foreground";

  return (
    <svg
      viewBox="0 0 72 28"
      role="img"
      aria-label="추세선"
      className={cn("h-7 w-[72px] overflow-visible", className)}
    >
      <path
        d={toPath(values)}
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={cn("stroke-[1.8]", strokeClass)}
      />
    </svg>
  );
}
```

- [ ] **Step 2: Index Strip component 작성**

Create `apps/web/src/features/market-dashboard/components/index-strip.tsx`:

```tsx
import type { IndexStripItem } from "../types";
import { formatChangeRate } from "../lib/formatters";
import { Sparkline } from "./sparkline";

type IndexStripProps = {
  indexes: IndexStripItem[];
};

export function IndexStrip({ indexes }: IndexStripProps) {
  return (
    <section className="border-b border-border bg-background px-5 py-2" aria-label="Market indexes">
      <div className="grid grid-cols-6 overflow-hidden rounded-md border border-border bg-card">
        {indexes.map((item) => (
          <article
            key={item.label}
            className="grid min-h-[76px] grid-cols-[1fr_auto] items-center gap-3 border-r border-border px-5 last:border-r-0"
          >
            <div className="flex flex-col gap-1">
              <span className="text-[12px] font-semibold text-muted-foreground">{item.label}</span>
              <div className="flex items-baseline gap-3">
                <strong className="font-sans text-[18px] font-bold leading-none tabular-nums">
                  {item.value}
                </strong>
                <span
                  className="text-[13px] font-semibold tabular-nums data-[side=fall]:text-fall data-[side=rise]:text-rise"
                  data-side={item.side}
                >
                  {formatChangeRate(item.changeRate)}
                </span>
              </div>
            </div>
            <Sparkline
              values={item.sparkline}
              variant={item.side === "rise" ? "rise" : item.side === "fall" ? "fall" : "muted"}
            />
          </article>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 3: typecheck로 shell 누락 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm exec tsc --noEmit
```

Expected:

```text
FAIL Cannot find module './market-dashboard-shell'
```

## Task 4: Dashboard Shell 초기 구조 작성

**Files:**
- Create: `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx`

- [ ] **Step 1: shell component 작성**

Create `apps/web/src/features/market-dashboard/components/market-dashboard-shell.tsx`:

```tsx
import type { MarketDashboardMockData } from "../types";

type MarketDashboardShellProps = {
  data: MarketDashboardMockData;
};

export function MarketDashboardShell({ data }: MarketDashboardShellProps) {
  return (
    <section className="grid gap-3 px-5 py-3 xl:grid-cols-[minmax(0,74%)_minmax(360px,26%)]">
      <div className="flex min-w-0 flex-col gap-3 rounded-md border border-border bg-card p-4">
        <p className="text-sm font-semibold text-muted-foreground">Selected Market</p>
        <h1 className="text-[32px] font-bold tabular-nums">{data.selectedMarket.market}</h1>
      </div>
      <aside className="min-h-[520px] rounded-md border border-border bg-card p-4">
        <p className="text-sm font-semibold text-muted-foreground">Market List</p>
      </aside>
    </section>
  );
}
```

- [ ] **Step 2: typecheck 통과 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm exec tsc --noEmit
```

Expected:

```text
No TypeScript errors
```

## Task 5: Stage 3 검증과 커밋

**Files:**
- Verify: `apps/web/src/app/page.tsx`
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

- [ ] **Step 3: Stage 3 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/app/page.tsx apps/web/src/features/market-dashboard/components
git commit -m "feat(web): add market dashboard shell"
```

Expected:

```text
[branch commit] feat(web): add market dashboard shell
```

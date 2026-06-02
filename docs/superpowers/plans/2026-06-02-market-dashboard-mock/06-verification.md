# Market Dashboard Mock Stage 6 Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mock dashboard가 spec의 완료 기준을 만족하는지 자동 테스트, build, 브라우저 screenshot, visual checklist로 검증한다.

**Architecture:** 검증 단계는 코드 기능을 확장하지 않는다. Next.js dev server를 실행하고 browser screenshot으로 chart blank 여부, text overlap, panel balance를 확인한 뒤 필요한 작은 CSS 조정만 같은 stage에서 처리한다.

**Tech Stack:** pnpm lint/test/build, Next.js dev server, Browser plugin 또는 Playwright, desktop viewport 1440x900과 1728x1117.

---

## 파일 구조

- Verify: `apps/web`
- Modify if needed: `apps/web/src/features/market-dashboard/components/*.tsx`
- Modify if needed: `apps/web/src/app/globals.css`

## Task 1: 자동 검증 실행

**Files:**
- Verify: `apps/web`

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

## Task 2: dev server 실행

**Files:**
- Verify: `apps/web`

- [ ] **Step 1: Next.js dev server 시작**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm dev
```

Expected:

```text
Local: http://localhost:3000
```

- [ ] **Step 2: 이미 3000 포트가 사용 중이면 3001 사용**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm dev -- -p 3001
```

Expected:

```text
Local: http://localhost:3001
```

## Task 3: 브라우저 검증

**Files:**
- Verify: `apps/web/src/features/market-dashboard/components`

- [ ] **Step 1: desktop 1440x900 확인**

Open:

```text
http://localhost:3000
```

Viewport:

```text
1440x900
```

Expected:

```text
Top Navigation visible
Index Strip visible
Selected Market chart visible
Right Market List visible
Orderbook visible below chart
Recent Trades visible beside Orderbook
Bottom Market Table begins below detail panels
```

- [ ] **Step 2: desktop 1728x1117 확인**

Open:

```text
http://localhost:3000
```

Viewport:

```text
1728x1117
```

Expected:

```text
Main column appears around 70-76 percent width
Right discovery panel appears around 24-30 percent width
Chart is the dominant visual area
Right list scroll area is not visually detached
```

- [ ] **Step 3: chart canvas 확인**

Inspect the chart area visually.

Expected:

```text
Candlestick marks render
Volume bars render
Price axis render
Time axis render
Chart area is not blank
```

- [ ] **Step 4: typography와 token 확인**

Inspect the rendered page visually.

Expected:

```text
Pretendard is used for Korean labels
Background uses DESIGN.md porcelain background
Cards use white surface
Borders use hairline token
Rise values are red
Fall values are blue
```

- [ ] **Step 5: overlap 확인**

Inspect the rendered page visually.

Expected:

```text
No button text overflows
No table text overlaps adjacent cells
No chart toolbar overlaps chart canvas
No right Market List rows overflow horizontally
```

## Task 4: small visual correction pass

**Files:**
- Modify if needed: `apps/web/src/features/market-dashboard/components/*.tsx`
- Modify if needed: `apps/web/src/app/globals.css`

- [ ] **Step 1: text overflow가 있으면 row/container width 조정**

For table overflow, change fixed columns to minimum-safe values. Example patch target:

```tsx
<TableHead className="w-[220px] px-4">Market</TableHead>
```

Use this replacement when the Market column is too narrow:

```tsx
<TableHead className="w-[260px] px-4">Market</TableHead>
```

Expected:

```text
Market names and Korean names remain inside the first column
```

- [ ] **Step 2: chart가 blank이면 container min height 확인**

For chart blank caused by zero-height container, ensure `LightweightCandleChart` root has fixed visual height:

```tsx
<div className="relative min-h-[430px] border-t border-border">
  <div ref={containerRef} className="h-[430px] w-full" aria-label="Mock candle chart" />
</div>
```

Expected:

```text
Chart renders after refresh
```

- [ ] **Step 3: 오른쪽 panel 높이가 어색하면 shell height 조정**

For right panel height imbalance, use:

```tsx
<Card className="flex h-[calc(100vh-148px)] min-h-[640px] flex-col overflow-hidden rounded-md border-border bg-card p-0 shadow-none">
```

Expected:

```text
Right panel aligns with top chart and stays scrollable
```

## Task 5: 최종 자동 검증 재실행

**Files:**
- Verify: `apps/web`

- [ ] **Step 1: lint 재실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm lint
```

Expected:

```text
No ESLint warnings or errors
```

- [ ] **Step 2: test 재실행**

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

- [ ] **Step 3: build 재실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm build
```

Expected:

```text
Compiled successfully
```

## Task 6: Stage 6 커밋과 완료 보고

**Files:**
- Stage: visual correction files changed in Task 4

- [ ] **Step 1: 변경 파일 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git status --short
```

Expected:

```text
Only Stage 6 visual correction files are unstaged
```

- [ ] **Step 2: 시각 보정이 있었으면 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/features/market-dashboard/components apps/web/src/app/globals.css
git commit -m "fix(web): polish mock dashboard layout"
```

Expected:

```text
[branch commit] fix(web): polish mock dashboard layout
```

- [ ] **Step 3: 시각 보정이 없으면 커밋 생략**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git diff --quiet
```

Expected:

```text
Exit code 0 when no visual correction files changed
```

- [ ] **Step 4: 완료 보고에 포함할 내용 정리**

Report:

```text
Dev server URL
lint/test/build 결과
검증 viewport
chart blank 여부
남은 design risk
```

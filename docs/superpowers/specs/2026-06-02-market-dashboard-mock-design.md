# Market Dashboard Mock 디자인 프로토타입 설계

작성일: 2026-06-02

## 목적

이 설계는 Upbit dashboard frontend의 1차 화면 디자인을 검증하기 위해 Mock 데이터 기반 데스크톱 풀 레이아웃을 구현하는 방향을 고정한다.

이번 단계의 목표는 실제 REST 또는 WebSocket 데이터를 연결하는 것이 아니다. 목표는 `DESIGN.md`와 `design.shadcn.css`의 시각 기준이 실제 Next.js 화면에서 잘 동작하는지 확인하고, Market dashboard의 주요 UI 영역이 같은 화면 밀도 안에서 균형 있게 보이는지 검증하는 것이다.

이 단계가 끝나면 사용자는 브라우저에서 다음 영역이 모두 포함된 데스크톱 대시보드 시안을 볼 수 있어야 한다.

- Top Navigation
- Index Strip
- Selected Market header
- Lightweight Charts 기반 mock candle chart
- 오른쪽 Market List discovery panel
- Orderbook panel
- Recent Trades panel
- 하단 전체 Market Table

## 근거 문서

- `CONTEXT.md`: Market, Selected Market, Market List, Ticker event, Trade event, Orderbook event, Candle event, Candle Unit, Quotation data 용어.
- `apps/web/AGENTS.md`: frontend 작업 전 `DESIGN.md`를 읽고 shadcn semantic token을 우선 사용해야 한다는 지침.
- `apps/web/DESIGN.md`: light-first fintech dashboard, 네 구역 desktop layout, chart 중심 구조, orderbook/trades/Market Table 구성.
- `apps/web/design.shadcn.css`: shadcn/ui semantic token bridge.
- `apps/web/design.tailwind.css`: DESIGN.md 기반 Tailwind v4 token export.
- `docs/adr/0003-rest-bff-and-direct-websocket.md`: REST는 Next.js BFF, realtime WebSocket은 FastAPI 직접 연결. 이번 단계에서는 둘 다 연결하지 않는다.
- `docs/adr/0005-quotation-only-mvp-boundary.md`: MVP는 공개 Quotation data만 사용하고 order form 또는 trading 기능은 제외한다.
- `docs/adr/0006-api-contract-envelope-and-model-source.md`: 실제 API 연결 단계에서는 Message envelope와 backend Pydantic 모델이 계약 원천이다.

## 범위

### 포함

- `apps/web` shadcn/ui 초기 환경설정.
- `DESIGN.md` token이 실제 global CSS와 shadcn semantic classes에 연결되는 구조.
- Pretendard variable font를 `next/font/local`로 적용.
- `lucide-react` 아이콘 사용.
- `lightweight-charts` 기반 mock candle chart.
- Mock 데이터 fixture:
  - indexes
  - markets
  - candles
  - orderbook
  - trades
- 데스크톱 풀 레이아웃 구현.
- 주요 UI 영역별 컴포넌트 경계 정리.
- Light/Dark token이 깨지지 않는 CSS 구조.
- 디자인 확인을 위한 브라우저 실행과 screenshot 검증.

### 제외

- 실제 `/api/markets`, `/api/candles`, `/api/snapshot` 호출.
- FastAPI WebSocket 연결.
- TanStack Query 도입.
- Zustand store 도입.
- Zod runtime validation 도입.
- Storybook 설정.
- 실제 검색 동작.
- 실제 tab 전환 또는 filter 상태 관리.
- 즐겨찾기 저장.
- order submission, simulated order, account, portfolio, login.
- 모바일 최적화 완성.
- TradingView Advanced Charts 또는 Trading Platform 도입.

## 핵심 결정

### 1. 1차는 데스크톱 풀 레이아웃으로 만든다

상단, 메인 차트, 오른쪽 Market List까지만 만들면 거래소형 dashboard의 실제 정보 밀도를 판단하기 어렵다.

따라서 1차 디자인 검증은 데스크톱 풀 레이아웃 전체를 대상으로 한다. 기능 동작은 최소화하되, 화면에 필요한 주요 정보 영역은 모두 배치한다.

### 2. Mock 데이터 어댑터를 둔다

UI는 실제 데이터처럼 렌더링하되 데이터 원천은 local fixture로 둔다.

```text
(mock fixtures)
  -> dashboard view model
  -> UI components
```

나중에 실제 REST/WebSocket 연결 단계에서 fixture만 data provider로 교체할 수 있도록, UI 컴포넌트는 가능한 한 plain props를 받는다.

### 3. 이벤트 동작은 시각 상태만 표현한다

이번 단계에서 버튼, tab, 검색, favorite, chart option은 실제 동작을 구현하지 않는다.

정책:

- active tab은 초기값만 표시한다.
- 검색 input은 입력 가능한 UI로만 둔다.
- favorite star는 mock state 값을 그대로 표시한다.
- theme toggle은 UI만 둔다. 실제 dark mode 전환은 별도 단계에서 다룬다.
- chart timeframe toggle은 선택된 시각 상태만 표시한다.

### 4. 차트는 Lightweight Charts를 우선 사용한다

`DESIGN.md`의 chart 요구사항은 simple candlestick chart에 가깝다. 따라서 1차는 `lightweight-charts`로 mock candle과 volume을 표시한다.

TradingView Advanced Charts 또는 Trading Platform은 다음 이유로 이번 단계에서 제외한다.

- MVP 범위는 Quotation data only다.
- 주문, broker, advanced trading toolbar가 필요하지 않다.
- 라이선스와 integration 비용이 mock design 검증 단계에 비해 크다.

### 5. Storybook은 후속 단계로 미룬다

Storybook은 component API와 props shape이 안정된 뒤에 가치가 크다. 이번 단계는 화면 구조와 정보 밀도를 먼저 검증하는 작업이므로 Storybook 설정은 제외한다.

## 의존성 정책

### 이번 단계에 추가할 의존성

```text
lucide-react
lightweight-charts
class-variance-authority
clsx
tailwind-merge
```

shadcn/ui CLI가 component source와 필요한 peer/dependency를 추가할 수 있으므로, 실제 implementation plan에서는 `pnpm dlx shadcn@latest info` 결과와 생성 파일을 확인한 뒤 최소 의존성을 고정한다.

### 이번 단계에서 설치할 shadcn/ui 후보

```text
button
card
badge
input
input-group
table
tabs
toggle-group
separator
scroll-area
skeleton
tooltip
dropdown-menu
select
switch
```

`sheet`, `command`, `alert`, `empty`, `chart`는 1차 구현 중 실제 필요성이 확인될 때만 추가한다.

정책:

- layout과 spacing은 `className`으로 조정한다.
- 색상과 typography는 shadcn semantic token과 DESIGN.md token을 우선한다.
- raw Tailwind color class는 사용하지 않는다.
- `space-x-*`, `space-y-*` 대신 `gap-*`를 사용한다.
- icon-only action에는 `Tooltip`을 붙인다.

### 후속 단계로 미룰 의존성

| 의존성 | 도입 시점 | 이유 |
| --- | --- | --- |
| `zustand` | cross-panel UI state가 실제 동작할 때 | `selectedMarket`, `candleUnit`, `marketSearch`, panel tab state가 여러 컴포넌트에 걸쳐 공유될 때 필요하다. Next.js App Router에서는 store provider 경계를 신중히 잡아야 한다. |
| `@tanstack/react-query` | REST BFF data loading 단계 | 서버 상태 fetching, caching, synchronization이 시작될 때 필요하다. Mock fixture 렌더링만 하는 1차 디자인에는 필요하지 않다. |
| `zod` | API/Event runtime validation 단계 | BFF 응답과 WebSocket event를 runtime에서 검증할 때 필요하다. 이번 단계에서는 backend 계약을 호출하지 않는다. |
| `storybook` | 컴포넌트 경계 안정 후 | 1차 화면 구조가 승인된 뒤 panel/table/chart component 문서화에 사용한다. |

## Font 정책

Pretendard variable font를 local asset으로 둔다.

```text
apps/web/src/app/fonts/PretendardVariable.woff2
```

Next.js App Router에서는 `next/font/local`로 로드한다.

예상 구조:

```tsx
import localFont from "next/font/local";

const pretendard = localFont({
  src: "./fonts/PretendardVariable.woff2",
  variable: "--font-pretendard",
  weight: "100 900",
  display: "swap",
});
```

`layout.tsx`의 `html` class에 `pretendard.variable`을 연결하고, Tailwind v4 `@theme inline`에서 `--font-sans`를 `var(--font-pretendard)`로 연결한다.

기존 Geist font는 1차 dashboard 화면에서는 제거하거나 fallback으로만 남긴다. dashboard의 기본 Korean/Numeric typography는 Pretendard가 담당한다.

## Icon 정책

아이콘은 `lucide-react`를 사용한다.

초기 사용 후보:

| 위치 | 아이콘 후보 |
| --- | --- |
| 검색 | `Search` |
| favorite | `Star` |
| 알림 | `Bell` |
| 언어/지역 | `Globe` |
| 테마 | `Sun`, `Moon` |
| dropdown | `ChevronDown` |
| 추가 액션 | `Plus`, `MoreHorizontal` |
| chart 설정 | `SlidersHorizontal` |
| refresh/status | `RefreshCw`, `Activity` |

정책:

- shadcn `Button` 안의 icon에는 `data-icon` 속성을 사용한다.
- 아이콘 크기는 shadcn component CSS에 맡기고 개별 width/height class를 남발하지 않는다.
- 명확하지 않은 icon-only button에는 tooltip을 붙인다.

## CSS와 Theme 구조

`apps/web/src/app/globals.css`는 app의 실제 global CSS entrypoint다. 여기에서 Tailwind와 디자인 token bridge를 연결한다.

예상 import 순서:

```css
@import "tailwindcss";
@import "../../design.tailwind.css";
@import "../../design.shadcn.css";
```

정책:

- 기본 Next.js 생성 색상 변수는 제거한다.
- `design.shadcn.css`의 `:root`, `.dark`, `@theme inline`, `@layer base`를 유지한다.
- shadcn component는 `bg-background`, `text-foreground`, `bg-card`, `border-border`, `text-muted-foreground`, `bg-primary` 같은 semantic class를 사용한다.
- rise/fall 같은 market movement color는 DESIGN.md token을 사용한다.
- dark mode token은 연결만 유지하고, 실제 theme toggle 동작은 후속 단계에서 다룬다.

## 화면 구조

### 전체 레이아웃

```text
DashboardPage
  -> DashboardTopNav
  -> IndexStrip
  -> DashboardShell
       -> MainColumn
            -> SelectedMarketPanel
            -> MarketDetailGrid
            -> MarketTablePanel
       -> MarketDiscoveryPanel
```

Desktop 비율:

- Main column: 70-76%
- Right discovery panel: 24-30%
- Panel gap: DESIGN.md의 `panel-gap` 기준
- Top navigation: 56-64px
- Index strip: compact full-width row

### Top Navigation

역할:

- 주요 navigation label 표시.
- market search input 표시.
- theme, notification, language action 표시.

shadcn/ui:

- `Button`
- `InputGroup`
- `Input`
- `Tooltip`
- `DropdownMenu`
- `Switch`

이번 단계에서는 navigation click, search result, language selection 동작을 구현하지 않는다.

### Index Strip

역할:

- KOSPI, KOSDAQ, USD/KRW, NASDAQ, S&P 500, BTC dominance 같은 외부 지표 mock을 compact하게 표시한다.

shadcn/ui:

- `Card` 또는 panel container
- `Separator`

시각화:

- Sparkline은 lightweight chart가 아니라 작은 SVG 또는 simple inline sparkline component로 처리한다.

정책:

- 실제 외부 index data가 연결된 것이 아니므로 fixture 이름에서 mock임을 명확히 한다.
- UI 문구에 임의로 "실시간"을 표시하지 않는다.

### Selected Market Panel

역할:

- Selected Market의 symbol, korean/english name, current price, change rate, 24h high/low, trade volume, trade value를 표시한다.
- Candle chart의 header와 controls를 포함한다.

shadcn/ui:

- `Card`
- `Badge`
- `Button`
- `Separator`
- `ToggleGroup`
- `Tooltip`

하위 컴포넌트:

```text
SelectedMarketPanel
  -> SelectedMarketHeader
  -> CandleUnitToggle
  -> LightweightCandleChart
```

정책:

- Selected Market 용어를 사용한다.
- "coin summary" 같은 표현은 피한다.
- 가격 숫자는 tabular number 스타일을 적용한다.
- 한국 시장 관례에 맞춰 rise는 red, fall은 blue를 사용한다.

### LightweightCandleChart

역할:

- mock candle data를 candlestick series로 표시한다.
- volume series를 chart 하단에 표시한다.
- container resize에 반응한다.

입력 shape:

```ts
type CandlePoint = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};
```

정책:

- React client component로 둔다.
- `createChart`와 series lifecycle은 chart component 내부에 가둔다.
- chart theme 값은 CSS variables에서 읽거나 adapter props로 전달한다.
- 이번 단계에서는 realtime update를 구현하지 않는다.
- 이번 단계에서는 crosshair OHLC external tooltip을 필수로 구현하지 않는다.

나중에 TradingView로 교체할 가능성을 위해 상위 panel은 chart library 세부 API를 알지 않게 한다.

### MarketDiscoveryPanel

역할:

- 오른쪽 panel에서 관심/KRW/BTC/USDT/보유 tab과 Market List를 표시한다.
- Selected Market과 같은 row는 blue tint로 강조한다.

shadcn/ui:

- `Tabs`
- `Table` 또는 compact row list
- `ScrollArea`
- `Button`
- `Badge`
- `Skeleton`
- `Tooltip`

정책:

- 오른쪽 panel은 discovery와 favorites에 집중한다.
- main chart header의 Selected Market summary를 반복하지 않는다.
- favorite star는 mock state만 표시한다.

### MarketDetailGrid

역할:

- chart 아래에 Orderbook과 Recent Trades를 나란히 배치한다.

Desktop 구조:

```text
MarketDetailGrid
  -> OrderbookPanel
  -> RecentTradesPanel
```

shadcn/ui:

- `Card`
- `Table`
- `ScrollArea`
- `Separator`

정책:

- orderbook depth bar는 직접 구현한다.
- order submission control은 넣지 않는다.
- Recent Trades는 time, side, price, size만 표시한다.

### MarketTablePanel

역할:

- 하단에 전체 Market Table mock을 표시한다.
- market category tab, market select, search input, table을 포함한다.

shadcn/ui:

- `Tabs`
- `Select`
- `InputGroup`
- `Input`
- `Table`
- `ScrollArea`
- `Badge`

표시 column:

- Market
- Current price
- Change rate
- 24h volume
- 24h trade value
- Open
- High
- Low
- 1d sparkline

정책:

- row height는 48-60px 범위로 둔다.
- table row를 card stack으로 만들지 않는다.
- selected/hover state는 subtle tint와 hairline divider를 사용한다.

## Mock 데이터 구조

Mock fixture는 dashboard feature 내부에 둔다.

예상 구조:

```text
apps/web/src/features/market-dashboard/mock/indexes.ts
apps/web/src/features/market-dashboard/mock/markets.ts
apps/web/src/features/market-dashboard/mock/candles.ts
apps/web/src/features/market-dashboard/mock/orderbook.ts
apps/web/src/features/market-dashboard/mock/trades.ts
```

Mock 데이터는 실제 Upbit field name을 그대로 복사하지 않는다. UI가 쓰기 쉬운 frontend view model shape로 둔다.

예상 type:

```ts
type MarketRow = {
  market: string;
  koreanName: string;
  englishName: string;
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
};
```

```ts
type OrderbookRow = {
  price: number;
  size: number;
  total: number;
  side: "ask" | "bid";
  depthRatio: number;
};
```

```ts
type TradeRow = {
  time: string;
  price: number;
  size: number;
  side: "rise" | "fall";
};
```

정책:

- mock 값은 디자인 확인용이며 실제 market data라고 표시하지 않는다.
- 화면에는 개발용 "mock" badge를 노출하지 않는다. 사용자가 보는 화면은 완성 시안처럼 보여야 한다.
- fixture 파일명과 주석에서만 mock임을 명확히 한다.

## 상태 관리 정책

이번 단계에서는 global client state library를 쓰지 않는다.

정책:

- 선택된 Market은 mock fixture의 `selected` 값 또는 page-level constant로 처리한다.
- active tab과 active candle unit은 initial visual state로만 둔다.
- 검색어, favorite toggle, sort, filter는 실제 상태 변경을 구현하지 않는다.
- chart resize와 chart lifecycle에 필요한 local client state/ref만 사용한다.

후속 단계에서 실제 interaction이 필요해지면 다음 기준으로 상태 도구를 선택한다.

- server state: TanStack Query
- shared client UI state: Zustand
- local visual state: React `useState`

## 접근성

1차 디자인에서도 기본 접근성 구조는 유지한다.

정책:

- icon-only button에는 accessible label 또는 tooltip을 둔다.
- table header를 의미 있게 유지한다.
- tab과 toggle은 shadcn component semantics를 따른다.
- 색상만으로 상승/하락을 전달하지 않고 `+`, `-` 기호와 텍스트 값을 함께 표시한다.
- chart canvas 주변에는 Selected Market과 latest price 텍스트가 별도로 존재해야 한다.

## 테스트와 검증

### 자동 검증

Implementation plan에서 다음 명령을 실행 대상으로 둔다.

```bash
pnpm lint
pnpm test
pnpm build
```

기존 BFF tests가 깨지지 않아야 한다.

### 수동 검증

Next dev server를 실행하고 브라우저에서 dashboard를 확인한다.

검증 항목:

- Pretendard가 적용된다.
- shadcn semantic token이 적용된다.
- `design.shadcn.css`의 background, foreground, card, border, primary token이 화면에 반영된다.
- 데스크톱 화면에서 Top Navigation, Index Strip, main chart, right Market List, orderbook, trades, bottom Market Table이 모두 보인다.
- chart가 blank canvas로 남지 않는다.
- mock candle과 volume이 표시된다.
- 오른쪽 Market List가 화면 높이에 맞춰 scroll된다.
- table text가 cell 밖으로 넘치지 않는다.
- 버튼과 입력이 기존 shadcn style과 DESIGN.md token을 따른다.

### Screenshot 검증

가능하면 Playwright 또는 in-app browser screenshot으로 desktop viewport를 확인한다.

기준 viewport:

```text
1440x900
1728x1117
```

확인 항목:

- chart 영역이 visual center로 보인다.
- 오른쪽 panel이 과하게 넓거나 좁지 않다.
- orderbook/trades가 chart와 단절되어 보이지 않는다.
- 하단 Market Table이 card stack처럼 보이지 않는다.
- text overlap이 없다.

## 구현 순서 초안

구체 구현 순서는 별도 plan에서 고정한다. 이 spec 기준의 예상 순서는 다음과 같다.

1. shadcn/ui 초기화와 `components.json` 생성.
2. `globals.css`에서 Tailwind v4, `design.tailwind.css`, `design.shadcn.css` 연결.
3. Pretendard font asset 추가와 `next/font/local` 연결.
4. shadcn/ui 필수 component 추가.
5. `lucide-react`, `lightweight-charts` 추가.
6. mock fixture와 formatter utility 작성.
7. dashboard layout component 작성.
8. Lightweight chart adapter 작성.
9. orderbook, trades, Market List, Market Table panel 작성.
10. lint/test/build와 browser screenshot 검증.

## 완료 기준

- `apps/web`가 shadcn/ui component를 사용할 수 있는 상태다.
- `DESIGN.md` 기반 CSS token이 실제 app global CSS에 연결되어 있다.
- Pretendard가 dashboard 기본 font로 적용된다.
- `lucide-react` icon이 navigation, search, favorite, option action에 적용된다.
- Mock 데이터 기반 데스크톱 풀 레이아웃이 렌더링된다.
- Lightweight Charts chart가 mock candle과 volume을 표시한다.
- 오른쪽 Market List, Orderbook, Recent Trades, 하단 Market Table이 모두 mock 데이터로 표시된다.
- 버튼, 탭, 검색, favorite은 시각 상태만 제공하며 실제 동작은 구현하지 않는다.
- Zustand, TanStack Query, Zod, Storybook은 설치하지 않는다.
- 기존 BFF tests가 깨지지 않는다.
- `pnpm lint`, `pnpm test`, `pnpm build`가 통과한다.
- 브라우저 screenshot 기준으로 text overlap, blank chart, 깨진 token 적용이 없다.

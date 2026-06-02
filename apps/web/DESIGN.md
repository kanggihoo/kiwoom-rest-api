---
version: alpha
name: Market Visualization Web
description: A light-first, dark-capable fintech market dashboard for Upbit-style crypto market data with a modern Toss/Linear-inspired surface.
colors:
  primary: "#006BFF"
  primary-strong: "#0052CC"
  secondary: "#7B8494"
  tertiary: "#F04452"
  neutral: "#FBFCFF"
  surface: "#FFFFFF"
  surface-muted: "#F3F6FB"
  surface-selected: "#EAF3FF"
  text-primary: "#151B2D"
  text-muted: "#7B8494"
  border: "#E3E8F0"
  rise: "#F04452"
  fall: "#1D6FFF"
  dark-background: "#11131A"
  dark-surface: "#171A23"
  dark-surface-elevated: "#1E2230"
  dark-border: "#2A3040"
  dark-text-primary: "#F4F7FB"
  dark-text-muted: "#9AA3B2"
  dark-primary: "#5EA2FF"
  dark-rise: "#FF5A66"
  dark-fall: "#4D91FF"
typography:
  display-price:
    fontFamily: Pretendard, Inter, Apple SD Gothic Neo, system-ui, sans-serif
    fontSize: 40px
    fontWeight: 700
    lineHeight: 44px
    letterSpacing: 0em
    fontFeature: "'tnum'"
  headline-md:
    fontFamily: Pretendard, Inter, Apple SD Gothic Neo, system-ui, sans-serif
    fontSize: 24px
    fontWeight: 700
    lineHeight: 30px
    letterSpacing: 0em
  section-title:
    fontFamily: Pretendard, Inter, Apple SD Gothic Neo, system-ui, sans-serif
    fontSize: 17px
    fontWeight: 700
    lineHeight: 23px
    letterSpacing: 0em
  body-md:
    fontFamily: Pretendard, Inter, Apple SD Gothic Neo, system-ui, sans-serif
    fontSize: 15px
    fontWeight: 500
    lineHeight: 23px
    letterSpacing: 0em
  table-value:
    fontFamily: Pretendard, Inter, Apple SD Gothic Neo, system-ui, sans-serif
    fontSize: 15px
    fontWeight: 600
    lineHeight: 20px
    letterSpacing: 0em
    fontFeature: "'tnum'"
  label-sm:
    fontFamily: Pretendard, Inter, Apple SD Gothic Neo, system-ui, sans-serif
    fontSize: 12px
    fontWeight: 500
    lineHeight: 16px
    letterSpacing: 0em
rounded:
  xs: 6px
  sm: 8px
  md: 12px
  lg: 16px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  nav-height: 60px
  panel-gap: 12px
  desktop-main-width: 74%
  desktop-side-width: 26%
components:
  app-shell:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.text-primary}"
    typography: "{typography.body-md}"
  top-navigation:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    height: 60px
  index-strip:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: 12px
  chart-panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: 16px
  chart-selected-value:
    textColor: "{colors.text-primary}"
    typography: "{typography.display-price}"
  market-row:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    typography: "{typography.table-value}"
    height: 56px
  market-row-selected:
    backgroundColor: "{colors.surface-selected}"
    textColor: "{colors.text-primary}"
    height: 56px
  filter-chip:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: 8px
  filter-chip-active:
    backgroundColor: "{colors.surface-selected}"
    textColor: "{colors.primary-strong}"
    rounded: "{rounded.md}"
    padding: 8px
  watchlist-panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: 16px
  orderbook-panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: 12px
  input-search:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    height: 40px
    padding: 12px
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 12px
  positive-number:
    textColor: "{colors.rise}"
    typography: "{typography.table-value}"
  negative-number:
    textColor: "{colors.fall}"
    typography: "{typography.table-value}"
  metadata-label:
    textColor: "{colors.text-muted}"
    typography: "{typography.label-sm}"
  hairline-divider:
    backgroundColor: "{colors.border}"
    height: 1px
  app-shell-dark:
    backgroundColor: "{colors.dark-background}"
    textColor: "{colors.dark-text-primary}"
    typography: "{typography.body-md}"
  top-navigation-dark:
    backgroundColor: "{colors.dark-surface}"
    textColor: "{colors.dark-text-primary}"
    height: 60px
  chart-panel-dark:
    backgroundColor: "{colors.dark-surface}"
    textColor: "{colors.dark-text-primary}"
    rounded: "{rounded.md}"
    padding: 16px
  elevated-panel-dark:
    backgroundColor: "{colors.dark-surface-elevated}"
    textColor: "{colors.dark-text-primary}"
    rounded: "{rounded.md}"
    padding: 16px
  input-search-dark:
    backgroundColor: "{colors.dark-surface-elevated}"
    textColor: "{colors.dark-text-primary}"
    rounded: "{rounded.md}"
    height: 40px
    padding: 12px
  filter-chip-active-dark:
    backgroundColor: "{colors.dark-surface-elevated}"
    textColor: "{colors.dark-primary}"
    rounded: "{rounded.md}"
    padding: 8px
  metadata-label-dark:
    textColor: "{colors.dark-text-muted}"
    typography: "{typography.label-sm}"
  hairline-divider-dark:
    backgroundColor: "{colors.dark-border}"
    height: 1px
  positive-number-dark:
    textColor: "{colors.dark-rise}"
    typography: "{typography.table-value}"
  negative-number-dark:
    textColor: "{colors.dark-fall}"
    typography: "{typography.table-value}"
---

# Design System: Market Visualization Web

## Overview

This product is a crypto market visualization web app for quickly scanning market movement and inspecting one selected coin with a simple candlestick chart. It is not a trading terminal, portfolio manager, or investment research product.

The layout uses an exchange-like information structure because the primary data source is Upbit-style market data. The visual treatment should feel more modern and calm: closer to Toss Securities or Linear in spacing, rounded controls, quiet surfaces, and reduced visual noise.

The atmosphere is **precise, calm, data-rich, and modern**. The screen should feel like a professional market monitor simplified for regular users: not as dense as a full exchange trading screen, and not as sparse as a generic SaaS dashboard.

### Product Direction

- **Structure:** exchange-grade market list, ticker data, candle chart, orderbook, and trades.
- **Surface:** modern fintech dashboard with light-first theme and dark-mode support.
- **Complexity:** enough detail for market scanning, but no professional TradingView toolbars, order entry forms, or portfolio/account features.

### Data Boundaries

Use these Upbit-style market data types as the default UI foundation:

- Market list and symbols.
- Ticker price, previous close, price change, change rate, 24h high/low, trade volume, and trade value.
- Candle OHLCV data for simple candlestick charts.
- Recent trades.
- Orderbook bid/ask prices, sizes, and total bid/ask sizes.
- Real-time updates through ticker, trade, orderbook, and candle streams where available.

The top index strip is allowed, but it is not provided by Upbit. Treat KOSPI, KOSDAQ, USD/KRW, NASDAQ, and S&P 500 as separate integrations. If no external index provider is connected, hide the strip or show a neutral empty state. Do not fabricate values.

Default exclusions: fear and greed index, AI news briefings, coin project fundamentals, analyst ratings, target prices, portfolio holdings, account balances, order submission, and social sentiment.

## Colors

The palette is a light-first fintech system built around a disciplined electric blue and Korean market movement colors.

- **Primary Electric Blue (`#006BFF`):** selected tabs, active filters, links, focus rings, and primary accent.
- **Porcelain App Background (`#FBFCFF`):** main page background, almost white with a cool financial tone.
- **Cool Panel Surface (`#FFFFFF`):** cards, table panels, chart containers, and the right rail.
- **Soft Market Canvas (`#F3F6FB`):** index strip, inactive controls, row hover, and quiet secondary surfaces.
- **Selection Blue Tint (`#EAF3FF`):** selected rows, active chip backgrounds, and chart selection states.
- **Ink Text (`#151B2D`):** primary headings, strong numbers, and table values.
- **Muted Text (`#7B8494`):** labels, timestamps, units, and secondary metadata.
- **Hairline Border (`#E3E8F0`):** dividers, table row lines, panel borders, and input strokes.
- **Rise Red (`#F04452`):** upward price movement in Korean market convention.
- **Fall Blue (`#1D6FFF`):** downward price movement in Korean market convention.

Dark mode reuses the same semantic roles with night surfaces: `#11131A` app background, `#171A23` panels, `#1E2230` elevated surfaces, `#2A3040` borders, `#F4F7FB` primary text, `#9AA3B2` muted text, and `#5EA2FF` interactive blue. Dark mode should be an alternate product mode, not a separate design language.

## Typography

Use a Korean-friendly modern sans-serif:

```css
font-family: Pretendard, "Inter", "Apple SD Gothic Neo", system-ui, sans-serif;
```

Typography should be calm and numeric-friendly.

- **Selected price:** 34-44px, 700 weight, tabular numbers.
- **Page title:** 22-28px, 700 weight.
- **Section heading:** 16-18px, 700 weight.
- **Table value:** 14-16px, 500-700 weight depending on importance.
- **Labels and units:** 12-13px, 500 weight.
- **Numeric data:** always use tabular numbers where possible.
- **Letter spacing:** neutral. Do not use decorative tracking.

## Layout

Use a four-zone desktop structure.

1. **Top Navigation**
   - Slim 56-64px height.
   - Product name or mark on the left.
   - Primary navigation: Market, Watchlist, Settings.
   - Center or right search input.
   - Theme toggle and refresh status.

2. **Index Strip**
   - Full-width row under navigation.
   - Shows external indicators such as KOSPI, KOSDAQ, USD/KRW, NASDAQ, and S&P 500.
   - Each item uses a small sparkline, current value, and change.
   - Keep this row compact. It should orient the user, not compete with the main chart.

3. **Main Market Area**
   - Two-column grid.
   - Left/main column takes roughly 70-76% of width.
   - Right panel takes roughly 24-30% of width.
   - Main column starts with selected coin header and a wide candlestick chart.
   - The chart should be horizontally long and visually dominant.

4. **Below-Chart Market Detail**
   - Under the chart, show orderbook and recent trades.
   - Orderbook uses bid/ask ladder with subtle depth bars.
   - Recent trades show time, side, price, and size.
   - Avoid order buttons or form controls.

The right panel is a persistent discovery panel. Its default state is watchlist and ranked markets. It should not repeat the selected coin chart summary already shown in the main panel. Rows include symbol, Korean/English name if available, current price, change rate, and favorite action.

On mobile, collapse into navigation, horizontal index strip, selected coin header, candlestick chart, watchlist/ranking tabs, then orderbook and trades as segmented tabs. Do not force desktop tables into mobile.

## Elevation & Depth

Depth is achieved through **tonal layers and hairline borders** rather than heavy shadows.

- The app background is a cool off-white.
- Primary content sits on white panels.
- Secondary regions use soft blue-gray surfaces.
- Sticky or floating surfaces may use very soft shadows, but default hierarchy should come from spacing, borders, and contrast.

Avoid heavy drop shadows, glassmorphism, neon glow, large decorative gradients, and nested rounded cards without a layout reason.

## Shapes

The shape language is softly modern but restrained.

- Panels: 12px radius.
- Inputs and chips: 10-12px radius.
- Icon buttons: 10px radius or circular when icon-only.
- Tables: flat rows with dividers, not card stacks.
- Segmented controls: 12px radius with clear active state.

Use one consistent radius system across light and dark modes.

## Components

### Navigation

The navigation is slim and tool-like. It uses a white or dark-panel surface, a hairline bottom border, a compact rounded search input, and icon-only controls for theme and refresh state.

### Index Strip

Index cards are compact scanner elements. They include value, change, and a tiny sparkline. They should not become large dashboard cards.

### Candlestick Chart Panel

The candlestick chart panel is the largest component on the screen. The header includes selected market, current price, change rate, 24h high/low, volume, and trade value. Controls are limited to timeframe tabs. Avoid drawing tools, indicator menus, screenshot buttons, and complex chart toolbar patterns.

### Orderbook

The orderbook sits below the chart. It uses ask and bid zones with tinted horizontal depth bars behind quantity or total fields. Rows are compact but readable. Do not include buy/sell order submission controls.

### Recent Trades

Recent trades sit next to the orderbook on desktop or behind a segmented tab on smaller widths. Show time, side, price, and size. Side color follows rise/fall colors.

### Market Table

Market table rows should feel closer to Toss Securities than an exchange terminal. Use 48-60px row height, soft active chips, subtle hover, selected states, and restrained columns: market, price, change, 24h trade value, and volume.

### Right Watchlist Panel

The right panel is reserved for discovery and favorites. It should include favorite icon, symbol, price, and change. The selected market may be highlighted with a blue tint. Do not repeat the full selected coin summary here.

### Chart Behavior

The chart is intentionally simple. Include candlestick OHLCV, volume bars, timeframe tabs, price axis, time axis, and hover crosshair if implemented. Exclude drawing tools, advanced indicators, multi-chart layout, strategy testing, trading order controls, and social overlays.

## Do's and Don'ts

- Do use Upbit-style market, ticker, candle, trade, and orderbook data as the implementation boundary.
- Do treat KOSPI, KOSDAQ, USD/KRW, NASDAQ, and S&P 500 as external integrations.
- Do make the selected coin chart the visual center of the screen.
- Do place orderbook and recent trades below the wide chart.
- Do keep the right panel focused on watchlist and market ranking.
- Do pair red/blue movement colors with plus/minus signs and labels.
- Do preserve the same layout, radius, typography, and hierarchy in dark mode.
- Don't copy Upbit or Toss brand assets, logos, icons, or exact page composition.
- Don't include fear and greed index, AI news, fundamentals, portfolio, account balance, or order submission without explicit data sources.
- Don't use a professional TradingView toolbar, drawing tools, or order forms.
- Don't duplicate selected coin summary information in the main chart header and right panel.
- Don't fabricate index values when an external index provider is missing.
- Don't rely on color alone to communicate price movement.

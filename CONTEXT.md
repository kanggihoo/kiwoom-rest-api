# Upbit Dashboard Context

This context defines the project language for the Upbit realtime monitoring dashboard MVP. The active application work is the Upbit dashboard; the Kiwoom REST API material in this repository remains documentation reference material.

## Language

### Market Data

**Quotation data**:
Public Upbit market data that does not require API key authentication.
_Avoid_: Exchange data, account data, private data

**Market**:
An Upbit trading pair such as `KRW-BTC`.
_Avoid_: Coin, ticker

**KRW Market**:
A **Market** whose quote currency is KRW.

**Selected Market**:
The **Market** currently shown in the dashboard detail area.
_Avoid_: Current coin, selected ticker

**Market List**:
Dashboard list of **Markets** with latest summary values.
_Avoid_: Watchlist, favorites

### Realtime Events

**Message envelope**:
Application message shape with `type`, `timestamp`, and `data`, used by REST responses and backend-to-frontend WebSocket events.
_Avoid_: Raw Upbit message

**Ticker event**:
Realtime current-price update for a **Market**.

**Trade event**:
Realtime execution update for a **Selected Market**.

**Orderbook event**:
Realtime bid/ask depth update for a **Selected Market**.

**Candle event**:
OHLCV update for a **Market** and candle unit.

**Candle Unit**:
Dashboard chart interval such as `1m`, `5m`, `1h`, `1d`, or `1w`.
_Avoid_: Upbit REST unit, Upbit WebSocket type

**Realtime Candle Unit**:
A **Candle Unit** that can be updated through a realtime **Candle event** in the MVP.
_Avoid_: Daily candle stream, weekly candle stream

**Alert event**:
Backend-generated market movement notification derived from **Quotation data**.
_Avoid_: Personal alert, user alert, notification setting

### Dashboard State

**MarketState**:
Backend-held runtime view of latest market data and active detail subscriptions.

**Snapshot**:
REST response containing the latest backend-held market state.

**Detail subscription**:
Subscription for selected-market **Trade events**, **Orderbook events**, and **Candle events** shared by clients watching the same **Selected Market**.

### Interface Boundary

**BFF**:
Browser-facing REST boundary that forwards dashboard REST requests to the backend API.
_Avoid_: Controller, API controller

**BFF Route Handler**:
Next.js Route Handler implementing a **BFF** REST endpoint.
_Avoid_: Controller

**Order form**:
Disabled dashboard UI surface that previews a future trading interaction.
_Avoid_: Trading form, order execution

## Relationships

- A **KRW Market** is a **Market** whose quote currency is KRW.
- The **Market List** shows many **Markets** using **Ticker events**.
- A **Selected Market** has **Trade events**, **Orderbook events**, and **Candle events**.
- REST responses and backend-to-frontend WebSocket events use a **Message envelope**.
- A **Detail subscription** can be shared by one or more clients watching the same **Selected Market**.
- A **Snapshot** is read from **MarketState**.
- A **Realtime Candle Unit** is a **Candle Unit**, but not every **Candle Unit** is realtime-updatable in the MVP.
- An **Alert event** is derived from **Quotation data**, not user-specific alert settings.
- A **BFF Route Handler** belongs to the REST path, not the realtime WebSocket path.
- The **Order form** appears in the MVP UI but does not create orders.

## Example Dialogue

> **Dev:** "When a user selects `KRW-BTC`, do we create one **Detail subscription** per client?"
> **Domain expert:** "No. A **Detail subscription** is shared by clients watching the same **Selected Market**."
>
> **Dev:** "Should the **Order form** submit an order during the MVP?"
> **Domain expert:** "No. The MVP uses **Quotation data** only; the **Order form** is disabled UI."

## Flagged Ambiguities

- "Controller" should not be used for Next.js REST endpoints in this project; use **BFF Route Handler**.
- "Order form" means disabled UI only in the MVP, not real or simulated order execution.
- "Alert" means an **Alert event**, not a user-configured personal alert.
- "Watchlist" should not be used for the full right-side market table; use **Market List**.
- "Snapshot" means the latest backend-held **MarketState**, not every REST response that returns a list.

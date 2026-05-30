# REST BFF and Direct WebSocket

## Status

Accepted

## Context

The Upbit dashboard needs both request/response data loading and realtime market updates. REST is used for initial data, snapshots, market lists, and candle history. WebSocket is used for high-frequency ticker, trade, orderbook, candle, and alert events. The Next.js app can simplify browser REST calls through same-origin Route Handlers, while the FastAPI backend owns the long-lived realtime gateway.

## Decision

Browser REST requests go through Next.js BFF Route Handlers, which call FastAPI REST endpoints using the internal FastAPI base URL. Browser WebSocket connections go directly to the FastAPI WebSocket endpoint.

Do not proxy the realtime WebSocket stream through Next.js for the MVP. FastAPI owns WebSocket origin allowlisting and realtime connection lifecycle. Next.js owns browser-facing REST BFF routes.

## Consequences

REST calls can use relative `/api/...` URLs from the browser and avoid direct FastAPI REST CORS concerns. WebSocket clients must know the FastAPI WebSocket URL and FastAPI must explicitly allow the frontend origin. The split keeps the realtime path simple and avoids making Next.js responsible for long-lived streaming connections.

# API Contract Envelope and Model Source

## Status

Accepted

## Context

The dashboard uses REST for request/response data and a direct FastAPI WebSocket for realtime updates. Both paths return application messages to the browser, but they have different transport semantics: REST has route and HTTP status information, while WebSocket events rely on message `type` for routing.

## Decision

Use a shared application **Message envelope** shape with `type`, `timestamp`, and `data` for REST responses and backend-to-frontend WebSocket events. Keep **Snapshot** terminology reserved for the latest backend-held **MarketState**; REST list responses use list-oriented message types such as `markets:list` and `candles:list`, while `GET /api/snapshot` uses `market-state:snapshot`.

Operational probe endpoints are not application messages. `/health` may return a plain, minimal status object because it is intended for local process checks, smoke checks, and future infrastructure health probes rather than browser data loading. Browser-facing dashboard REST responses such as `markets:list`, `market-state:snapshot`, and `candles:list` still use the shared **Message envelope**.

Use backend Pydantic models as the contract source for Phase 1. Python fields use `snake_case`; JSON and TypeScript fields use `camelCase` through explicit Pydantic `serialization_alias` fields and matching TypeScript types. Do not introduce OpenAPI-based TypeScript generation in Phase 1.

## Consequences

Frontend message handling can rely on the same envelope shape across REST and WebSocket paths. REST response `type` values must still respect domain language and must not call every list response a snapshot. TypeScript contract types are manually maintained in Phase 1, so tests must verify the Pydantic JSON output shape that the frontend types mirror.

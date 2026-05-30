# BFF Upstream Error Handling

## Status

Accepted

## Context

The Next.js app exposes REST BFF Route Handlers for browser requests, while FastAPI owns the backend REST API. The MVP already has a health BFF route, and planned routes such as `markets`, `snapshot`, and `candles` will all call the FastAPI upstream. If each Route Handler handles network failures, non-2xx responses, timeouts, and invalid upstream payloads independently, browser-facing error responses will drift as the BFF surface grows.

## Decision

Use a shared upstream client/error mapper for Next.js BFF Route Handlers that call FastAPI. Route Handlers should focus on request parsing, route-specific upstream calls, and successful response shaping. Common FastAPI upstream failure cases should be mapped in one place to consistent browser-facing HTTP status codes and JSON error bodies.

Do not repeat route-local `try`/`catch` blocks for ordinary FastAPI upstream failure handling unless the route has a genuinely route-specific recovery path or response contract.

## Consequences

BFF routes will have a small common dependency, but error responses will stay consistent across `health`, `markets`, `snapshot`, and `candles`. New BFF routes should use the shared helper instead of inventing their own network and upstream error handling.

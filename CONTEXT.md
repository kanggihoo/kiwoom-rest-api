# Context

## Project

This repository contains Kiwoom REST API documentation and an Upbit realtime monitoring dashboard MVP.

The active application work is the Upbit dashboard under `apps/`.

## Upbit Dashboard Goal

Build a local-first realtime monitoring dashboard for public Upbit market data. The MVP is for market observation, not trading execution.

## In Scope

- Public Upbit quotation data.
- KRW market monitoring.
- Realtime ticker, trade, orderbook, candle, and alert events.
- FastAPI backend process memory for MVP state.
- Next.js frontend dashboard UI.
- Next.js Route Handler as REST BFF.
- Direct browser connection to the FastAPI WebSocket endpoint.

## Out of Scope

- Upbit API key authentication.
- Actual orders.
- Login and user accounts.
- DB and Redis for the MVP.
- Deployment.
- Personalized watchlists or alert settings.

## Architecture Terms

- **Frontend**: the Next.js app in `apps/web`.
- **Backend**: the FastAPI app in `apps/backend`.
- **BFF**: Next.js Route Handlers that proxy browser REST calls to FastAPI.
- **MarketState**: backend in-memory state for latest market snapshots.
- **Snapshot**: REST response containing the latest backend-held market state.
- **Event envelope**: WebSocket message shape with a `type` and `data`.
- **Ticker event**: realtime current-price update.
- **Detail subscription**: selected-market stream for trade, orderbook, and candle data.
- **Alert event**: backend-generated market movement notification.

## Key Decisions

- Keep frontend and backend as separate apps under `apps/`.
- Do not put root `package.json`, root `pnpm-workspace.yaml`, or root Upbit `pyproject.toml` in the repository root.
- Use the root `Makefile` only as a local command entry point.
- Use `pnpm` for frontend dependencies.
- Use `uv` for backend dependencies and virtualenv management.
- Use backend process memory for MVP state.
- Use docs and Pydantic/OpenAPI contracts before adding shared packages.

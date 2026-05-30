# Process Memory for MVP State

## Status

Accepted

## Context

The MVP is a local-first realtime monitoring dashboard, not a persisted trading or portfolio system. It needs fast access to the latest ticker snapshot, selected-market subscriptions, recent price history for alerts, and recent alert events. Adding Redis or a database at this stage would add operational complexity before persistence or horizontal scaling requirements exist.

## Decision

Store MVP runtime state in the FastAPI backend process memory. This includes latest ticker snapshots, connected client state, detail subscriptions, short-term price history, and recent alert events.

Do not add Redis or a database for MVP state unless requirements change. Revisit this decision when the backend must run multiple instances, preserve state across restarts, share recent alerts between instances, cache candle REST responses, or use Pub/Sub or Streams for event fanout.

## Consequences

The MVP remains simple to run locally and avoids unnecessary infrastructure. State resets when the backend process restarts, and the backend is effectively single-instance for realtime state. Any later move to Redis or a database must introduce explicit state ownership and migration rules instead of assuming process memory semantics.

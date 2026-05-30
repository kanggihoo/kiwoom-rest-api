# Root Local Command Entrypoint

## Status

Accepted

## Context

The Upbit dashboard MVP has two independently runnable apps: the Next.js frontend in `apps/web` and the FastAPI backend in `apps/backend`. The frontend uses `pnpm`, while the backend uses `uv`, so making the repository root own application dependencies would blur the app boundary and make local setup less explicit.

## Decision

Use the repository root only as a local command entrypoint. Keep frontend dependency and workspace files under `apps/web`, keep backend dependency and virtualenv files under `apps/backend`, and use the root `Makefile` to forward common local commands such as `dev`, `dev-api`, `dev-web`, and health checks.

Do not add root-level `package.json`, root-level `pnpm-workspace.yaml`, or a root-level Upbit dashboard `pyproject.toml` unless this decision is revisited.

## Consequences

Developers can run common commands from the repository root through `make`, while each app remains responsible for its own dependency manager and runtime configuration. Cross-app shared code or generated contracts should be introduced deliberately instead of appearing implicitly through a root workspace.

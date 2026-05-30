.PHONY: dev dev-api dev-api-no-upbit dev-web health-api health-web test-api upbit-smoke lint-web build-web

BACKEND_HOST ?= 0.0.0.0
BACKEND_PORT ?= 8000
WEB_PORT ?= 3000
FASTAPI_BASE_URL ?= http://localhost:$(BACKEND_PORT)

dev:
	$(MAKE) -j2 dev-api dev-web

dev-api:
	uv run --directory apps/backend uvicorn upbit_dashboard.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

dev-api-no-upbit:
	UPBIT_WS_ENABLED=false uv run --directory apps/backend uvicorn upbit_dashboard.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

upbit-smoke:
	uv run --directory apps/backend python -m upbit_dashboard.tools.smoke_upbit_connection

dev-web:
	FASTAPI_BASE_URL=$(FASTAPI_BASE_URL) pnpm -C apps/web dev --port $(WEB_PORT)

health-api:
	curl -fsS http://localhost:$(BACKEND_PORT)/health

health-web:
	curl -fsS http://localhost:$(WEB_PORT)/api/health

test-api:
	uv run --directory apps/backend pytest

lint-web:
	pnpm -C apps/web lint

build-web:
	pnpm -C apps/web build

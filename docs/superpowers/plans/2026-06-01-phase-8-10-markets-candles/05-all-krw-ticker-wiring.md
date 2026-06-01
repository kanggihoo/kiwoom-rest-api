# 05 All KRW Ticker Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 8에 맞춰 backend ticker runner가 전체 KRW Market 목록을 사용할 수 있게 하되, 명시 설정값으로 기존 `KRW-BTC,KRW-ETH` 개발 모드를 유지할 수 있게 한다.

**Architecture:** 설정값 `UPBIT_TICKER_MARKETS_MODE`를 추가한다. 기본값은 Phase 8 목적에 맞게 `all_krw`로 두고, `configured` 모드에서는 기존 `UPBIT_TICKER_MARKETS`를 사용한다. 전체 KRW mode에서는 `MarketCatalogueService`가 반환한 Market 목록을 runner subscription 코드로 넘긴다.

**Tech Stack:** Python 3.12, FastAPI lifespan, Pydantic Settings, pytest, RTK.

---

**순서:** 05 / 07  
**이전 단계:** [04-validation-error-envelope.md](./04-validation-error-envelope.md)  
**다음 단계:** [06-next-bff-routes.md](./06-next-bff-routes.md)

### Task 01: ticker market mode settings 테스트 작성

**Files:**
- Modify: `apps/backend/tests/test_settings.py`
- Modify: `apps/backend/src/upbit_dashboard/settings.py`
- Modify: `apps/backend/tests/conftest.py`

- [ ] **Step 1: 실패하는 settings 테스트 추가**

`apps/backend/tests/test_settings.py`에 다음 테스트를 추가한다.

```python
def test_backend_settings_default_to_all_krw_ticker_mode() -> None:
    settings = BackendSettings(_env_file=None)

    assert settings.upbit_ticker_markets_mode == "all_krw"


def test_backend_settings_accept_configured_ticker_mode() -> None:
    settings = BackendSettings(
        UPBIT_TICKER_MARKETS_MODE="configured",
        UPBIT_TICKER_MARKETS="KRW-BTC,KRW-ETH",
        _env_file=None,
    )

    assert settings.upbit_ticker_markets_mode == "configured"
    assert settings.upbit_ticker_markets == ("KRW-BTC", "KRW-ETH")
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_settings.py -q
```

Expected:

```text
AttributeError: 'BackendSettings' object has no attribute 'upbit_ticker_markets_mode'
```

### Task 02: ticker market mode settings 구현

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/settings.py`
- Modify: `apps/backend/tests/conftest.py`

- [ ] **Step 1: settings 필드 추가**

`apps/backend/src/upbit_dashboard/settings.py`에 상수와 타입을 추가한다.

```python
from typing import Annotated, Literal

DEFAULT_TICKER_MARKETS_MODE = "all_krw"
TickerMarketsMode = Literal["all_krw", "configured"]
```

`BackendSettings`에 필드를 추가한다.

```python
upbit_ticker_markets_mode: TickerMarketsMode = Field(
    DEFAULT_TICKER_MARKETS_MODE,
    validation_alias="UPBIT_TICKER_MARKETS_MODE",
)
```

validator를 추가한다.

```python
@field_validator("upbit_ticker_markets_mode", mode="before")
@classmethod
def validate_upbit_ticker_markets_mode(cls, value: object) -> object:
    if isinstance(value, str) and value.strip() == "":
        return DEFAULT_TICKER_MARKETS_MODE
    return value
```

`apps/backend/tests/conftest.py`의 `SETTING_ENV_NAMES`에 추가한다.

```python
"UPBIT_TICKER_MARKETS_MODE",
```

- [ ] **Step 2: settings 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_settings.py -q
```

Expected:

```text
passed
```

### Task 03: lifespan 전체 KRW ticker wiring 테스트 작성

**Files:**
- Modify: `apps/backend/tests/test_lifespan.py`
- Modify: `apps/backend/src/upbit_dashboard/main.py`

- [ ] **Step 1: 실패하는 lifespan 테스트 추가**

`apps/backend/tests/test_lifespan.py`에 다음 테스트를 추가한다.

```python
import anyio

from upbit_dashboard.contracts.rest import MarketSummary
from upbit_dashboard.settings import get_settings


class FakeMarketCatalogueForTicker:
    async def list_krw_markets(self):
        return (
            MarketSummary(
                market="KRW-BTC",
                korean_name="비트코인",
                english_name="Bitcoin",
                quote_currency="KRW",
                base_currency="BTC",
            ),
            MarketSummary(
                market="KRW-ETH",
                korean_name="이더리움",
                english_name="Ethereum",
                quote_currency="KRW",
                base_currency="ETH",
            ),
        )


def test_resolve_ticker_markets_uses_all_krw_catalogue(monkeypatch) -> None:
    from upbit_dashboard.main import resolve_ticker_markets

    monkeypatch.setenv("UPBIT_TICKER_MARKETS_MODE", "all_krw")
    settings = get_settings()

    markets = anyio.run(resolve_ticker_markets, settings, FakeMarketCatalogueForTicker())

    assert markets == ("KRW-BTC", "KRW-ETH")


def test_resolve_ticker_markets_uses_configured_markets(monkeypatch) -> None:
    from upbit_dashboard.main import resolve_ticker_markets

    monkeypatch.setenv("UPBIT_TICKER_MARKETS_MODE", "configured")
    monkeypatch.setenv("UPBIT_TICKER_MARKETS", "KRW-XRP,KRW-ETH")
    settings = get_settings()

    markets = anyio.run(resolve_ticker_markets, settings, FakeMarketCatalogueForTicker())

    assert markets == ("KRW-XRP", "KRW-ETH")
```

- [ ] **Step 2: 기존 lifespan 테스트의 구독 mode 고정**

기존 `test_lifespan_starts_upbit_stream_by_default`, `test_lifespan_passes_settings_to_upbit_stream`, `test_lifespan_ticker_handler_updates_market_state_and_logs`에는 실제 Upbit Market 목록 조회가 일어나지 않도록 다음 env 설정을 추가한다.

```python
monkeypatch.setenv("UPBIT_TICKER_MARKETS_MODE", "configured")
```

`test_lifespan_passes_settings_to_upbit_stream`에는 이미 `UPBIT_TICKER_MARKETS`를 설정하므로 `configured` mode에서 기존 assertion을 유지한다.

- [ ] **Step 3: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_lifespan.py -q
```

Expected:

```text
ImportError: cannot import name 'resolve_ticker_markets'
```

### Task 04: ticker markets resolver 구현

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/main.py`

- [ ] **Step 1: resolver 추가**

`apps/backend/src/upbit_dashboard/main.py`에 helper를 추가한다.

```python
async def resolve_ticker_markets(settings, market_catalogue) -> tuple[str, ...]:
    if settings.upbit_ticker_markets_mode == "configured":
        return settings.upbit_ticker_markets
    markets = await market_catalogue.list_krw_markets()
    return tuple(market.market for market in markets)
```

- [ ] **Step 2: lifespan startup에서 resolver 사용**

lifespan에서 `run_ticker_stream(markets=settings.upbit_ticker_markets, ...)` 호출 전 markets를 계산한다.

```python
markets = await resolve_ticker_markets(settings, app.state.market_catalogue)
ticker_task = asyncio.create_task(
    run_ticker_stream(
        markets=markets,
        endpoint=settings.upbit_ws_endpoint,
        ticket=settings.upbit_ticket,
        on_ticker=on_ticker,
        initial_backoff=settings.initial_backoff_seconds,
        max_backoff=settings.max_backoff_seconds,
    )
)
```

- [ ] **Step 3: lifespan/settings 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_lifespan.py apps/backend/tests/test_settings.py -q
```

Expected:

```text
passed
```

- [ ] **Step 4: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/main.py apps/backend/src/upbit_dashboard/settings.py apps/backend/tests/conftest.py apps/backend/tests/test_lifespan.py apps/backend/tests/test_settings.py
rtk proxy git commit -m "feat: support all krw ticker subscriptions"
```

Expected:

```text
커밋 생성
```

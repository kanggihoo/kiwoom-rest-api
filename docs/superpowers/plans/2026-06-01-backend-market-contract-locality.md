# Backend Market Contract Locality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Concentrate Market normalization in the `market` Module, move Upbit raw message parsing out of browser-facing `contracts`, and document `/health` as a Message envelope exception.

**Architecture:** The `market` Module owns Market code normalization, comma-separated Market list parsing, and KRW Market validation. The `upbit` package owns Upbit raw WebSocket message models and mappers as Adapter implementation details, while `contracts` keeps frontend-facing Message envelope and quotation models. `/health` remains a plain operational probe, documented as outside the application Message envelope contract.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, pytest, RTK, ADR Markdown.

---

## Scope

Included:

- ADR-0006 documentation update for `/health` as an operational endpoint exception.
- Market normalization/list parsing/KRW validation ownership moved to `upbit_dashboard.market`.
- `settings` and `upbit.client` use the Market Module instead of local split/upper logic.
- Upbit raw ticker message and Upbit-to-app mapper moved from `contracts` to `upbit`.
- Tests updated so browser-facing contract tests import quotation names from `contracts.quotation`, not through `contracts.events`.

Excluded:

- Connecting `MarketState.upsert_ticker()` to the runtime ticker stream. That is Phase 3.
- Extracting an Upbit REST Market List Adapter from `tools.smoke_upbit_connection`. That review item is excluded.
- Adding `/api/snapshot`, `/api/markets`, backend-to-frontend WebSocket routes, or frontend changes.

## File Structure

- Modify `docs/adr/0006-api-contract-envelope-and-model-source.md`
  - Documents that operational endpoints such as `/health` are outside the application Message envelope.
- Modify `apps/backend/src/upbit_dashboard/market/catalogue.py`
  - Owns `MarketCode`, single Market normalization, Market list parsing, and KRW Market list validation.
- Modify `apps/backend/src/upbit_dashboard/settings.py`
  - Keeps env/default settings ownership, delegates `UPBIT_TICKER_MARKETS` parsing to `market.catalogue`.
- Modify `apps/backend/src/upbit_dashboard/upbit/client.py`
  - Owns Upbit WebSocket connection/subscription/payload flow, delegates Market validation and raw mapping.
- Create `apps/backend/src/upbit_dashboard/upbit/messages.py`
  - Owns Upbit raw WebSocket message Pydantic models.
- Create `apps/backend/src/upbit_dashboard/upbit/mappers.py`
  - Owns Upbit raw message to app quotation model mapping.
- Modify `apps/backend/src/upbit_dashboard/contracts/events.py`
  - Uses quotation models without re-exporting `StreamType`, `CandleUnit`, `AskBid`, etc. as the import surface.
- Delete `apps/backend/src/upbit_dashboard/contracts/upbit.py`
  - Raw Upbit input contract no longer belongs in browser-facing contracts.
- Delete `apps/backend/src/upbit_dashboard/contracts/mappers.py`
  - Upbit Adapter mapping no longer belongs in browser-facing contracts.
- Modify backend tests under `apps/backend/tests`
  - Test the new Market Module interface, updated settings/client behavior, and new Upbit Adapter module paths.

## Task 1: Document `/health` Message Envelope Exception

**Files:**

- Modify: `docs/adr/0006-api-contract-envelope-and-model-source.md`

- [ ] **Step 1: Update ADR-0006**

Add this paragraph after the first paragraph in the `Decision` section:

```markdown
Operational probe endpoints are not application messages. `/health` may return a plain, minimal status object because it is intended for local process checks, smoke checks, and future infrastructure health probes rather than browser data loading. Browser-facing dashboard REST responses such as `markets:list`, `market-state:snapshot`, and `candles:list` still use the shared **Message envelope**.
```

- [ ] **Step 2: Verify the ADR text is present**

Run:

```bash
rtk proxy rg -n "Operational probe endpoints|/health.*plain" docs/adr/0006-api-contract-envelope-and-model-source.md
```

Expected: output includes the new paragraph line.

- [ ] **Step 3: Commit**

```bash
git add docs/adr/0006-api-contract-envelope-and-model-source.md
git commit -m "docs: document health envelope exception"
```

## Task 2: Move Market List Parsing and KRW Validation into the Market Module

**Files:**

- Modify: `apps/backend/src/upbit_dashboard/market/catalogue.py`
- Modify: `apps/backend/src/upbit_dashboard/settings.py`
- Modify: `apps/backend/src/upbit_dashboard/upbit/client.py`
- Modify: `apps/backend/tests/test_market_catalogue.py`
- Modify: `apps/backend/tests/test_settings.py`
- Modify: `apps/backend/tests/test_upbit_settings.py`

- [ ] **Step 1: Write failing Market Module tests**

Append these tests to `apps/backend/tests/test_market_catalogue.py`:

```python
from upbit_dashboard.market.catalogue import (
    normalize_krw_market_codes,
    parse_market_code_list,
    parse_krw_market_code_list,
)


def test_parse_market_code_list_normalizes_comma_separated_values() -> None:
    assert parse_market_code_list(" krw-btc,KRW-XRP, ,krw-eth ", default=("KRW-BTC",)) == (
        "KRW-BTC",
        "KRW-XRP",
        "KRW-ETH",
    )


def test_parse_market_code_list_uses_default_for_blank_input() -> None:
    assert parse_market_code_list("  ", default=("KRW-BTC", "KRW-ETH")) == ("KRW-BTC", "KRW-ETH")


def test_normalize_krw_market_codes_rejects_empty_and_non_krw_markets() -> None:
    with pytest.raises(ValueError, match="At least one"):
        normalize_krw_market_codes([" ", ""])

    with pytest.raises(ValueError, match="KRW"):
        normalize_krw_market_codes(["USDT-BTC"])


def test_parse_krw_market_code_list_rejects_non_krw_markets() -> None:
    with pytest.raises(ValueError, match="KRW"):
        parse_krw_market_code_list("KRW-BTC,USDT-ETH", default=("KRW-BTC",))
```

If the file already imports `assert_krw_market`, `is_krw_market`, and `parse_market_code`, merge the new imported names into the existing import block instead of adding a second import block.

- [ ] **Step 2: Write failing settings validation test**

Modify `apps/backend/tests/test_settings.py` to import `ValidationError`:

```python
from pydantic import ValidationError
```

Append this test:

```python
def test_backend_settings_reject_non_krw_ticker_markets() -> None:
    with pytest.raises(ValidationError, match="KRW"):
        BackendSettings(
            UPBIT_TICKER_MARKETS="KRW-BTC,USDT-ETH",
            _env_file=None,
        )
```

- [ ] **Step 3: Write failing Upbit subscription tests**

Replace the contents of `apps/backend/tests/test_upbit_settings.py` with:

```python
import pytest

from upbit_dashboard.market.catalogue import normalize_krw_market_codes
from upbit_dashboard.upbit.client import build_ticker_subscription
from upbit_dashboard.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
)


def test_default_upbit_phase2_settings_are_fixed() -> None:
    assert DEFAULT_UPBIT_WS_ENDPOINT == "wss://api.upbit.com/websocket/v1"
    assert DEFAULT_TICKER_MARKETS == ("KRW-BTC", "KRW-ETH")
    assert DEFAULT_TICKET == "upbit-dashboard-phase2"


def test_normalize_krw_market_codes_trims_and_uppercases_codes() -> None:
    assert normalize_krw_market_codes([" krw-btc ", "krw-eth"]) == ("KRW-BTC", "KRW-ETH")


def test_build_ticker_subscription_uses_default_format_and_codes() -> None:
    message = build_ticker_subscription([" krw-btc ", "KRW-ETH"])

    assert message == [
        {"ticket": "upbit-dashboard-phase2"},
        {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
        {"format": "DEFAULT"},
    ]


def test_build_ticker_subscription_rejects_non_krw_markets() -> None:
    with pytest.raises(ValueError, match="KRW"):
        build_ticker_subscription(["USDT-BTC"])
```

- [ ] **Step 4: Run the focused failing tests**

Run:

```bash
cd apps/backend && rtk proxy uv run pytest tests/test_market_catalogue.py tests/test_settings.py::test_backend_settings_reject_non_krw_ticker_markets tests/test_upbit_settings.py -q
```

Expected: FAIL because `parse_market_code_list`, `parse_krw_market_code_list`, and `normalize_krw_market_codes` do not exist yet.

- [ ] **Step 5: Implement Market Module ownership**

Update `apps/backend/src/upbit_dashboard/market/catalogue.py` to include these imports and functions:

```python
from collections.abc import Iterable
```

```python
def normalize_market_codes(markets: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(
        parse_market_code(market).as_upbit_code()
        for market in markets
        if market.strip()
    )
    if not normalized:
        raise ValueError("At least one Upbit Market is required.")
    return normalized


def normalize_krw_market_codes(markets: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(
        assert_krw_market(market).as_upbit_code()
        for market in markets
        if market.strip()
    )
    if not normalized:
        raise ValueError("At least one KRW Market is required.")
    return normalized


def parse_market_code_list(
    raw_value: str | None,
    *,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    if raw_value is None or raw_value.strip() == "":
        return default
    return normalize_market_codes(raw_value.split(","))


def parse_krw_market_code_list(
    raw_value: str | None,
    *,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    if raw_value is None or raw_value.strip() == "":
        return default
    return normalize_krw_market_codes(raw_value.split(","))
```

- [ ] **Step 6: Delegate settings Market parsing**

In `apps/backend/src/upbit_dashboard/settings.py`, add this import:

```python
from upbit_dashboard.market.catalogue import parse_krw_market_code_list
```

Change `validate_upbit_ticker_markets` to:

```python
    @field_validator("upbit_ticker_markets", mode="before")
    @classmethod
    def validate_upbit_ticker_markets(cls, value: object) -> tuple[str, ...] | object:
        if not isinstance(value, str):
            return value
        return parse_krw_market_code_list(value, default=DEFAULT_TICKER_MARKETS)
```

Delete the old `parse_market_list()` function from `settings.py`.

- [ ] **Step 7: Delegate Upbit subscription Market validation**

In `apps/backend/src/upbit_dashboard/upbit/client.py`, add:

```python
from upbit_dashboard.market.catalogue import normalize_krw_market_codes
```

Delete the local `normalize_markets()` function.

Change `build_ticker_subscription()` to:

```python
def build_ticker_subscription(
    markets: Sequence[str] = DEFAULT_TICKER_MARKETS,
    ticket: str = DEFAULT_TICKET,
) -> list[dict[str, object]]:
    codes = list(normalize_krw_market_codes(markets))
    return [
        {"ticket": ticket},
        {"type": "ticker", "codes": codes},
        {"format": DEFAULT_WS_FORMAT},
    ]
```

- [ ] **Step 8: Run focused tests**

Run:

```bash
cd apps/backend && rtk proxy uv run pytest tests/test_market_catalogue.py tests/test_settings.py tests/test_upbit_settings.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add apps/backend/src/upbit_dashboard/market/catalogue.py apps/backend/src/upbit_dashboard/settings.py apps/backend/src/upbit_dashboard/upbit/client.py apps/backend/tests/test_market_catalogue.py apps/backend/tests/test_settings.py apps/backend/tests/test_upbit_settings.py
git commit -m "refactor: centralize market normalization"
```

## Task 3: Move Upbit Raw Message Models and Mappers into the Upbit Adapter

**Files:**

- Create: `apps/backend/src/upbit_dashboard/upbit/messages.py`
- Create: `apps/backend/src/upbit_dashboard/upbit/mappers.py`
- Modify: `apps/backend/src/upbit_dashboard/upbit/client.py`
- Modify: `apps/backend/tests/test_upbit_ticker_mapper.py`
- Modify: `apps/backend/tests/test_upbit_client.py`
- Delete: `apps/backend/src/upbit_dashboard/contracts/upbit.py`
- Delete: `apps/backend/src/upbit_dashboard/contracts/mappers.py`

- [ ] **Step 1: Update mapper tests to target the Upbit Adapter Module**

In `apps/backend/tests/test_upbit_ticker_mapper.py`, change the imports to:

```python
from pydantic import ValidationError
import pytest

from upbit_dashboard.contracts.quotation import StreamType
from upbit_dashboard.upbit.mappers import map_upbit_ticker_message
from upbit_dashboard.upbit.messages import UpbitTickerMessage
```

- [ ] **Step 2: Run the focused failing mapper tests**

Run:

```bash
cd apps/backend && rtk proxy uv run pytest tests/test_upbit_ticker_mapper.py -q
```

Expected: FAIL because `upbit_dashboard.upbit.mappers` and `upbit_dashboard.upbit.messages` do not exist yet.

- [ ] **Step 3: Create Upbit raw message Module**

Create `apps/backend/src/upbit_dashboard/upbit/messages.py`:

```python
"""Upbit WebSocket raw message models.

These models validate external Upbit input before adapter code maps it into
browser-facing application quotation contracts.
"""

from typing import Literal

from pydantic import BaseModel, Field


class UpbitTickerMessage(BaseModel):
    # Minimal required schema for one Upbit ticker WebSocket event.
    type: Literal["ticker"] = Field(description="Upbit WebSocket data type. ticker.")
    code: str = Field(description="Upbit Market code. Example: KRW-BTC.")
    opening_price: float = Field(description="Opening price. Upbit ticker.opening_price.")
    high_price: float = Field(description="High price. Upbit ticker.high_price.")
    low_price: float = Field(description="Low price. Upbit ticker.low_price.")
    trade_price: float = Field(description="Current trade price. Upbit ticker.trade_price.")
    signed_change_price: float = Field(description="Signed daily change price. Upbit ticker.signed_change_price.")
    signed_change_rate: float = Field(description="Signed daily change rate. Upbit ticker.signed_change_rate.")
    trade_volume: float = Field(description="Latest trade volume. Upbit ticker.trade_volume.")
    acc_trade_volume_24h: float = Field(description="24h accumulated trade volume. Upbit ticker.acc_trade_volume_24h.")
    acc_trade_price_24h: float = Field(description="24h accumulated trade price. Upbit ticker.acc_trade_price_24h.")
    trade_timestamp: int = Field(description="Trade timestamp in milliseconds. Upbit ticker.trade_timestamp.")
    timestamp: int = Field(description="Event timestamp in milliseconds. Upbit ticker.timestamp.")
    stream_type: Literal["SNAPSHOT", "REALTIME"] = Field(description="Upbit stream_type.")
```

- [ ] **Step 4: Create Upbit mapper Module**

Create `apps/backend/src/upbit_dashboard/upbit/mappers.py`:

```python
"""Mapping rules from Upbit raw messages to application quotation contracts."""

from upbit_dashboard.contracts.quotation import StreamType, TickerData
from upbit_dashboard.upbit.messages import UpbitTickerMessage


def map_upbit_ticker_message(message: UpbitTickerMessage) -> TickerData:
    return TickerData(
        market=message.code,
        opening_price=message.opening_price,
        high_price=message.high_price,
        low_price=message.low_price,
        trade_price=message.trade_price,
        signed_change_price=message.signed_change_price,
        signed_change_rate=message.signed_change_rate,
        trade_volume=message.trade_volume,
        acc_trade_volume_24h=message.acc_trade_volume_24h,
        acc_trade_price_24h=message.acc_trade_price_24h,
        trade_timestamp_ms=message.trade_timestamp,
        timestamp_ms=message.timestamp,
        stream_type=StreamType(message.stream_type),
    )
```

- [ ] **Step 5: Update Upbit client imports**

In `apps/backend/src/upbit_dashboard/upbit/client.py`, replace:

```python
from upbit_dashboard.contracts.mappers import map_upbit_ticker_message
from upbit_dashboard.contracts.upbit import UpbitTickerMessage
```

with:

```python
from upbit_dashboard.upbit.mappers import map_upbit_ticker_message
from upbit_dashboard.upbit.messages import UpbitTickerMessage
```

- [ ] **Step 6: Delete old contracts Modules**

Delete:

```text
apps/backend/src/upbit_dashboard/contracts/upbit.py
apps/backend/src/upbit_dashboard/contracts/mappers.py
```

- [ ] **Step 7: Run focused Upbit tests**

Run:

```bash
cd apps/backend && rtk proxy uv run pytest tests/test_upbit_ticker_mapper.py tests/test_upbit_client.py -q
```

Expected: PASS.

- [ ] **Step 8: Verify old imports are gone**

Run:

```bash
rtk proxy rg -n "contracts\\.mappers|contracts\\.upbit" apps/backend/src apps/backend/tests
```

Expected: no output.

- [ ] **Step 9: Commit**

```bash
git add apps/backend/src/upbit_dashboard/upbit/messages.py apps/backend/src/upbit_dashboard/upbit/mappers.py apps/backend/src/upbit_dashboard/upbit/client.py apps/backend/tests/test_upbit_ticker_mapper.py apps/backend/tests/test_upbit_client.py
git rm apps/backend/src/upbit_dashboard/contracts/upbit.py apps/backend/src/upbit_dashboard/contracts/mappers.py
git commit -m "refactor: move upbit raw mapping into adapter"
```

## Task 4: Stop Using Events Module as Quotation Re-Export Surface

**Files:**

- Modify: `apps/backend/src/upbit_dashboard/contracts/events.py`
- Modify: `apps/backend/tests/test_contract_serialization.py`
- Modify: `apps/backend/tests/test_upbit_ticker_mapper.py`

- [ ] **Step 1: Update contract serialization imports**

In `apps/backend/tests/test_contract_serialization.py`, use this import shape:

```python
from upbit_dashboard.contracts.events import (
    AlertData,
    AlertKind,
    CandleUpdateData,
    CandleUpdateEvent,
    RealtimeCandleUnit,
    Severity,
    TickerUpdateEvent,
    TradeUpdateEvent,
)
from upbit_dashboard.contracts.quotation import (
    AskBid,
    Candle,
    CandleUnit,
    StreamType,
    TickerData,
    TradeData,
)
```

Keep the existing `contracts.rest` imports unchanged.

- [ ] **Step 2: Add a test that events does not expose quotation names**

Append this test to `apps/backend/tests/test_contract_serialization.py`:

```python
def test_events_module_does_not_reexport_quotation_models() -> None:
    import upbit_dashboard.contracts.events as events

    assert not hasattr(events, "StreamType")
    assert not hasattr(events, "CandleUnit")
    assert not hasattr(events, "AskBid")
```

- [ ] **Step 3: Run the focused failing contract test**

Run:

```bash
cd apps/backend && rtk proxy uv run pytest tests/test_contract_serialization.py::test_events_module_does_not_reexport_quotation_models -q
```

Expected: FAIL because `events.py` currently imports those names into its module namespace.

- [ ] **Step 4: Refactor events.py to import quotation as a Module**

Change `apps/backend/src/upbit_dashboard/contracts/events.py` imports from:

```python
from upbit_dashboard.contracts.quotation import (
    AskBid,
    Candle,
    OrderbookData,
    CandleUnit,
    StreamType,
    TickerData,
    TradeData,
)
```

to:

```python
from upbit_dashboard.contracts import quotation
```

Then update type annotations in the same file:

```python
class CandleUpdateData(BaseModel):
    # 실시간 캔들 업데이트 payload
    market: str = Field(description="Market 코드.")
    candle_unit: RealtimeCandleUnit = Field(
        serialization_alias="candleUnit", description="실시간 candle 단위. 1m, 5m, 15m, 30m, 1h만 허용."
    )
    candle: quotation.Candle = Field(description="OHLCV candle 값.")
    timestamp_ms: int = Field(
        serialization_alias="timestampMs", description="Upbit candle WebSocket timestamp."
    )
    stream_type: quotation.StreamType = Field(
        serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME."
    )
```

```python
class TickerUpdateEvent(BaseModel):
    # 내부 상태의 ticker 갱신 이벤트
    type: Literal["ticker:update"] = Field(default="ticker:update", description="Ticker update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: quotation.TickerData = Field(description="Ticker update payload.")
```

```python
class TradeUpdateEvent(BaseModel):
    # 실시간 체결 업데이트 이벤트
    type: Literal["trade:update"] = Field(default="trade:update", description="Trade update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: quotation.TradeData = Field(description="Trade update payload.")
```

```python
class OrderbookUpdateEvent(BaseModel):
    # 실시간 호가 업데이트 이벤트
    type: Literal["orderbook:update"] = Field(default="orderbook:update", description="Orderbook update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: quotation.OrderbookData = Field(description="Orderbook update payload.")
```

- [ ] **Step 5: Run focused contract tests**

Run:

```bash
cd apps/backend && rtk proxy uv run pytest tests/test_contract_serialization.py tests/test_upbit_ticker_mapper.py -q
```

Expected: PASS.

- [ ] **Step 6: Verify tests no longer import quotation names from events**

Run:

```bash
rtk proxy rg -n "from upbit_dashboard\\.contracts\\.events import \\([^)]*(AskBid|Candle|CandleUnit|StreamType|TickerData|TradeData)" apps/backend/tests
```

Expected: no output.

- [ ] **Step 7: Commit**

```bash
git add apps/backend/src/upbit_dashboard/contracts/events.py apps/backend/tests/test_contract_serialization.py apps/backend/tests/test_upbit_ticker_mapper.py
git commit -m "refactor: separate event and quotation contract imports"
```

## Task 5: Full Verification

**Files:**

- Verify all backend source, tests, and ADR changes from Tasks 1-4.

- [ ] **Step 1: Run backend test suite**

Run:

```bash
cd apps/backend && rtk proxy uv run pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 2: Check old Upbit raw contract imports**

Run:

```bash
rtk proxy rg -n "contracts\\.mappers|contracts\\.upbit|from upbit_dashboard\\.upbit\\.client import .*normalize_markets|def parse_market_list" apps/backend/src apps/backend/tests
```

Expected: no output.

- [ ] **Step 3: Check whitespace**

Run:

```bash
rtk git diff --check
```

Expected: no whitespace errors.

- [ ] **Step 4: Review diff**

Run:

```bash
rtk git diff --stat
rtk git diff -- docs/adr/0006-api-contract-envelope-and-model-source.md apps/backend/src/upbit_dashboard apps/backend/tests
```

Expected:

- ADR-0006 only documents the `/health` exception.
- `market.catalogue` owns Market list parsing and KRW validation.
- `settings.py` does not define `parse_market_list`.
- `upbit.client` does not define `normalize_markets`.
- Upbit raw message/mapping files live under `upbit`.
- `contracts/upbit.py` and `contracts/mappers.py` are deleted.
- `contracts/events.py` no longer exposes quotation names as the caller import path.

- [ ] **Step 5: Final commit if prior tasks were not committed separately**

If Tasks 1-4 were not committed individually, commit the complete change:

```bash
git add docs/adr/0006-api-contract-envelope-and-model-source.md apps/backend/src/upbit_dashboard apps/backend/tests
git rm apps/backend/src/upbit_dashboard/contracts/upbit.py apps/backend/src/upbit_dashboard/contracts/mappers.py
git commit -m "refactor: improve backend contract locality"
```

## Self-Review

Spec coverage:

- `/health` Message envelope exception is covered by Task 1.
- Market normalization, list parsing, and KRW validation are covered by Task 2.
- Upbit raw message and mapper ownership are covered by Task 3.
- `contracts.events` import confusion is covered by Task 4.
- Phase 3 `MarketState` runtime wiring is explicitly excluded.
- Smoke REST Market Adapter extraction is explicitly excluded.

Placeholder scan:

- Placeholder scan passed; every code or verification step has concrete content.

Type consistency:

- Market list functions return `tuple[str, ...]`.
- `build_ticker_subscription()` continues to accept `Sequence[str]` and return `list[dict[str, object]]`.
- `UpbitTickerMessage` and `map_upbit_ticker_message()` names are preserved, but their Module path changes from `contracts` to `upbit`.

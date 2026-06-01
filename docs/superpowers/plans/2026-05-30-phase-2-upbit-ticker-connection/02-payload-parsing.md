# 02 Payload Parsing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upbit WebSocket payload를 안전하게 파싱하고, ticker payload를 Phase 1 `TickerData`로 변환한다.

**Architecture:** `client.py`에 payload decoding, Upbit error payload 분리, `UpbitTickerMessage` validation, mapper 호출을 추가한다. WebSocket 연결 loop는 아직 만들지 않고, bytes/str payload를 순수 함수로 처리해 네트워크 없는 테스트를 유지한다.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, RTK.

---

**순서:** 02 / 06
**이전 단계:** [01-settings-and-subscription.md](./01-settings-and-subscription.md)
**다음 단계:** [03-stream-runner.md](./03-stream-runner.md)

### Task 02: WebSocket payload 파싱과 ticker 변환

**Files:**
- Modify: `apps/backend/src/upbit_dashboard/upbit/client.py`
- Create: `apps/backend/tests/test_upbit_client.py`

- [ ] **Step 1: 실패하는 payload 파싱 테스트 작성**

`apps/backend/tests/test_upbit_client.py`를 만든다.

```python
import json

from pydantic import ValidationError
import pytest

from upbit_dashboard.contracts.quotation import StreamType
from upbit_dashboard.upbit.client import UpbitWebSocketError, parse_ticker_payload


def _ticker_payload() -> dict[str, object]:
    return {
        "type": "ticker",
        "code": "KRW-BTC",
        "opening_price": 108000000,
        "high_price": 109000000,
        "low_price": 107500000,
        "trade_price": 108359000,
        "signed_change_price": -106000,
        "signed_change_rate": -0.001,
        "trade_volume": 0.01,
        "acc_trade_volume_24h": 1288.5,
        "acc_trade_price_24h": 139663338391,
        "trade_timestamp": 1760000000000,
        "timestamp": 1760000000100,
        "stream_type": "REALTIME",
    }


def test_parse_ticker_payload_converts_bytes_to_ticker_data() -> None:
    payload = json.dumps(_ticker_payload()).encode("utf-8")

    ticker = parse_ticker_payload(payload)

    assert ticker.market == "KRW-BTC"
    assert ticker.trade_price == 108359000
    assert ticker.trade_timestamp_ms == 1760000000000
    assert ticker.stream_type is StreamType.REALTIME


def test_parse_ticker_payload_serializes_with_frontend_aliases() -> None:
    ticker = parse_ticker_payload(json.dumps(_ticker_payload()))

    dumped = ticker.model_dump(mode="json", by_alias=True)

    assert dumped["market"] == "KRW-BTC"
    assert dumped["tradePrice"] == 108359000
    assert dumped["streamType"] == "REALTIME"
    assert "trade_price" not in dumped


def test_parse_ticker_payload_rejects_upbit_error_payload() -> None:
    payload = {
        "error": {
            "name": "NO_CODES",
            "message": "codes field is required",
        }
    }

    with pytest.raises(UpbitWebSocketError) as exc_info:
        parse_ticker_payload(json.dumps(payload))

    assert exc_info.value.name == "NO_CODES"
    assert "codes field is required" in str(exc_info.value)


def test_parse_ticker_payload_rejects_non_object_json() -> None:
    with pytest.raises(ValueError, match="JSON object"):
        parse_ticker_payload("[1, 2, 3]")


def test_parse_ticker_payload_rejects_invalid_ticker_shape() -> None:
    payload = _ticker_payload()
    payload.pop("trade_price")

    with pytest.raises(ValidationError):
        parse_ticker_payload(json.dumps(payload))
```

- [ ] **Step 2: 테스트 실패 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_client.py -q
```

Expected:

```text
ImportError: cannot import name 'UpbitWebSocketError'
```

- [ ] **Step 3: payload 파싱 구현**

`apps/backend/src/upbit_dashboard/upbit/client.py`를 다음 내용으로 교체한다.

```python
from collections.abc import Sequence
import json
from typing import Any

from upbit_dashboard.contracts.mappers import map_upbit_ticker_message
from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.contracts.upbit import UpbitTickerMessage
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_WS_FORMAT,
)


class UpbitWebSocketError(RuntimeError):
    def __init__(self, name: str, message: str) -> None:
        self.name = name
        self.message = message
        super().__init__(f"{name}: {message}")


def normalize_markets(markets: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(market.strip().upper() for market in markets if market.strip())
    if not normalized:
        raise ValueError("At least one Upbit Market is required.")
    return normalized


def build_ticker_subscription(
    markets: Sequence[str] = DEFAULT_TICKER_MARKETS,
    ticket: str = DEFAULT_TICKET,
) -> list[dict[str, object]]:
    codes = list(normalize_markets(markets))
    return [
        {"ticket": ticket},
        {"type": "ticker", "codes": codes},
        {"format": DEFAULT_WS_FORMAT},
    ]


def decode_json_object(payload: bytes | str) -> dict[str, Any]:
    text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    decoded = json.loads(text)
    if not isinstance(decoded, dict):
        raise ValueError("Upbit WebSocket payload must be a JSON object.")
    return decoded


def raise_for_upbit_error(message: dict[str, Any]) -> None:
    error = message.get("error")
    if error is None:
        return
    if not isinstance(error, dict):
        raise UpbitWebSocketError("UNKNOWN", "Malformed Upbit WebSocket error payload.")
    name = error.get("name")
    detail = error.get("message")
    raise UpbitWebSocketError(
        name if isinstance(name, str) else "UNKNOWN",
        detail if isinstance(detail, str) else "Unknown Upbit WebSocket error.",
    )


def parse_ticker_payload(payload: bytes | str) -> TickerData:
    message = decode_json_object(payload)
    raise_for_upbit_error(message)
    return map_upbit_ticker_message(UpbitTickerMessage.model_validate(message))
```

- [ ] **Step 4: 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_upbit_client.py apps/backend/tests/test_upbit_settings.py -q
```

Expected:

```text
10 passed
```

- [ ] **Step 5: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/src/upbit_dashboard/upbit/client.py apps/backend/tests/test_upbit_client.py
rtk proxy git commit -m "feat: parse upbit ticker websocket payloads"
```

Expected:

```text
커밋 생성
```

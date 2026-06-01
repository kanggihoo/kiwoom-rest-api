# 03 Market State Semantics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 3 snapshot route와 ticker wiring이 의존하는 `MarketState`의 same-Market replacement와 explicit `generated_at` 동작을 테스트로 고정한다.

**Architecture:** `MarketState` 구현은 이미 존재하므로 production code를 변경하지 않는다. 테스트 helper만 configurable하게 바꾸고, 같은 Market ticker upsert가 기존 값을 교체하는지와 `snapshot(generated_at=...)`이 명시 시각을 사용하는지 검증한다.

**Tech Stack:** Python 3.12, pytest, Pydantic contract models, RTK.

---

**순서:** 03 / 04
**이전 단계:** [02-ticker-state-wiring.md](./02-ticker-state-wiring.md)
**다음 단계:** [04-verification.md](./04-verification.md)

### Task 03: MarketState semantics 테스트 보강

**Files:**
- Modify: `apps/backend/tests/test_market_state.py`

- [ ] **Step 1: ticker test helper를 configurable하게 수정**

`apps/backend/tests/test_market_state.py`의 `_ticker()`를 다음처럼 수정한다.

```python
def _ticker(market: str, trade_price: float = 1.5) -> TickerData:
    return TickerData(
        market=market,
        opening_price=1.0,
        high_price=2.0,
        low_price=0.5,
        trade_price=trade_price,
        signed_change_price=0.1,
        signed_change_rate=0.01,
        trade_volume=1.0,
        acc_trade_volume_24h=2.0,
        acc_trade_price_24h=3.0,
        trade_timestamp_ms=1,
        timestamp_ms=2,
        stream_type=StreamType.REALTIME,
    )
```

- [ ] **Step 2: replacement와 explicit generated_at 테스트 추가**

`apps/backend/tests/test_market_state.py`에 다음 테스트를 추가한다.

```python
def test_market_state_upsert_replaces_existing_market_ticker() -> None:
    state = MarketState()

    state.upsert_ticker(_ticker("KRW-BTC", trade_price=1.5))
    state.upsert_ticker(_ticker("KRW-BTC", trade_price=2.5))

    stored_ticker = state.get_ticker("KRW-BTC")
    assert stored_ticker is not None
    assert stored_ticker.trade_price == 2.5
    assert len(state.snapshot().tickers) == 1


def test_market_state_snapshot_uses_explicit_generated_at() -> None:
    state = MarketState()
    generated_at = datetime(2026, 6, 1, 3, 0, tzinfo=timezone.utc)

    state.upsert_ticker(_ticker("KRW-BTC"))

    assert state.snapshot(generated_at=generated_at).generated_at == generated_at
```

- [ ] **Step 3: MarketState 테스트 통과 확인**

Run:

```bash
rtk test uv run --directory apps/backend pytest apps/backend/tests/test_market_state.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 4: 단계 커밋**

Run:

```bash
rtk proxy git add apps/backend/tests/test_market_state.py
rtk proxy git commit -m "test: lock market state snapshot semantics"
```

Expected:

```text
커밋 생성
```

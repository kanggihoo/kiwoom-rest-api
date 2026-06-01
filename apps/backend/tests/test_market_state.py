from datetime import datetime, timezone

from upbit_dashboard.contracts.quotation import StreamType, TickerData
from upbit_dashboard.state.market_state import MarketState


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


def test_market_state_snapshot_tracks_latest_ticker_values() -> None:
    state = MarketState()
    assert state.updated_at is None

    state.upsert_ticker(_ticker("KRW-BTC"))
    state.upsert_ticker(_ticker("KRW-ETH"))

    snapshot = state.snapshot()
    assert snapshot.generated_at.tzinfo == timezone.utc
    assert len(snapshot.tickers) == 2
    assert {ticker.market for ticker in snapshot.tickers} == {"KRW-BTC", "KRW-ETH"}

    state.remove_ticker("krw-btc")
    assert state.get_ticker("KRW-BTC") is None
    assert state.snapshot().tickers[0].market in {"KRW-ETH"}


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

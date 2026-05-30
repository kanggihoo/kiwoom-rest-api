from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock

from upbit_dashboard.contracts.quotation import TickerData


@dataclass(frozen=True)
class MarketStateSnapshot:
    generated_at: datetime
    tickers: tuple[TickerData, ...]


class MarketState:
    def __init__(self) -> None:
        self._tickers: dict[str, TickerData] = {}
        self._updated_at: datetime | None = None
        self._lock = RLock()

    @property
    def updated_at(self) -> datetime | None:
        return self._updated_at

    def upsert_ticker(self, ticker: TickerData) -> None:
        with self._lock:
            self._tickers[ticker.market] = ticker
            self._updated_at = datetime.now(timezone.utc)

    def remove_ticker(self, market: str) -> None:
        normalized = market.strip().upper()
        with self._lock:
            self._tickers.pop(normalized, None)
            if not self._tickers:
                self._updated_at = None

    def get_ticker(self, market: str) -> TickerData | None:
        normalized = market.strip().upper()
        with self._lock:
            return self._tickers.get(normalized)

    def iter_tickers(self) -> Iterable[TickerData]:
        with self._lock:
            return tuple(self._tickers.values())

    def snapshot(self, generated_at: datetime | None = None) -> MarketStateSnapshot:
        with self._lock:
            return MarketStateSnapshot(
                generated_at=generated_at or self._updated_at or datetime.now(timezone.utc),
                tickers=tuple(self._tickers.values()),
            )

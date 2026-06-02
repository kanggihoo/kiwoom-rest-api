from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from upbit_dashboard.api.errors import DashboardApiError
from upbit_dashboard.contracts.errors import RestErrorCode
from upbit_dashboard.contracts.quotation import Candle, CandleUnit
from upbit_dashboard.contracts.rest import (
    CandlesListData,
    MarketStateSnapshotData,
    MarketsListData,
    MarketSummary,
)
from upbit_dashboard.market.catalogue import assert_krw_market
from upbit_dashboard.state.market_state import MarketState
from upbit_dashboard.upbit.rest import UpbitCandleResponse


class MarketCatalogue(Protocol):
    async def list_krw_markets(self) -> Sequence[MarketSummary]:
        ...


class CandleRestClient(Protocol):
    async def list_candles(
        self,
        *,
        unit: CandleUnit,
        market: str,
        count: int,
        to: str | None,
    ) -> Sequence[UpbitCandleResponse]:
        ...


def _map_upbit_candle(raw: UpbitCandleResponse) -> Candle:
    return Candle(
        candle_date_time_utc=raw.candle_date_time_utc,
        candle_date_time_kst=raw.candle_date_time_kst,
        opening_price=raw.opening_price,
        high_price=raw.high_price,
        low_price=raw.low_price,
        trade_price=raw.trade_price,
        candle_acc_trade_volume=raw.candle_acc_trade_volume,
        candle_acc_trade_price=raw.candle_acc_trade_price,
    )


def _normalize_candle_market(raw_market: str) -> str:
    try:
        return assert_krw_market(raw_market).as_upbit_code()
    except ValueError as exc:
        raise DashboardApiError(
            code=RestErrorCode.BAD_REQUEST,
            message=str(exc),
            details={"market": raw_market},
            status_code=400,
        ) from exc


class QuotationReadService:
    def __init__(
        self,
        *,
        market_catalogue: MarketCatalogue,
        upbit_rest_client: CandleRestClient,
        market_state: MarketState,
    ) -> None:
        self._market_catalogue = market_catalogue
        self._upbit_rest_client = upbit_rest_client
        self._market_state = market_state

    async def list_markets(self) -> MarketsListData:
        markets = await self._market_catalogue.list_krw_markets()
        return MarketsListData(markets=list(markets))

    async def list_candles(
        self,
        *,
        market: str,
        unit: CandleUnit,
        count: int,
        to: str | None,
    ) -> CandlesListData:
        normalized_market = _normalize_candle_market(market)
        raw_candles = await self._upbit_rest_client.list_candles(
            unit=unit,
            market=normalized_market,
            count=count,
            to=to,
        )
        candles = sorted(
            (_map_upbit_candle(raw_candle) for raw_candle in raw_candles),
            key=lambda candle: candle.candle_date_time_utc,
        )
        return CandlesListData(
            market=normalized_market,
            candle_unit=unit,
            candles=candles,
        )

    def get_snapshot(self, generated_at: datetime | None = None) -> MarketStateSnapshotData:
        snapshot = self._market_state.snapshot(generated_at=generated_at)
        return MarketStateSnapshotData(
            generated_at=snapshot.generated_at,
            tickers=list(snapshot.tickers),
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import BaseModel, Field, TypeAdapter

from upbit_dashboard.contracts.quotation import CandleUnit


class UpbitMarketResponse(BaseModel):
    market: str = Field(description="Upbit Market code.")
    korean_name: str = Field(description="Korean Market name.")
    english_name: str = Field(description="English Market name.")


class UpbitCandleResponse(BaseModel):
    market: str = Field(description="Upbit Market code.")
    candle_date_time_utc: str = Field(description="Candle UTC timestamp.")
    candle_date_time_kst: str = Field(description="Candle KST timestamp.")
    opening_price: float = Field(description="Opening price.")
    high_price: float = Field(description="High price.")
    low_price: float = Field(description="Low price.")
    trade_price: float = Field(description="Trade price.")
    candle_acc_trade_volume: float = Field(description="Accumulated trade volume.")
    candle_acc_trade_price: float = Field(description="Accumulated trade value.")


@dataclass
class UpbitRestError(Exception):
    status_code: int | None
    message: str
    error_name: str | None = None
    remaining_req: str | None = None


MARKET_LIST_PATH = "/v1/market/all"

_MARKET_LIST_ADAPTER = TypeAdapter(list[UpbitMarketResponse])
_CANDLE_LIST_ADAPTER = TypeAdapter(list[UpbitCandleResponse])


_CANDLE_PATHS = {
    CandleUnit.ONE_MINUTE: "/v1/candles/minutes/1",
    CandleUnit.FIVE_MINUTES: "/v1/candles/minutes/5",
    CandleUnit.FIFTEEN_MINUTES: "/v1/candles/minutes/15",
    CandleUnit.THIRTY_MINUTES: "/v1/candles/minutes/30",
    CandleUnit.ONE_HOUR: "/v1/candles/minutes/60",
    CandleUnit.ONE_DAY: "/v1/candles/days",
    CandleUnit.ONE_WEEK: "/v1/candles/weeks",
}


def _build_candle_path(unit: CandleUnit) -> str:
    return _CANDLE_PATHS[unit]


class UpbitRestClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def list_markets(self) -> list[UpbitMarketResponse]:
        response = await self._request("GET", MARKET_LIST_PATH, params={"is_details": "false"})
        return _MARKET_LIST_ADAPTER.validate_python(response.json())

    async def list_candles(
        self,
        *,
        unit: CandleUnit,
        market: str,
        count: int,
        to: str | None,
    ) -> list[UpbitCandleResponse]:
        params: dict[str, str | int] = {"market": market, "count": count}
        if to is not None:
            params["to"] = to
        response = await self._request("GET", _build_candle_path(unit), params=params)
        return _CANDLE_LIST_ADAPTER.validate_python(response.json())

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any],
    ) -> httpx.Response:
        try:
            response = await self._http_client.request(method, path, params=params)
        except httpx.TimeoutException as exc:
            raise UpbitRestError(status_code=None, message="Upbit REST request timed out.") from exc
        except httpx.HTTPError as exc:
            raise UpbitRestError(status_code=None, message="Upbit REST request failed.") from exc

        if response.is_success:
            return response

        error_name: str | None = None
        message = f"Upbit REST responded with HTTP {response.status_code}."
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict) and isinstance(body.get("error"), dict):
            error = body["error"]
            raw_name = error.get("name")
            raw_message = error.get("message")
            error_name = str(raw_name) if raw_name is not None else None
            message = raw_message if isinstance(raw_message, str) else message

        raise UpbitRestError(
            status_code=response.status_code,
            message=message,
            error_name=error_name,
            remaining_req=response.headers.get("Remaining-Req"),
        )

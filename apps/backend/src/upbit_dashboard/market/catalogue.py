import asyncio
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from upbit_dashboard.contracts.rest import MarketSummary
from upbit_dashboard.upbit.rest import UpbitMarketResponse


MARKET_CODE_PATTERN = re.compile(r"^[A-Z0-9-]+-[A-Z0-9]+$")


@dataclass(frozen=True)
class MarketCode:
    quote_currency: str
    base_currency: str

    def as_upbit_code(self) -> str:
        return f"{self.quote_currency}-{self.base_currency}"


def normalize_market_code(raw_market: str) -> str:
    market = (raw_market or "").strip().upper()
    if not market:
        raise ValueError("Market 코드가 비어 있습니다.")
    return market


def parse_market_code(raw_market: str) -> MarketCode:
    normalized = normalize_market_code(raw_market)
    if not MARKET_CODE_PATTERN.fullmatch(normalized):
        raise ValueError(f"지원하지 않는 Market 코드 형식입니다: {normalized}")

    quote_currency, base_currency = normalized.split("-", 1)
    if not quote_currency or not base_currency:
        raise ValueError(f"지원하지 않는 Market 코드 형식입니다: {normalized}")

    return MarketCode(quote_currency=quote_currency, base_currency=base_currency)


def is_krw_market(raw_market: str) -> bool:
    return parse_market_code(raw_market).quote_currency == "KRW"


def assert_krw_market(raw_market: str) -> MarketCode:
    market = parse_market_code(raw_market)
    if market.quote_currency != "KRW":
        raise ValueError(f"KRW 마켓이 아닙니다: {market.as_upbit_code()}")
    return market


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


class MarketClient(Protocol):
    async def list_markets(self) -> list[UpbitMarketResponse]:
        ...


def map_upbit_market_summary(market: UpbitMarketResponse) -> MarketSummary:
    parsed = assert_krw_market(market.market)
    return MarketSummary(
        market=parsed.as_upbit_code(),
        korean_name=market.korean_name,
        english_name=market.english_name,
        quote_currency=parsed.quote_currency,
        base_currency=parsed.base_currency,
    )


class MarketCatalogueService:
    def __init__(self, *, client: MarketClient, ttl_seconds: int) -> None:
        self._client = client
        self._ttl = timedelta(seconds=ttl_seconds)
        self._markets: tuple[MarketSummary, ...] | None = None
        self._fetched_at: datetime | None = None
        self._refresh_lock = asyncio.Lock()

    async def list_krw_markets(self, now: datetime | None = None) -> tuple[MarketSummary, ...]:
        current_time = now or datetime.now(timezone.utc)
        fresh = self._fresh(current_time)
        if fresh is not None:
            return fresh

        async with self._refresh_lock:
            current_time = now or datetime.now(timezone.utc)
            fresh = self._fresh(current_time)
            if fresh is not None:
                return fresh

            try:
                raw_markets = await self._client.list_markets()
            except Exception:
                if self._markets is not None:
                    return self._markets
                raise

            krw_markets = tuple(
                map_upbit_market_summary(raw_market)
                for raw_market in raw_markets
                if is_krw_market(raw_market.market)
            )
            self._markets = krw_markets
            self._fetched_at = current_time
            return krw_markets

    def _fresh(self, now: datetime) -> tuple[MarketSummary, ...] | None:
        if self._markets is None or self._fetched_at is None:
            return None
        if now - self._fetched_at > self._ttl:
            return None
        return self._markets

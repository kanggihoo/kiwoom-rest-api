from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.logging_config import configure_logging
from upbit_dashboard.settings import (
    DEFAULT_TICKET,
    DEFAULT_TICKER_MARKETS,
    DEFAULT_UPBIT_REST_MARKETS_URL,
    DEFAULT_UPBIT_WS_ENDPOINT,
    SMOKE_TIMEOUT_SECONDS,
    get_settings,
)
from upbit_dashboard.upbit.client import stream_tickers

logger = logging.getLogger(__name__)


def validate_market_response(data: Any) -> int:
    if not isinstance(data, list):
        raise RuntimeError("Upbit REST market response must be a list.")
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("market"), str):
            raise RuntimeError("Upbit REST market response items must include market.")
    return len(data)


async def check_rest_market_endpoint(url: str = DEFAULT_UPBIT_REST_MARKETS_URL) -> int:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        count = validate_market_response(response.json())
        logger.info("REST market check ok count=%s", count)
        return count


async def collect_required_tickers(
    markets: tuple[str, ...] = DEFAULT_TICKER_MARKETS,
    timeout_seconds: float = SMOKE_TIMEOUT_SECONDS,
    endpoint: str = DEFAULT_UPBIT_WS_ENDPOINT,
    ticket: str = DEFAULT_TICKET,
) -> dict[str, TickerData]:
    required = set(markets)
    received: dict[str, TickerData] = {}

    try:
        async with asyncio.timeout(timeout_seconds):
            async for ticker in stream_tickers(
                markets=markets,
                endpoint=endpoint,
                ticket=ticket,
            ):
                logger.info(
                    "ticker received market=%s tradePrice=%s streamType=%s",
                    ticker.market,
                    ticker.trade_price,
                    ticker.stream_type.value,
                )
                if ticker.market in required:
                    received[ticker.market] = ticker
                if required.issubset(received):
                    return received
    except TimeoutError as exc:
        missing = ",".join(sorted(required.difference(received)))
        raise TimeoutError(f"Missing ticker markets before timeout: {missing}") from exc

    missing = ",".join(sorted(required.difference(received)))
    raise RuntimeError(f"Ticker stream ended before required markets arrived: {missing}")


async def main_async() -> None:
    settings = get_settings()
    await check_rest_market_endpoint(settings.upbit_rest_markets_url)
    received = await collect_required_tickers(
        markets=settings.upbit_ticker_markets,
        timeout_seconds=settings.smoke_timeout_seconds,
        endpoint=settings.upbit_ws_endpoint,
        ticket=settings.upbit_ticket,
    )
    logger.info("smoke ok markets=%s", ",".join(sorted(received)))


def main() -> None:
    configure_logging()
    try:
        asyncio.run(main_async())
    except Exception:
        logger.exception("smoke failed")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

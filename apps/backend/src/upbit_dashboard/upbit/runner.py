from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
import inspect
import logging

from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
    INITIAL_BACKOFF_SECONDS,
    MAX_BACKOFF_SECONDS,
)
from upbit_dashboard.upbit.client import stream_tickers

logger = logging.getLogger(__name__)

TickerHandler = Callable[[TickerData], None | Awaitable[None]]


def next_backoff(current: float, maximum: float) -> float:
    if current <= 0:
        raise ValueError("current backoff must be positive")
    if maximum <= 0:
        raise ValueError("maximum backoff must be positive")
    return min(current * 2, maximum)


async def log_ticker(ticker: TickerData) -> None:
    logger.info(
        "Upbit ticker received market=%s tradePrice=%s streamType=%s",
        ticker.market,
        ticker.trade_price,
        ticker.stream_type.value,
    )


async def emit_ticker(handler: TickerHandler, ticker: TickerData) -> None:
    result = handler(ticker)
    if inspect.isawaitable(result):
        await result


async def _sleep_or_stop(stop_event: asyncio.Event | None, delay: float) -> None:
    if stop_event is None:
        await asyncio.sleep(delay)
        return
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=delay)
    except TimeoutError:
        return


async def run_ticker_stream(
    markets: Sequence[str] = DEFAULT_TICKER_MARKETS,
    endpoint: str = DEFAULT_UPBIT_WS_ENDPOINT,
    ticket: str = DEFAULT_TICKET,
    on_ticker: TickerHandler = log_ticker,
    stop_event: asyncio.Event | None = None,
    initial_backoff: float = INITIAL_BACKOFF_SECONDS,
    max_backoff: float = MAX_BACKOFF_SECONDS,
) -> None:
    logger.info("Upbit ticker stream starting markets=%s", ",".join(markets))
    backoff = initial_backoff

    while stop_event is None or not stop_event.is_set():
        try:
            async for ticker in stream_tickers(markets=markets, endpoint=endpoint, ticket=ticket):
                backoff = initial_backoff
                await emit_ticker(on_ticker, ticker)
                if stop_event is not None and stop_event.is_set():
                    return
        except asyncio.CancelledError:
            raise
        except Exception:
            if stop_event is not None and stop_event.is_set():
                return
            logger.warning("Upbit WS disconnected; reconnecting in %.1fs", backoff, exc_info=True)
            await _sleep_or_stop(stop_event, backoff)
            backoff = next_backoff(backoff, max_backoff)

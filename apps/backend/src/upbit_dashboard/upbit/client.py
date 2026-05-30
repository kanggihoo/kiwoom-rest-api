from collections.abc import AsyncIterator, Sequence
from typing import Any
import json
import logging

from websockets.asyncio.client import connect

from upbit_dashboard.contracts.mappers import map_upbit_ticker_message
from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.contracts.upbit import UpbitTickerMessage
from upbit_dashboard.upbit.settings import (
    DEFAULT_TICKER_MARKETS,
    DEFAULT_TICKET,
    DEFAULT_UPBIT_WS_ENDPOINT,
    DEFAULT_WS_FORMAT,
)


logger = logging.getLogger(__name__)


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


async def stream_tickers(
    markets: Sequence[str] = DEFAULT_TICKER_MARKETS,
    endpoint: str = DEFAULT_UPBIT_WS_ENDPOINT,
) -> AsyncIterator[TickerData]:
    subscription = build_ticker_subscription(markets)
    async with connect(endpoint, ping_interval=20, ping_timeout=20) as websocket:
        await websocket.send(json.dumps(subscription))
        logger.info("Upbit WS connected endpoint=%s", endpoint)
        async for payload in websocket:
            try:
                yield parse_ticker_payload(payload)
            except UpbitWebSocketError:
                logger.exception("Upbit WS error payload received")
            except Exception:
                logger.exception("Upbit WS message validation failed")


import os


DEFAULT_UPBIT_WS_ENDPOINT = "wss://api.upbit.com/websocket/v1"
DEFAULT_UPBIT_REST_MARKETS_URL = "https://api.upbit.com/v1/market/all?is_details=false"
DEFAULT_TICKER_MARKETS = ("KRW-BTC", "KRW-ETH")
DEFAULT_TICKET = "upbit-dashboard-phase2"
DEFAULT_WS_FORMAT = "DEFAULT"
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
SMOKE_TIMEOUT_SECONDS = 15.0

_FALSE_VALUES = {"0", "false", "off", "no"}


def is_upbit_ws_enabled(raw_value: str | None = None) -> bool:
    value = os.getenv("UPBIT_WS_ENABLED") if raw_value is None else raw_value
    if value is None or value.strip() == "":
        return True
    return value.strip().lower() not in _FALSE_VALUES


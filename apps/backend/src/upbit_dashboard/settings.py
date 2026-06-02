from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from upbit_dashboard.market.catalogue import parse_krw_market_code_list


DEFAULT_BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

DEFAULT_LOG_FORMAT = "plain"
DEFAULT_LOG_LEVEL = "INFO"
SUPPORTED_LOG_FORMATS = {"plain", "rich"}

DEFAULT_UPBIT_WS_ENDPOINT = "wss://api.upbit.com/websocket/v1"
DEFAULT_UPBIT_REST_MARKETS_URL = "https://api.upbit.com/v1/market/all?is_details=false"
DEFAULT_UPBIT_REST_BASE_URL = "https://api.upbit.com"
DEFAULT_TICKER_MARKETS = ("KRW-BTC", "KRW-ETH")
DEFAULT_MARKET_CATALOGUE_TTL_SECONDS = 600
DEFAULT_TICKER_MARKETS_MODE = "all_krw"
DEFAULT_TICKET = "upbit-dashboard-phase2"
DEFAULT_WS_FORMAT = "DEFAULT"
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
SMOKE_TIMEOUT_SECONDS = 15.0
TickerMarketsMode = Literal["all_krw", "configured"]

_FLOAT_DEFAULTS = {
    "initial_backoff_seconds": INITIAL_BACKOFF_SECONDS,
    "max_backoff_seconds": MAX_BACKOFF_SECONDS,
    "smoke_timeout_seconds": SMOKE_TIMEOUT_SECONDS,
}
_INT_DEFAULTS = {
    "market_catalogue_ttl_seconds": DEFAULT_MARKET_CATALOGUE_TTL_SECONDS,
}


class BackendSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DEFAULT_BACKEND_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    log_format: str = Field(DEFAULT_LOG_FORMAT, validation_alias="LOG_FORMAT")
    log_level: str = Field(DEFAULT_LOG_LEVEL, validation_alias="LOG_LEVEL")
    upbit_ws_enabled: bool = Field(True, validation_alias="UPBIT_WS_ENABLED")
    upbit_ws_endpoint: str = Field(
        DEFAULT_UPBIT_WS_ENDPOINT,
        validation_alias="UPBIT_WS_ENDPOINT",
    )
    upbit_rest_base_url: str = Field(
        DEFAULT_UPBIT_REST_BASE_URL,
        validation_alias="UPBIT_REST_BASE_URL",
    )
    upbit_rest_markets_url: str = Field(
        DEFAULT_UPBIT_REST_MARKETS_URL,
        validation_alias="UPBIT_REST_MARKETS_URL",
    )
    market_catalogue_ttl_seconds: int = Field(
        DEFAULT_MARKET_CATALOGUE_TTL_SECONDS,
        gt=0,
        validation_alias="MARKET_CATALOGUE_TTL_SECONDS",
    )
    upbit_ticker_markets: Annotated[tuple[str, ...], NoDecode] = Field(
        DEFAULT_TICKER_MARKETS,
        validation_alias="UPBIT_TICKER_MARKETS",
    )
    upbit_ticker_markets_mode: TickerMarketsMode = Field(
        DEFAULT_TICKER_MARKETS_MODE,
        validation_alias="UPBIT_TICKER_MARKETS_MODE",
    )
    upbit_ticket: str = Field(
        DEFAULT_TICKET,
        validation_alias="UPBIT_TICKET",
    )
    initial_backoff_seconds: float = Field(
        INITIAL_BACKOFF_SECONDS,
        gt=0,
        validation_alias="UPBIT_INITIAL_BACKOFF_SECONDS",
    )
    max_backoff_seconds: float = Field(
        MAX_BACKOFF_SECONDS,
        gt=0,
        validation_alias="UPBIT_MAX_BACKOFF_SECONDS",
    )
    smoke_timeout_seconds: float = Field(
        SMOKE_TIMEOUT_SECONDS,
        gt=0,
        validation_alias="UPBIT_SMOKE_TIMEOUT_SECONDS",
    )

    @field_validator("log_format", mode="before")
    @classmethod
    def validate_log_format(cls, value: object) -> str:
        return normalize_log_format(value if isinstance(value, str) else None)

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, value: object) -> str:
        return normalize_log_level(value if isinstance(value, str) else None)

    @field_validator("upbit_ws_enabled", mode="before")
    @classmethod
    def validate_upbit_ws_enabled(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return True
        return value

    @field_validator("upbit_ticker_markets", mode="before")
    @classmethod
    def validate_upbit_ticker_markets(cls, value: object) -> tuple[str, ...] | object:
        if not isinstance(value, str):
            return value
        return parse_krw_market_code_list(value, default=DEFAULT_TICKER_MARKETS)

    @field_validator("upbit_ticker_markets_mode", mode="before")
    @classmethod
    def validate_upbit_ticker_markets_mode(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return DEFAULT_TICKER_MARKETS_MODE
        return value

    @field_validator(
        "initial_backoff_seconds",
        "max_backoff_seconds",
        "smoke_timeout_seconds",
        mode="before",
    )
    @classmethod
    def validate_optional_positive_float(
        cls,
        value: object,
        info: ValidationInfo,
    ) -> object:
        if isinstance(value, str) and value.strip() == "":
            return _FLOAT_DEFAULTS[info.field_name]
        return value

    @field_validator("market_catalogue_ttl_seconds", mode="before")
    @classmethod
    def validate_optional_positive_int(
        cls,
        value: object,
        info: ValidationInfo,
    ) -> object:
        if isinstance(value, str) and value.strip() == "":
            return _INT_DEFAULTS[info.field_name]
        return value


def normalize_log_format(raw_value: str | None) -> str:
    if raw_value is None or raw_value.strip() == "":
        return DEFAULT_LOG_FORMAT

    normalized = raw_value.strip().lower()
    if normalized not in SUPPORTED_LOG_FORMATS:
        return DEFAULT_LOG_FORMAT
    return normalized


def normalize_log_level(raw_value: str | None) -> str:
    if raw_value is None or raw_value.strip() == "":
        return DEFAULT_LOG_LEVEL

    normalized = raw_value.strip().upper()
    level_value = logging.getLevelNamesMapping().get(normalized)
    if not isinstance(level_value, int):
        return DEFAULT_LOG_LEVEL
    return normalized


@lru_cache
def get_settings() -> BackendSettings:
    return BackendSettings()

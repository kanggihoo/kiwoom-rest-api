from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from upbit_dashboard.settings import BackendSettings, DEFAULT_BACKEND_ENV_FILE


def test_backend_settings_uses_pydantic_base_settings() -> None:
    assert issubclass(BackendSettings, BaseSettings)
    assert BackendSettings.model_config["env_file"] == DEFAULT_BACKEND_ENV_FILE


def test_backend_settings_use_mvp_defaults() -> None:
    settings = BackendSettings(_env_file=None)

    assert settings.log_format == "plain"
    assert settings.log_level == "INFO"
    assert settings.upbit_ws_enabled is True
    assert settings.upbit_ws_endpoint == "wss://api.upbit.com/websocket/v1"
    assert settings.upbit_rest_markets_url == "https://api.upbit.com/v1/market/all?is_details=false"
    assert settings.upbit_ticker_markets == ("KRW-BTC", "KRW-ETH")
    assert settings.upbit_ticket == "upbit-dashboard-phase2"
    assert settings.initial_backoff_seconds == 1.0
    assert settings.max_backoff_seconds == 30.0
    assert settings.smoke_timeout_seconds == 15.0


def test_backend_settings_read_and_normalize_environment_values() -> None:
    settings = BackendSettings(
        LOG_FORMAT="RICH",
        LOG_LEVEL="debug",
        UPBIT_WS_ENABLED="off",
        UPBIT_WS_ENDPOINT="wss://example.test/ws",
        UPBIT_REST_MARKETS_URL="https://example.test/markets",
        UPBIT_TICKER_MARKETS=" krw-btc,KRW-XRP, ,krw-eth ",
        UPBIT_TICKET="local-ticket",
        UPBIT_INITIAL_BACKOFF_SECONDS="2.5",
        UPBIT_MAX_BACKOFF_SECONDS="20",
        UPBIT_SMOKE_TIMEOUT_SECONDS="7",
        _env_file=None,
    )

    assert settings.log_format == "rich"
    assert settings.log_level == "DEBUG"
    assert settings.upbit_ws_enabled is False
    assert settings.upbit_ws_endpoint == "wss://example.test/ws"
    assert settings.upbit_rest_markets_url == "https://example.test/markets"
    assert settings.upbit_ticker_markets == ("KRW-BTC", "KRW-XRP", "KRW-ETH")
    assert settings.upbit_ticket == "local-ticket"
    assert settings.initial_backoff_seconds == 2.5
    assert settings.max_backoff_seconds == 20.0
    assert settings.smoke_timeout_seconds == 7.0


def test_backend_settings_reads_env_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "UPBIT_WS_ENABLED=false",
                "UPBIT_TICKER_MARKETS=KRW-XRP,KRW-ETH",
                "LOG_LEVEL=debug",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("UPBIT_WS_ENABLED", raising=False)
    monkeypatch.delenv("UPBIT_TICKER_MARKETS", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = BackendSettings(_env_file=env_file)

    assert settings.upbit_ws_enabled is False
    assert settings.upbit_ticker_markets == ("KRW-XRP", "KRW-ETH")
    assert settings.log_level == "DEBUG"


def test_shell_environment_overrides_backend_env_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("UPBIT_WS_ENABLED=false\n", encoding="utf-8")
    monkeypatch.setenv("UPBIT_WS_ENABLED", "true")

    settings = BackendSettings(_env_file=env_file)

    assert settings.upbit_ws_enabled is True


def test_backend_settings_reject_non_krw_ticker_markets() -> None:
    with pytest.raises(ValidationError, match="KRW"):
        BackendSettings(
            UPBIT_TICKER_MARKETS="KRW-BTC,USDT-ETH",
            _env_file=None,
        )

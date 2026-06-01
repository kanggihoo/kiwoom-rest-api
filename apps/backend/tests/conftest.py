import pytest


SETTING_ENV_NAMES = (
    "LOG_FORMAT",
    "LOG_LEVEL",
    "UPBIT_WS_ENABLED",
    "UPBIT_WS_ENDPOINT",
    "UPBIT_REST_MARKETS_URL",
    "UPBIT_TICKER_MARKETS",
    "UPBIT_TICKET",
    "UPBIT_INITIAL_BACKOFF_SECONDS",
    "UPBIT_MAX_BACKOFF_SECONDS",
    "UPBIT_SMOKE_TIMEOUT_SECONDS",
)


@pytest.fixture(autouse=True)
def isolate_backend_env_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for env_name in SETTING_ENV_NAMES:
        monkeypatch.delenv(env_name, raising=False)

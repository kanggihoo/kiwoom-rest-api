import pytest

from upbit_dashboard.settings import get_settings


SETTING_ENV_NAMES = (
    "LOG_FORMAT",
    "LOG_LEVEL",
    "UPBIT_WS_ENABLED",
    "UPBIT_WS_ENDPOINT",
    "UPBIT_REST_MARKETS_URL",
    "UPBIT_REST_BASE_URL",
    "UPBIT_TICKER_MARKETS",
    "MARKET_CATALOGUE_TTL_SECONDS",
    "UPBIT_TICKER_MARKETS_MODE",
    "UPBIT_TICKET",
    "UPBIT_INITIAL_BACKOFF_SECONDS",
    "UPBIT_MAX_BACKOFF_SECONDS",
    "UPBIT_SMOKE_TIMEOUT_SECONDS",
)


@pytest.fixture(autouse=True)
def isolate_backend_env_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    for env_name in SETTING_ENV_NAMES:
        monkeypatch.delenv(env_name, raising=False)
    yield
    get_settings.cache_clear()

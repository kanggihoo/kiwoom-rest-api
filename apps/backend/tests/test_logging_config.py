import logging

import pytest

from upbit_dashboard.logging_config import (
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    build_logging_config,
    get_log_format,
    get_log_level,
)


def test_default_log_format_is_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOG_FORMAT", raising=False)

    assert get_log_format() == DEFAULT_LOG_FORMAT
    assert get_log_format() == "plain"


def test_unknown_log_format_falls_back_to_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "unknown")

    assert get_log_format() == "plain"


def test_rich_log_format_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "rich")

    assert get_log_format() == "rich"


def test_log_format_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "RICH")

    assert get_log_format() == "rich"


def test_default_log_level_is_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    assert get_log_level() == DEFAULT_LOG_LEVEL
    assert get_log_level() == "INFO"


def test_debug_log_level_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")

    assert get_log_level() == "DEBUG"


def test_unknown_log_level_falls_back_to_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "verbose")

    assert get_log_level() == "INFO"


def test_plain_logging_config_contains_expected_loggers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "plain")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = build_logging_config()

    assert config["version"] == 1
    assert config["disable_existing_loggers"] is False
    assert config["root"] == {"handlers": ["console"], "level": "DEBUG"}
    assert config["handlers"]["console"]["class"] == "logging.StreamHandler"
    assert config["handlers"]["console"]["formatter"] == "plain"
    assert config["formatters"]["plain"]["format"] == "%(asctime)s %(levelname)-8s [%(name)s] %(filename)s:%(lineno)d %(message)s"
    assert config["formatters"]["plain"]["datefmt"] == "%Y-%m-%d %H:%M:%S"

    for logger_name in ("upbit_dashboard", "uvicorn", "uvicorn.error", "uvicorn.access"):
        assert config["loggers"][logger_name] == {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        }


def test_rich_logging_config_uses_rich_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "rich")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    config = build_logging_config()

    assert config["handlers"]["console"]["class"] == "rich.logging.RichHandler"
    assert config["handlers"]["console"]["level"] == "INFO"
    assert config["handlers"]["console"]["rich_tracebacks"] is True
    assert config["handlers"]["console"]["show_time"] is True
    assert config["handlers"]["console"]["show_level"] is True
    assert config["handlers"]["console"]["show_path"] is True
    assert config["handlers"]["console"]["enable_link_path"] is True
    assert config["handlers"]["console"]["markup"] is False
    assert config["handlers"]["console"]["formatter"] == "rich"
    assert config["formatters"]["rich"]["format"] == "%(message)s"


def test_known_logging_level_names_are_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    for level_name in logging.getLevelNamesMapping():
        if isinstance(logging.getLevelName(level_name), int):
            monkeypatch.setenv("LOG_LEVEL", level_name.lower())
            assert get_log_level() == level_name

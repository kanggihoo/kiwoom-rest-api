from __future__ import annotations

import logging
import logging.config
import os
from typing import Any


DEFAULT_LOG_FORMAT = "plain"
DEFAULT_LOG_LEVEL = "INFO"
SUPPORTED_LOG_FORMATS = {"plain", "rich"}

APP_LOGGERS = (
    "upbit_dashboard",
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
)

PLAIN_LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(filename)s:%(lineno)d %(message)s"
PLAIN_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
RICH_LOG_FORMAT = "%(message)s"


def get_log_format(raw_value: str | None = None) -> str:
    value = os.getenv("LOG_FORMAT") if raw_value is None else raw_value
    if value is None or value.strip() == "":
        return DEFAULT_LOG_FORMAT

    normalized = value.strip().lower()
    if normalized not in SUPPORTED_LOG_FORMATS:
        return DEFAULT_LOG_FORMAT
    return normalized


def get_log_level(raw_value: str | None = None) -> str:
    value = os.getenv("LOG_LEVEL") if raw_value is None else raw_value
    if value is None or value.strip() == "":
        return DEFAULT_LOG_LEVEL

    normalized = value.strip().upper()
    level_value = logging.getLevelNamesMapping().get(normalized)
    if not isinstance(level_value, int):
        return DEFAULT_LOG_LEVEL
    return normalized


def build_logging_config() -> dict[str, Any]:
    log_format = get_log_format()
    log_level = get_log_level()

    if log_format == "rich":
        return _build_rich_config(log_level)
    return _build_plain_config(log_level)


def configure_logging() -> None:
    logging.config.dictConfig(build_logging_config())


def _build_plain_config(log_level: str) -> dict[str, Any]:
    return _base_config(
        log_level=log_level,
        formatter_name="plain",
        formatters={
            "plain": {
                "format": PLAIN_LOG_FORMAT,
                "datefmt": PLAIN_DATE_FORMAT,
            }
        },
        handler={
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "plain",
            "stream": "ext://sys.stderr",
        },
    )


def _build_rich_config(log_level: str) -> dict[str, Any]:
    return _base_config(
        log_level=log_level,
        formatter_name="rich",
        formatters={
            "rich": {
                "format": RICH_LOG_FORMAT,
            }
        },
        handler={
            "class": "rich.logging.RichHandler",
            "level": log_level,
            "formatter": "rich",
            "rich_tracebacks": True,
            "show_time": True,
            "show_level": True,
            "show_path": True,
            "enable_link_path": True,
            "markup": False,
        },
    )


def _base_config(
    *,
    log_level: str,
    formatter_name: str,
    formatters: dict[str, dict[str, Any]],
    handler: dict[str, Any],
) -> dict[str, Any]:
    del formatter_name
    loggers = {
        logger_name: {
            "handlers": ["console"],
            "level": log_level,
            "propagate": False,
        }
        for logger_name in APP_LOGGERS
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "console": handler,
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
        "loggers": loggers,
    }

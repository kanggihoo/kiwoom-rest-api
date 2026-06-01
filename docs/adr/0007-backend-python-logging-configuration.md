# Backend Python Logging Configuration

## Status

Accepted

## Context

The FastAPI backend uses Python's standard `logging.getLogger(__name__)` pattern across application modules, but it does not yet have a shared logging configuration entrypoint. Uvicorn also emits its own `uvicorn`, `uvicorn.error`, and `uvicorn.access` logs, while backend command-line tools can configure logging independently.

If each entrypoint configures logging separately, log format, level handling, handler behavior, and uvicorn integration will drift over time. The backend needs one logging policy that works for the FastAPI app, uvicorn, and local backend tools.

The immediate need is local development debugging. Rich console logging is useful for readable colored output, rich tracebacks, and source file/line display, but ANSI-styled output should not become the default behavior for every environment.

## Decision

Configure backend Python logging through one application-owned module:

```text
apps/backend/src/upbit_dashboard/logging_config.py
```

Use Python's standard `logging` package and `logging.config.dictConfig(...)` as the configuration mechanism.

The logging configuration module owns:

- log format selection
- log level selection
- console handler selection
- root logger configuration
- `upbit_dashboard` logger configuration
- `uvicorn`, `uvicorn.error`, and `uvicorn.access` logger configuration

Use environment variables for runtime selection:

```text
LOG_FORMAT=plain|rich
LOG_LEVEL=INFO|DEBUG|...
```

`LOG_FORMAT` defaults to `plain`.

`LOG_LEVEL` defaults to `INFO`.

`LOG_FORMAT=rich` enables `rich.logging.RichHandler` for local development debugging. Rich logging should show time, level, message, and the source file/line path column. Rich tracebacks should be enabled. Rich markup in application log messages should remain disabled.

Keep the default plain formatter readable in terminals and CI, including timestamp, level, logger name, source file/line, and message.

Do not use an external YAML or JSON logging configuration file for the MVP. Keeping the configuration in Python allows environment parsing, fallback behavior, and handler selection to stay close to the application runtime.

Do not introduce JSON logging, file logging, log rotation, or external log collector integration in this decision.

## Consequences

FastAPI, uvicorn, and backend command-line tools can share the same logging behavior by calling `configure_logging()`.

Uvicorn access and error logs will follow the backend logging policy instead of drifting from application logs.

Local developers can opt into Rich logs with:

```bash
LOG_FORMAT=rich LOG_LEVEL=DEBUG make dev-api
```

Plain logs remain the default, which keeps local defaults, CI output, and future non-interactive environments free from Rich-specific formatting unless explicitly enabled.

The backend gains a runtime dependency on `rich`, but it is only used when `LOG_FORMAT=rich`.

Future logging features, such as JSON logs or file handlers, should extend `logging_config.py` deliberately instead of adding route-local, tool-local, or module-local logging setup.

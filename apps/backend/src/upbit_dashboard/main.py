from contextlib import asynccontextmanager, suppress
import asyncio
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI

from upbit_dashboard.api.exception_handlers import register_exception_handlers
from upbit_dashboard.api.router import api_router
from upbit_dashboard.logging_config import configure_logging
from upbit_dashboard.state.market_state import MarketState
from upbit_dashboard.upbit.runner import run_ticker_stream
from upbit_dashboard.upbit.settings import is_upbit_ws_enabled

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ticker_task: asyncio.Task[None] | None = None

    if is_upbit_ws_enabled():
        ticker_task = asyncio.create_task(run_ticker_stream())
        logger.info("Upbit ticker stream background task created")
    else:
        logger.info("Upbit ticker stream disabled by UPBIT_WS_ENABLED=false")

    app.state.upbit_ticker_task = ticker_task

    try:
        yield
    finally:
        if ticker_task is not None:
            ticker_task.cancel()
            with suppress(asyncio.CancelledError):
                await ticker_task


def create_app() -> FastAPI:
    app = FastAPI(title="Upbit Dashboard API", lifespan=lifespan)
    app.state.market_state = MarketState()
    app.state.upbit_ticker_task = None

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


app = create_app()

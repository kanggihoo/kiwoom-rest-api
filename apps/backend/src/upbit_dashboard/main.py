from contextlib import asynccontextmanager, suppress
import asyncio
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI
import httpx

from upbit_dashboard.api.exception_handlers import register_exception_handlers
from upbit_dashboard.api.queries.quotation import QuotationReadService
from upbit_dashboard.api.router import api_router
from upbit_dashboard.api.routes import health
from upbit_dashboard.logging_config import configure_logging
from upbit_dashboard.settings import get_settings
from upbit_dashboard.contracts.quotation import TickerData
from upbit_dashboard.market.catalogue import MarketCatalogueService
from upbit_dashboard.state.market_state import MarketState
from upbit_dashboard.upbit.rest import UpbitRestClient
from upbit_dashboard.upbit.runner import log_ticker, run_ticker_stream

logger = logging.getLogger(__name__)


async def handle_ticker(app: FastAPI, ticker: TickerData) -> None:
    app.state.market_state.upsert_ticker(ticker)
    await log_ticker(ticker)


async def resolve_ticker_markets(settings, market_catalogue) -> tuple[str, ...]:
    if settings.upbit_ticker_markets_mode == "configured":
        return settings.upbit_ticker_markets
    markets = await market_catalogue.list_krw_markets()
    return tuple(market.market for market in markets)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ticker_task: asyncio.Task[None] | None = None
    settings = get_settings()
    http_client = httpx.AsyncClient(base_url=settings.upbit_rest_base_url, timeout=5.0)
    upbit_rest_client = UpbitRestClient(http_client=http_client)

    app.state.settings = settings
    app.state.market_state = MarketState()
    app.state.upbit_rest_http_client = http_client
    app.state.market_catalogue = MarketCatalogueService(
        client=upbit_rest_client,
        ttl_seconds=settings.market_catalogue_ttl_seconds,
    )
    app.state.upbit_rest_client = upbit_rest_client
    app.state.quotation_read_service = QuotationReadService(
        market_catalogue=app.state.market_catalogue,
        upbit_rest_client=upbit_rest_client,
        market_state=app.state.market_state,
    )

    try:
        if settings.upbit_ws_enabled:
            markets = await resolve_ticker_markets(settings, app.state.market_catalogue)

            async def on_ticker(ticker: TickerData) -> None:
                await handle_ticker(app, ticker)

            ticker_task = asyncio.create_task(
                run_ticker_stream(
                    markets=markets,
                    endpoint=settings.upbit_ws_endpoint,
                    ticket=settings.upbit_ticket,
                    on_ticker=on_ticker,
                    initial_backoff=settings.initial_backoff_seconds,
                    max_backoff=settings.max_backoff_seconds,
                )
            )
            logger.info("Upbit ticker stream background task created")
        else:
            logger.info("Upbit ticker stream disabled by UPBIT_WS_ENABLED=false")

        app.state.upbit_ticker_task = ticker_task

        yield
    finally:
        if ticker_task is not None:
            ticker_task.cancel()
            with suppress(asyncio.CancelledError):
                await ticker_task
        await http_client.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(title="Upbit Dashboard API", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(api_router)

    return app


app = create_app()

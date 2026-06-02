from fastapi import APIRouter

from upbit_dashboard.api.routes import candles, markets, snapshot

api_router = APIRouter(prefix="/api")
api_router.include_router(markets.router)
api_router.include_router(snapshot.router)
api_router.include_router(candles.router)

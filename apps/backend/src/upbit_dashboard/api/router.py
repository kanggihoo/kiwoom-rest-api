from fastapi import APIRouter

from upbit_dashboard.api.routes import health, snapshot

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(snapshot.router)

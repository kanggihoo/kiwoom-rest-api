from fastapi import APIRouter

from upbit_dashboard.api.routes import health

api_router = APIRouter()
api_router.include_router(health.router)

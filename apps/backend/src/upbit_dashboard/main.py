from fastapi import FastAPI, Request

from upbit_dashboard.api.errors import DashboardApiError, make_error_response
from upbit_dashboard.state.market_state import MarketState

app = FastAPI(title="Upbit Dashboard API")
app.state.market_state = MarketState()


@app.exception_handler(DashboardApiError)
async def api_error_handler(_: Request, exc: DashboardApiError):
    return make_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "upbit-dashboard-backend"}

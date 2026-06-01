from fastapi import FastAPI
from fastapi.testclient import TestClient

from upbit_dashboard.api.errors import DashboardApiError
from upbit_dashboard.api.exception_handlers import register_exception_handlers
from upbit_dashboard.contracts.errors import RestErrorCode


def test_register_exception_handlers_maps_dashboard_api_error() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-dashboard-api-error")
    def raise_dashboard_api_error() -> None:
        raise DashboardApiError(
            code=RestErrorCode.NOT_FOUND,
            message="Market not found.",
            details={"market": "KRW-UNKNOWN"},
        )

    response = TestClient(app).get("/raise-dashboard-api-error")

    assert response.status_code == 404
    assert response.json()["type"] == "error"
    assert response.json()["data"] == {
        "code": "NOT_FOUND",
        "message": "Market not found.",
        "details": {"market": "KRW-UNKNOWN"},
    }

from fastapi import FastAPI, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from upbit_dashboard.api.errors import DashboardApiError
from upbit_dashboard.api.exception_handlers import register_exception_handlers
from upbit_dashboard.contracts.errors import RestErrorCode
from upbit_dashboard.upbit.rest import UpbitRestError


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


def test_register_exception_handlers_maps_request_validation_error() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/requires-count")
    def requires_count(count: int = Query(le=200)) -> dict[str, int]:
        return {"count": count}

    response = TestClient(app).get("/requires-count?count=201")

    assert response.status_code == 422
    body = response.json()
    assert body["type"] == "error"
    assert body["data"]["code"] == "VALIDATION_ERROR"
    assert body["data"]["message"] == "Request validation failed."
    assert body["data"]["details"]["errors"][0]["loc"] == ["query", "count"]


def test_request_validation_error_handler_serializes_validator_context() -> None:
    class Payload(BaseModel):
        name: str

        @field_validator("name")
        @classmethod
        def reject_bad_name(cls, value: str) -> str:
            if value == "bad":
                raise ValueError("bad name")
            return value

    app = FastAPI()
    register_exception_handlers(app)

    @app.post("/payload")
    def accept_payload(payload: Payload) -> Payload:
        return payload

    response = TestClient(app).post("/payload", json={"name": "bad"})

    assert response.status_code == 422
    body = response.json()
    assert body["type"] == "error"
    error = body["data"]["details"]["errors"][0]
    assert error["loc"] == ["body", "name"]
    assert error["ctx"]["error"] == "bad name"


def test_register_exception_handlers_maps_upbit_rest_error() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-upbit-rest-error")
    def raise_upbit_rest_error() -> None:
        raise UpbitRestError(
            status_code=429,
            message="Too many requests",
            error_name="429",
            remaining_req="group=candle; min=1800; sec=0",
        )

    response = TestClient(app).get("/raise-upbit-rest-error")

    assert response.status_code == 429
    assert response.json()["type"] == "error"
    assert response.json()["data"] == {
        "code": "RATE_LIMITED",
        "message": "Too many requests",
        "details": {
            "upbitStatus": 429,
            "upbitErrorName": "429",
            "remainingReq": "group=candle; min=1800; sec=0",
        },
    }

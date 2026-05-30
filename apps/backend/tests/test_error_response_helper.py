import json

from upbit_dashboard.api.errors import make_error_response, make_error_response_or_fallback
from upbit_dashboard.contracts.errors import RestErrorCode


def test_make_error_response_uses_contract_status_mapping() -> None:
    response = make_error_response(
        code=RestErrorCode.RATE_LIMITED,
        message="limit",
        details={"upbitStatus": 429},
    )

    payload = json.loads(response.body.decode())

    assert response.status_code == 429
    assert payload["type"] == "error"
    assert payload["data"]["code"] == "RATE_LIMITED"
    assert payload["data"]["details"]["upbitStatus"] == 429


def test_make_error_response_or_fallback_returns_fallback_for_invalid_detail() -> None:
    response = make_error_response_or_fallback(
        code=RestErrorCode.BAD_REQUEST,
        message="bad request",
        details={"bad": object()},
    )

    payload = json.loads(response.body.decode())

    assert response.status_code == 500
    assert payload["type"] == "error"

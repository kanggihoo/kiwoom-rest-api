from datetime import datetime, timezone

from upbit_dashboard.contracts.errors import (
    ErrorData,
    ErrorEnvelope,
    RestErrorCode,
    WebSocketErrorCode,
    rest_status_for_error,
)


def test_error_envelope_serializes_code_as_string() -> None:
    envelope = ErrorEnvelope(
        timestamp=datetime(2026, 5, 30, 3, 0, tzinfo=timezone.utc),
        data=ErrorData(
            code=RestErrorCode.RATE_LIMITED,
            message="Upbit request rate limit exceeded.",
            details={
                "upbitStatus": 429,
                "rateLimitGroup": "candle",
                "remainingSec": 0,
            },
        ),
    )

    assert envelope.model_dump(mode="json") == {
        "type": "error",
        "timestamp": "2026-05-30T03:00:00Z",
        "data": {
            "code": "RATE_LIMITED",
            "message": "Upbit request rate limit exceeded.",
            "details": {
                "upbitStatus": 429,
                "rateLimitGroup": "candle",
                "remainingSec": 0,
            },
        },
    }


def test_rest_error_status_mapping_separates_bad_request_and_validation() -> None:
    assert rest_status_for_error(RestErrorCode.BAD_REQUEST) == 400
    assert rest_status_for_error(RestErrorCode.VALIDATION_ERROR) == 422


def test_rest_error_status_mapping_separates_rate_limit_and_block() -> None:
    assert rest_status_for_error(RestErrorCode.TEMPORARILY_BLOCKED) == 418
    assert rest_status_for_error(RestErrorCode.RATE_LIMITED) == 429


def test_websocket_error_codes_include_upbit_error_cases() -> None:
    assert WebSocketErrorCode.UPBIT_WS_ERROR.value == "UPBIT_WS_ERROR"
    assert WebSocketErrorCode.RATE_LIMITED.value == "RATE_LIMITED"
    assert WebSocketErrorCode.TEMPORARILY_BLOCKED.value == "TEMPORARILY_BLOCKED"

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import status
from fastapi.responses import JSONResponse

from upbit_dashboard.contracts.errors import RestErrorCode, rest_status_for_error
from upbit_dashboard.contracts.errors import make_error_envelope


@dataclass
class DashboardApiError(Exception):
    code: RestErrorCode
    message: str
    details: dict[str, Any] | None = None
    status_code: int | None = None


def make_error_response(
    code: RestErrorCode,
    message: str,
    details: dict[str, Any] | None = None,
    status_code: int | None = None,
) -> JSONResponse:
    envelope = make_error_envelope(code=code, message=message, details=_json_safe(details))
    response_status = status_code or rest_status_for_error(code)
    return JSONResponse(status_code=response_status, content=envelope.model_dump(mode="json"))


def _json_safe(value: Any) -> Any:
    if isinstance(value, BaseException):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_safe(nested_value) for key, nested_value in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(nested_value) for nested_value in value]
    if isinstance(value, list):
        return [_json_safe(nested_value) for nested_value in value]
    if isinstance(value, set):
        return [_json_safe(nested_value) for nested_value in sorted(value, key=repr)]
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_json_safe(nested_value) for nested_value in value]
    return value


def make_error_response_or_fallback(
    code: RestErrorCode,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    try:
        return make_error_response(
            code=code,
            message=message,
            details=details,
        )
    except Exception as exc:  # pragma: no cover
        # 계약 코드가 깨지더라도 FastAPI가 500 대신 안전하게 응답할 수 있게 fallback 처리.
        fallback_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(
            status_code=fallback_status,
            content={
                "type": "error",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "data": {
                    "code": RestErrorCode.INTERNAL_ERROR,
                    "message": "Error envelope serialization failed.",
                    "details": {"originalError": str(exc)},
                },
            },
        )

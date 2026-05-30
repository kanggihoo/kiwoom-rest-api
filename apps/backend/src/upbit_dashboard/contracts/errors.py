from datetime import datetime
from datetime import timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class RestErrorCode(StrEnum):
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    TEMPORARILY_BLOCKED = "TEMPORARILY_BLOCKED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    UPBIT_BAD_REQUEST = "UPBIT_BAD_REQUEST"
    UPBIT_ERROR = "UPBIT_ERROR"
    UPBIT_TIMEOUT = "UPBIT_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class WebSocketErrorCode(StrEnum):
    INVALID_MESSAGE = "INVALID_MESSAGE"
    UNSUPPORTED_MESSAGE_TYPE = "UNSUPPORTED_MESSAGE_TYPE"
    INVALID_MARKET = "INVALID_MARKET"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    TEMPORARILY_BLOCKED = "TEMPORARILY_BLOCKED"
    UPBIT_WS_ERROR = "UPBIT_WS_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


REST_ERROR_STATUS: dict[RestErrorCode, int] = {
    RestErrorCode.BAD_REQUEST: 400,
    RestErrorCode.NOT_FOUND: 404,
    RestErrorCode.TEMPORARILY_BLOCKED: 418,
    RestErrorCode.VALIDATION_ERROR: 422,
    RestErrorCode.RATE_LIMITED: 429,
    RestErrorCode.UPBIT_BAD_REQUEST: 502,
    RestErrorCode.UPBIT_ERROR: 502,
    RestErrorCode.UPBIT_TIMEOUT: 504,
    RestErrorCode.INTERNAL_ERROR: 500,
}


class ErrorData(BaseModel):
    code: RestErrorCode | WebSocketErrorCode = Field(
        description="앱 내부 에러 코드. HTTP status와 별도로 프론트 분기에 사용한다.",
    )
    message: str = Field(description="사람이 읽을 수 있는 짧은 에러 설명.")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Upbit 원본 status/error.name/Remaining-Req 등 추가 맥락.",
    )


class ErrorEnvelope(BaseModel):
    type: Literal["error"] = Field(
        default="error",
        description="에러 envelope type.",
    )
    timestamp: datetime = Field(
        description="우리 서버가 에러 응답 또는 이벤트를 만든 시각.",
    )
    data: ErrorData = Field(description="에러 상세 payload.")


def rest_status_for_error(code: RestErrorCode) -> int:
    return REST_ERROR_STATUS[code]


def make_error_envelope(
    code: RestErrorCode | WebSocketErrorCode,
    message: str,
    details: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
) -> ErrorEnvelope:
    return ErrorEnvelope(
        timestamp=timestamp or datetime.now(timezone.utc),
        data=ErrorData(code=code, message=message, details=details),
    )

from upbit_dashboard.api.errors import DashboardApiError
from upbit_dashboard.contracts.errors import RestErrorCode
from upbit_dashboard.upbit.rest import UpbitRestError


def map_upbit_rest_error(error: UpbitRestError) -> DashboardApiError:
    status_code = error.status_code
    details = {
        "upbitStatus": status_code,
        "upbitErrorName": error.error_name,
        "remainingReq": error.remaining_req,
    }

    if status_code == 418:
        return DashboardApiError(
            code=RestErrorCode.TEMPORARILY_BLOCKED,
            message=error.message,
            details=details,
            status_code=418,
        )
    if status_code == 429:
        return DashboardApiError(
            code=RestErrorCode.RATE_LIMITED,
            message=error.message,
            details=details,
            status_code=429,
        )
    if status_code == 400:
        return DashboardApiError(
            code=RestErrorCode.UPBIT_BAD_REQUEST,
            message=error.message,
            details=details,
            status_code=502,
        )
    if status_code is None:
        return DashboardApiError(
            code=RestErrorCode.UPBIT_TIMEOUT if "timed out" in error.message else RestErrorCode.UPBIT_ERROR,
            message=error.message,
            details=details,
        )
    return DashboardApiError(
        code=RestErrorCode.UPBIT_ERROR,
        message=error.message,
        details=details,
    )

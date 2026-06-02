from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from upbit_dashboard.api.errors import DashboardApiError, make_error_response
from upbit_dashboard.api.upbit_errors import map_upbit_rest_error
from upbit_dashboard.contracts.errors import RestErrorCode
from upbit_dashboard.upbit.rest import UpbitRestError


async def dashboard_api_error_handler(_: Request, exc: DashboardApiError):
    return make_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
    )


async def request_validation_error_handler(_: Request, exc: RequestValidationError):
    return make_error_response(
        code=RestErrorCode.VALIDATION_ERROR,
        message="Request validation failed.",
        details={"errors": exc.errors()},
        status_code=422,
    )


async def upbit_rest_error_handler(request: Request, exc: UpbitRestError):
    api_error = map_upbit_rest_error(exc)
    return await dashboard_api_error_handler(request, api_error)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DashboardApiError, dashboard_api_error_handler)
    app.add_exception_handler(UpbitRestError, upbit_rest_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)

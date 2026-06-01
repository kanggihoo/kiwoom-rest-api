from fastapi import FastAPI, Request

from upbit_dashboard.api.errors import DashboardApiError, make_error_response


async def dashboard_api_error_handler(_: Request, exc: DashboardApiError):
    return make_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DashboardApiError, dashboard_api_error_handler)

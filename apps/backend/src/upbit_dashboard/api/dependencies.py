from typing import Annotated

from fastapi import Depends, Request

from upbit_dashboard.api.queries.quotation import QuotationReadService


def get_quotation_read_service(request: Request) -> QuotationReadService:
    return request.app.state.quotation_read_service


QuotationReadServiceDependency = Annotated[
    QuotationReadService,
    Depends(get_quotation_read_service),
]

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Query

from upbit_dashboard.api.dependencies import QuotationReadServiceDependency
from upbit_dashboard.contracts.quotation import CandleUnit
from upbit_dashboard.contracts.rest import CandlesListResponse

router = APIRouter(prefix="/candles", tags=["candles"])
CandleToQuery = Annotated[
    str | None,
    Query(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?$",
        description="조회 기준 시각. 예: 2026-06-01T00:00:00Z.",
    ),
]


@router.get("", response_model=CandlesListResponse)
async def get_candles(
    quotation_read_service: QuotationReadServiceDependency,
    market: str,
    unit: CandleUnit,
    count: Annotated[int, Query(ge=1, le=200)] = 200,
    to: CandleToQuery = None,
) -> CandlesListResponse:
    data = await quotation_read_service.list_candles(
        market=market,
        unit=unit,
        count=count,
        to=to,
    )
    return CandlesListResponse(
        timestamp=datetime.now(timezone.utc),
        data=data,
    )

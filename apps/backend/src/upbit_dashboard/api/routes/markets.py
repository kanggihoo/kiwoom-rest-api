from datetime import datetime, timezone

from fastapi import APIRouter

from upbit_dashboard.api.dependencies import QuotationReadServiceDependency
from upbit_dashboard.contracts.rest import MarketsListResponse

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=MarketsListResponse)
async def get_markets(quotation_read_service: QuotationReadServiceDependency) -> MarketsListResponse:
    data = await quotation_read_service.list_markets()
    return MarketsListResponse(
        timestamp=datetime.now(timezone.utc),
        data=data,
    )

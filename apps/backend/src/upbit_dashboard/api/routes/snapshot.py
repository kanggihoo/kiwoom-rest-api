from datetime import datetime, timezone

from fastapi import APIRouter

from upbit_dashboard.api.dependencies import QuotationReadServiceDependency
from upbit_dashboard.contracts.rest import MarketStateSnapshotResponse

router = APIRouter(prefix="/snapshot", tags=["snapshot"])


@router.get("", response_model=MarketStateSnapshotResponse)
def get_snapshot(quotation_read_service: QuotationReadServiceDependency) -> MarketStateSnapshotResponse:
    data = quotation_read_service.get_snapshot()
    return MarketStateSnapshotResponse(
        timestamp=data.generated_at,
        data=data,
    )

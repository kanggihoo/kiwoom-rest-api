from datetime import datetime, timezone

from fastapi import APIRouter, Request

from upbit_dashboard.contracts.rest import (
    MarketStateSnapshotData,
    MarketStateSnapshotResponse,
)
from upbit_dashboard.state.market_state import MarketState

router = APIRouter()


@router.get("/api/snapshot", response_model=MarketStateSnapshotResponse)
def get_snapshot(request: Request) -> MarketStateSnapshotResponse:
    market_state: MarketState = request.app.state.market_state
    snapshot = market_state.snapshot()
    return MarketStateSnapshotResponse(
        timestamp=snapshot.generated_at,
        data=MarketStateSnapshotData(
            generated_at=snapshot.generated_at,
            tickers=list(snapshot.tickers),
        ),
    )

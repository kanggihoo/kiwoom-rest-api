"""실시간 이벤트 응답 계약.

서버가 WebSocket/SSE 등으로 내보내는 이벤트 타입과 payload 형식을 고정한다.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from upbit_dashboard.contracts import quotation


class RealtimeCandleUnit(StrEnum):
    # 실시간 업데이트에서 허용되는 캔들 주기만 명시
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"


class AlertKind(StrEnum):
    # 알림 규칙 이름. UI 라우팅/필터링용.
    DAILY_RISE = "dailyRise"
    DAILY_DROP = "dailyDrop"
    SHORT_TERM_RISE = "shortTermRise"
    SHORT_TERM_DROP = "shortTermDrop"


class Severity(StrEnum):
    # 알림 표시 레벨
    INFO = "info"
    WARNING = "warning"


class CandleUpdateData(BaseModel):
    # 실시간 캔들 업데이트 payload
    market: str = Field(description="Market 코드.")
    candle_unit: RealtimeCandleUnit = Field(
        serialization_alias="candleUnit", description="실시간 candle 단위. 1m, 5m, 15m, 30m, 1h만 허용."
    )
    candle: quotation.Candle = Field(description="OHLCV candle 값.")
    timestamp_ms: int = Field(
        serialization_alias="timestampMs", description="Upbit candle WebSocket timestamp."
    )
    stream_type: quotation.StreamType = Field(
        serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME."
    )


class AlertData(BaseModel):
    # 신규 알림 이벤트의 본문 모델
    id: str = Field(description="프론트 리스트 key와 중복 방지용 ID.")
    market: str = Field(description="Alert 대상 Market.")
    alert_kind: AlertKind = Field(serialization_alias="alertKind", description="Alert 종류.")
    title: str = Field(description="UI 표시 제목.")
    message: str = Field(description="UI 표시 메시지.")
    severity: Severity = Field(description="표시 심각도.")
    basis_rate: float = Field(serialization_alias="basisRate", description="Alert를 발생시킨 등락률.")
    basis_window: Literal["24h", "1m"] = Field(serialization_alias="basisWindow", description="Alert 계산 기준 구간.")
    created_at: datetime = Field(serialization_alias="createdAt", description="Alert 생성 시각.")


class TickerUpdateEvent(BaseModel):
    # 내부 상태의 ticker 갱신 이벤트
    type: Literal["ticker:update"] = Field(default="ticker:update", description="Ticker update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: quotation.TickerData = Field(description="Ticker update payload.")


class TradeUpdateEvent(BaseModel):
    # 실시간 체결 업데이트 이벤트
    type: Literal["trade:update"] = Field(default="trade:update", description="Trade update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: quotation.TradeData = Field(description="Trade update payload.")


class OrderbookUpdateEvent(BaseModel):
    # 실시간 호가 업데이트 이벤트
    type: Literal["orderbook:update"] = Field(default="orderbook:update", description="Orderbook update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: quotation.OrderbookData = Field(description="Orderbook update payload.")


class CandleUpdateEvent(BaseModel):
    # 실시간 캔들 업데이트 이벤트
    type: Literal["candle:update"] = Field(default="candle:update", description="Candle update event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: CandleUpdateData = Field(description="Candle update payload.")


class AlertNewEvent(BaseModel):
    # 새 알림 생성 이벤트
    type: Literal["alert:new"] = Field(default="alert:new", description="Alert new event type.")
    timestamp: datetime = Field(description="우리 서버가 이벤트를 만든 시각.")
    data: AlertData = Field(description="Alert payload.")

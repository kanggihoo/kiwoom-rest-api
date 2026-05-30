"""Upbit WebSocket 원시 메시지 계약.

아직 내부 계약으로 변환되기 전, 외부 수신 데이터 형식을 여기서 먼저 파싱/검증한다.
"""

from typing import Literal

from pydantic import BaseModel, Field


class UpbitTickerMessage(BaseModel):
    # Upbit이 보내는 ticker 이벤트 1종에 대한 최소 필수 스키마
    type: Literal["ticker"] = Field(description="Upbit WebSocket 데이터 항목. ticker.")
    code: str = Field(description="Upbit Market 코드. 예: KRW-BTC.")
    opening_price: float = Field(description="시가. Upbit ticker.opening_price.")
    high_price: float = Field(description="고가. Upbit ticker.high_price.")
    low_price: float = Field(description="저가. Upbit ticker.low_price.")
    trade_price: float = Field(description="현재가. Upbit ticker.trade_price.")
    signed_change_price: float = Field(description="전일 대비 가격 변동 값. Upbit ticker.signed_change_price.")
    signed_change_rate: float = Field(description="전일 대비 등락률. Upbit ticker.signed_change_rate.")
    trade_volume: float = Field(description="최근 거래량. Upbit ticker.trade_volume.")
    acc_trade_volume_24h: float = Field(description="최근 24시간 누적 거래량. Upbit ticker.acc_trade_volume_24h.")
    acc_trade_price_24h: float = Field(description="최근 24시간 누적 거래대금. Upbit ticker.acc_trade_price_24h.")
    trade_timestamp: int = Field(description="체결 타임스탬프(ms). Upbit ticker.trade_timestamp.")
    timestamp: int = Field(description="이벤트 타임스탬프(ms). Upbit ticker.timestamp.")
    stream_type: Literal["SNAPSHOT", "REALTIME"] = Field(description="Upbit stream_type.")

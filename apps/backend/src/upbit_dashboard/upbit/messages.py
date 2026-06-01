"""Upbit WebSocket raw message models.

These models validate external Upbit input before adapter code maps it into
browser-facing application quotation contracts.
"""

from typing import Literal

from pydantic import BaseModel, Field


class UpbitTickerMessage(BaseModel):
    # Minimal required schema for one Upbit ticker WebSocket event.
    type: Literal["ticker"] = Field(description="Upbit WebSocket data type. ticker.")
    code: str = Field(description="Upbit Market code. Example: KRW-BTC.")
    opening_price: float = Field(description="Opening price. Upbit ticker.opening_price.")
    high_price: float = Field(description="High price. Upbit ticker.high_price.")
    low_price: float = Field(description="Low price. Upbit ticker.low_price.")
    trade_price: float = Field(description="Current trade price. Upbit ticker.trade_price.")
    signed_change_price: float = Field(description="Signed daily change price. Upbit ticker.signed_change_price.")
    signed_change_rate: float = Field(description="Signed daily change rate. Upbit ticker.signed_change_rate.")
    trade_volume: float = Field(description="Latest trade volume. Upbit ticker.trade_volume.")
    acc_trade_volume_24h: float = Field(description="24h accumulated trade volume. Upbit ticker.acc_trade_volume_24h.")
    acc_trade_price_24h: float = Field(description="24h accumulated trade price. Upbit ticker.acc_trade_price_24h.")
    trade_timestamp: int = Field(description="Trade timestamp in milliseconds. Upbit ticker.trade_timestamp.")
    timestamp: int = Field(description="Event timestamp in milliseconds. Upbit ticker.timestamp.")
    stream_type: Literal["SNAPSHOT", "REALTIME"] = Field(description="Upbit stream_type.")

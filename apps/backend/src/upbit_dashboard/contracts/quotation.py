"""Upbit 시세/체결/호가 데이터 계약.

이 모듈은 내부 비즈니스에서 공통으로 쓰는 도메인 모델을 정의합니다.
각 모델은 Upbit 원시 데이터의 필드명을 API 정책에 맞춰 매핑해 사용합니다.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class StreamType(StrEnum):
    # 실시간 데이터는 스냅샷/실시간 상태로 구분된다.
    SNAPSHOT = "SNAPSHOT"
    REALTIME = "REALTIME"


class AskBid(StrEnum):
    # ASK/BID는 체결이 어느 쪽 주문 라인에서 발생했는지 나타낸다.
    ASK = "ASK"
    BID = "BID"


class CandleUnit(StrEnum):
    # 캔들 단위는 REST/일반 조회에서 통용되는 전체 집합이다.
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class TickerData(BaseModel):
    # 티커 상태 스냅샷/업데이트를 위한 핵심 가격·거래량 모델
    market: str = Field(description="Market 코드. Upbit ticker.code 기준.")
    opening_price: float = Field(
        serialization_alias="openingPrice", description="시가. Upbit ticker.opening_price 기준."
    )
    high_price: float = Field(
        serialization_alias="highPrice", description="고가. Upbit ticker.high_price 기준."
    )
    low_price: float = Field(
        serialization_alias="lowPrice", description="저가. Upbit ticker.low_price 기준."
    )
    trade_price: float = Field(
        serialization_alias="tradePrice", description="현재가. Upbit ticker.trade_price 기준."
    )
    signed_change_price: float = Field(
        serialization_alias="signedChangePrice",
        description="전일 대비 가격 변동 값. Upbit ticker.signed_change_price 기준.",
    )
    signed_change_rate: float = Field(
        serialization_alias="signedChangeRate",
        description="전일 대비 등락률. Upbit ticker.signed_change_rate 기준.",
    )
    trade_volume: float = Field(
        serialization_alias="tradeVolume", description="최근 거래량. Upbit ticker.trade_volume 기준."
    )
    acc_trade_volume_24h: float = Field(
        serialization_alias="accTradeVolume24h", description="최근 24시간 누적 거래량. Upbit ticker.acc_trade_volume_24h 기준."
    )
    acc_trade_price_24h: float = Field(
        serialization_alias="accTradePrice24h", description="최근 24시간 누적 거래대금. Upbit ticker.acc_trade_price_24h 기준."
    )
    trade_timestamp_ms: int = Field(
        serialization_alias="tradeTimestampMs",
        description="체결 타임스탬프(ms). Upbit ticker.trade_timestamp 기준.",
    )
    timestamp_ms: int = Field(
        serialization_alias="timestampMs", description="Upbit 이벤트 타임스탬프(ms). Upbit ticker.timestamp 기준."
    )
    stream_type: StreamType = Field(
        serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME."
    )


class TradeData(BaseModel):
    # 체결 1건의 정규화된 형태
    market: str = Field(description="Market 코드. Upbit trade.code 기준.")
    trade_price: float = Field(
        serialization_alias="tradePrice", description="체결 가격. Upbit trade.trade_price 기준."
    )
    trade_volume: float = Field(
        serialization_alias="tradeVolume", description="체결량. Upbit trade.trade_volume 기준."
    )
    ask_bid: AskBid = Field(
        serialization_alias="askBid", description="매수/매도 구분. Upbit trade.ask_bid 기준."
    )
    trade_timestamp_ms: int = Field(
        serialization_alias="tradeTimestampMs",
        description="체결 타임스탬프(ms). Upbit trade.trade_timestamp 기준.",
    )
    sequential_id: int = Field(
        serialization_alias="sequentialId", description="체결 번호. Upbit trade.sequential_id 기준."
    )
    timestamp_ms: int = Field(
        serialization_alias="timestampMs", description="Upbit 이벤트 타임스탬프(ms). Upbit trade.timestamp 기준."
    )
    stream_type: StreamType = Field(
        serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME."
    )


class OrderbookUnit(BaseModel):
    # 호가 1단위의 가격/수량 페어
    ask_price: float = Field(serialization_alias="askPrice", description="매도 호가. Upbit orderbook_units.ask_price 기준.")
    bid_price: float = Field(serialization_alias="bidPrice", description="매수 호가. Upbit orderbook_units.bid_price 기준.")
    ask_size: float = Field(serialization_alias="askSize", description="매도 잔량. Upbit orderbook_units.ask_size 기준.")
    bid_size: float = Field(serialization_alias="bidSize", description="매수 잔량. Upbit orderbook_units.bid_size 기준.")


class OrderbookData(BaseModel):
    # 호가창 전체 요약 + 레벨 단위 호가 목록
    market: str = Field(description="Market 코드. Upbit orderbook.code 기준.")
    total_ask_size: float = Field(
        serialization_alias="totalAskSize", description="매도 총 잔량. Upbit orderbook.total_ask_size 기준."
    )
    total_bid_size: float = Field(
        serialization_alias="totalBidSize", description="매수 총 잔량. Upbit orderbook.total_bid_size 기준."
    )
    level: float = Field(description="호가 모아보기 단위. Upbit orderbook.level 기준.")
    units: list[OrderbookUnit] = Field(description="호가 목록. Upbit orderbook.orderbook_units 기준.")
    timestamp_ms: int = Field(
        serialization_alias="timestampMs", description="Upbit 이벤트 타임스탬프(ms). Upbit orderbook.timestamp 기준."
    )
    stream_type: StreamType = Field(
        serialization_alias="streamType", description="Upbit stream_type. SNAPSHOT 또는 REALTIME."
    )


class Candle(BaseModel):
    # 기간봉(OHLCV) 정규화 모델, 정렬이나 구간 계산의 기본 단위로 사용
    candle_date_time_utc: str = Field(
        serialization_alias="candleDateTimeUtc", description="캔들 기준 시각 UTC. Upbit candle.candle_date_time_utc 기준."
    )
    candle_date_time_kst: str = Field(
        serialization_alias="candleDateTimeKst", description="캔들 기준 시각 KST. Upbit candle.candle_date_time_kst 기준."
    )
    opening_price: float = Field(
        serialization_alias="openingPrice", description="시가. Upbit candle.opening_price 기준."
    )
    high_price: float = Field(
        serialization_alias="highPrice", description="고가. Upbit candle.high_price 기준."
    )
    low_price: float = Field(
        serialization_alias="lowPrice", description="저가. Upbit candle.low_price 기준."
    )
    trade_price: float = Field(
        serialization_alias="tradePrice", description="종가. Upbit candle.trade_price 기준."
    )
    candle_acc_trade_volume: float = Field(
        serialization_alias="candleAccTradeVolume", description="누적 거래량. Upbit candle.candle_acc_trade_volume 기준."
    )
    candle_acc_trade_price: float = Field(
        serialization_alias="candleAccTradePrice", description="누적 거래금액. Upbit candle.candle_acc_trade_price 기준."
    )

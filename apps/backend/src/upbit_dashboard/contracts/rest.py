from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from upbit_dashboard.contracts.quotation import Candle, CandleUnit, TickerData


class MarketSummary(BaseModel):
    market: str = Field(description="Upbit Market 코드. 예: KRW-BTC.")
    korean_name: str = Field(serialization_alias="koreanName", description="한글 Market 이름.")
    english_name: str = Field(serialization_alias="englishName", description="영문 Market 이름.")
    quote_currency: str = Field(serialization_alias="quoteCurrency", description="기준 통화. 예: KRW.")
    base_currency: str = Field(serialization_alias="baseCurrency", description="대상 자산. 예: BTC.")


class MarketsListData(BaseModel):
    markets: list[MarketSummary] = Field(description="Market 메타데이터 목록.")


class MarketsListResponse(BaseModel):
    type: Literal["markets:list"] = Field(
        default="markets:list",
        description="Market metadata list response type.",
    )
    timestamp: datetime = Field(description="우리 서버가 응답을 만든 시각.")
    data: MarketsListData = Field(description="Market metadata list payload.")


class MarketStateSnapshotData(BaseModel):
    generated_at: datetime = Field(
        serialization_alias="generatedAt",
        description="백엔드 MarketState snapshot 생성 시각.",
    )
    tickers: list[TickerData] = Field(description="최신 ticker 목록. ticker:update.data와 같은 구조.")


class MarketStateSnapshotResponse(BaseModel):
    type: Literal["market-state:snapshot"] = Field(
        default="market-state:snapshot",
        description="MarketState snapshot response type.",
    )
    timestamp: datetime = Field(description="우리 서버가 응답을 만든 시각.")
    data: MarketStateSnapshotData = Field(description="MarketState snapshot payload.")


class CandlesListData(BaseModel):
    market: str = Field(description="Market 코드.")
    candle_unit: CandleUnit = Field(
        serialization_alias="candleUnit",
        description="앱 candle 단위.",
    )
    candles: list[Candle] = Field(description="candleDateTimeUtc 오름차순 candle 목록.")


class CandlesListResponse(BaseModel):
    type: Literal["candles:list"] = Field(
        default="candles:list",
        description="Candles list response type.",
    )
    timestamp: datetime = Field(description="우리 서버가 응답을 만든 시각.")
    data: CandlesListData = Field(description="Candles list payload.")

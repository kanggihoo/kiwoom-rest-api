import re

from dataclasses import dataclass


MARKET_CODE_PATTERN = re.compile(r"^[A-Z0-9-]+-[A-Z0-9]+$")


@dataclass(frozen=True)
class MarketCode:
    quote_currency: str
    base_currency: str

    def as_upbit_code(self) -> str:
        return f"{self.quote_currency}-{self.base_currency}"


def normalize_market_code(raw_market: str) -> str:
    market = (raw_market or "").strip().upper()
    if not market:
        raise ValueError("Market 코드가 비어 있습니다.")
    return market


def parse_market_code(raw_market: str) -> MarketCode:
    normalized = normalize_market_code(raw_market)
    if not MARKET_CODE_PATTERN.fullmatch(normalized):
        raise ValueError(f"지원하지 않는 Market 코드 형식입니다: {normalized}")

    quote_currency, base_currency = normalized.split("-", 1)
    if not quote_currency or not base_currency:
        raise ValueError(f"지원하지 않는 Market 코드 형식입니다: {normalized}")

    return MarketCode(quote_currency=quote_currency, base_currency=base_currency)


def is_krw_market(raw_market: str) -> bool:
    return parse_market_code(raw_market).quote_currency == "KRW"


def assert_krw_market(raw_market: str) -> MarketCode:
    market = parse_market_code(raw_market)
    if market.quote_currency != "KRW":
        raise ValueError(f"KRW 마켓이 아닙니다: {market.as_upbit_code()}")
    return market

from upbit_dashboard.contracts.quotation import StreamType, TickerData
from upbit_dashboard.contracts.upbit import UpbitTickerMessage


def map_upbit_ticker_message(message: UpbitTickerMessage) -> TickerData:
    return TickerData(
        market=message.code,
        opening_price=message.opening_price,
        high_price=message.high_price,
        low_price=message.low_price,
        trade_price=message.trade_price,
        signed_change_price=message.signed_change_price,
        signed_change_rate=message.signed_change_rate,
        trade_volume=message.trade_volume,
        acc_trade_volume_24h=message.acc_trade_volume_24h,
        acc_trade_price_24h=message.acc_trade_price_24h,
        trade_timestamp_ms=message.trade_timestamp,
        timestamp_ms=message.timestamp,
        stream_type=StreamType(message.stream_type),
    )

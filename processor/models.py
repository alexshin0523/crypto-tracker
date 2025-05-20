from dataclasses import dataclass

@dataclass
class Trade:
    symbol: str
    price: float
    size: float
    event_ts: int            # epoch-ms

@dataclass
class Candle:
    symbol: str
    interval: str            # e.g. "1m"
    window_start: int
    window_end: int
    open: float
    high: float
    low: float
    close: float
    volume: float


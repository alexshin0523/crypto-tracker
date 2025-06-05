from dataclasses import dataclass, asdict
import json

@dataclass
class Trade:
    symbol: str
    price: float
    size: float
    event_ts: int

@dataclass
class Candle:
    symbol: str
    interval: str
    window_start: int
    window_end: int
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class CandleRecord:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_json(self) -> str:
        return json.dumps(asdict(self))
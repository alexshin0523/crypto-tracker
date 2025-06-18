from dataclasses import dataclass, asdict
import json, math

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

    def to_json(self) -> str:
        return json.dumps(asdict(self))

@dataclass
class CandleAccumulator:
    open:   float = None
    high:   float = -math.inf
    low:    float = math.inf
    close:  float = None
    volume: float = 0.0
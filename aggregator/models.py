from faust import Record

class Trade(Record, serializer='json'):
    # fields match the Kafka message fields for trades.<symbol>
    e: str      # event type
    E: int      # event time (ms)
    s: str      # symbol, e.g. "BTCUSDT"
    p: float    # price
    q: float    # quantity
    T: int      # trade execution time (ms)

class Candle(Record, serializer='json'):
    symbol: str
    interval: str            # "1s"
    window_start: int        # epoch ms
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: int
    proc_latency_ms: float   # processing delay
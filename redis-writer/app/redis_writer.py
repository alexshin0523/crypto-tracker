from redis import Redis
from redistimeseries.client import Client as RedisTimeSeries
from config import INTERVAL_TO_MS, RETENTION_CANDLES

def get_ts_client(host, port):
    redis_conn = Redis(host=host, port=port, db=0)
    return RedisTimeSeries(conn=redis_conn)

def write_candle_to_redis(ts, candle):
    symbol = candle['symbol']
    interval = candle['interval']
    timestamp = int(candle['window_start'])
    key_prefix = f"ohlcv:{symbol}:{interval}"
    retention = get_retention_ms(interval)

    for field in ['open', 'high', 'low', 'close', 'volume']:
        ts_key = f"{key_prefix}:{field}"
        ts.add(ts_key, timestamp, candle[field], retention_msecs=retention)

def get_retention_ms(interval: str) -> int:
    return INTERVAL_TO_MS.get(interval) * RETENTION_CANDLES

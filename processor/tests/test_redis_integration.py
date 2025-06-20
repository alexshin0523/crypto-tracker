import os
import json
import pytest
import redis
from processor.sinks.redis_sink import RedisCandleSink
from processor.models import Candle

@pytest.fixture(scope="module")
def real_redis():
    url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    client = redis.from_url(url)
    client.flushdb()
    yield client
    client.flushdb()
    client.close()

def test_redis_sink_against_real_redis(real_redis):
    sink = RedisCandleSink(redis_url=os.getenv("REDIS_URL"), history_size=3)
    sink.open(None)

    candle = Candle("ETH-USD", "5m", 0, 300000, 2000.0, 2100.0, 1950.0, 2050.0, 5.0)
    sink.invoke(candle.to_json(), None)

    # verify ZSET
    key_hist = f"candles:{candle.interval}:{candle.symbol}"
    members = real_redis.zrange(key_hist, 0, -1)
    assert json.loads(members[0]) == json.loads(candle.to_json())

    # verify HASH
    key_curr = f"candles:current:{candle.interval}:{candle.symbol}"
    stored = real_redis.hgetall(key_curr)
    assert stored[b"open"] == b"2000.0"

    sink.close()

import json
import time
import pytest
import fakeredis
from processor.sinks.redis_sink import RedisCandleSink
from processor.models import Candle

@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Replace redis.ConnectionPool.from_url → real FakeRedis instance."""
    fake = fakeredis.FakeRedis()
    # pool isn’t really used by FakeRedis, so we just return None
    monkeypatch.setattr("redis.ConnectionPool.from_url", lambda url: None)
    monkeypatch.setattr("redis.Redis", lambda connection_pool=None: fake)
    return fake

def make_sample_candle():
    now = int(time.time() * 1000)
    return Candle(
        symbol="BTCUSDT",
        interval="1m",
        window_start=now - 60_000,
        window_end=now,
        open=50000.0,
        high=50500.0,
        low=49900.0,
        close=50200.0,
        volume=12.34,
    )

def test_redis_candle_sink_writes_history_and_current(fake_redis):
    sink = RedisCandleSink(redis_url="redis://doesnt:matter", history_size=2)
    # Simulate Flink lifecycle
    sink.open(runtime_context=None)

    candle = make_sample_candle()
    json_str = candle.to_json()

    # invoke once
    sink.invoke(json_str, context=None)
    # now we should have one member in the ZSET
    key_hist = f"candles:{candle.interval}:{candle.symbol}"
    assert fake_redis.zcard(key_hist) == 1
    # the stored member (as bytes) should equal our JSON
    members = fake_redis.zrange(key_hist, 0, -1)
    assert members == [json_str.encode()]

    # and the hash for the current candle
    key_curr = f"candles:current:{candle.interval}:{candle.symbol}"
    data = fake_redis.hgetall(key_curr)
    # All fields should round-trip
    for field in ("open", "high", "low", "close", "volume", "window_start", "window_end"):
        assert field.encode() in data

    # Test trimming behavior: write a second candle and a third, ensure oldest is dropped
    candle2 = make_sample_candle()
    sink.invoke(candle2.to_json(), context=None)
    candle3 = make_sample_candle()
    sink.invoke(candle3.to_json(), context=None)
    # history_size=2, so only 2 remain
    assert fake_redis.zcard(key_hist) == 2

    sink.close()


# import json
# import pytest
# from unittest.mock import MagicMock, patch
# from processor.sinks.redis_sink import RedisCandleSink
# from processor.models import Candle
#
# @pytest.fixture(autouse=True)
# def fake_redis(monkeypatch):
#     fake = MagicMock()
#     monkeypatch.setattr('redis.ConnectionPool.from_url', lambda url: None)
#     monkeypatch.setattr('redis.Redis', lambda connection_pool=None: fake)
#     return fake
#
#
# def make_candle():
#     return Candle('BTC', '1m', 0, 60_000, 100, 110, 90, 105, 5)
#
#
# def test_redis_sink_invocations(fake_redis):
#     sink = RedisCandleSink(redis_url='redis://x', history_size=2)
#     sink.open(None)
#     c = make_candle()
#     js = c.to_json()
#     sink.invoke(js, None)
#     # history ZADD and trim
#     zkey = f'candles:{c.interval}:{c.symbol}'
#     fake_redis.zadd.assert_called_once_with(zkey, {js: c.window_start})
#     fake_redis.zremrangebyrank.assert_called_once()
#     # current HSET
#     hkey = f'candles:current:{c.interval}:{c.symbol}'
#     fake_redis.hset.assert_called_once()
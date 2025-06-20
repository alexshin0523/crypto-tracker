import pytest
from processor.sources import create_trade_consumer
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from processor.config import KAFKA_BOOTSTRAP


def test_create_trade_consumer_defaults():
    consumer = create_trade_consumer(['t1', 't2'])
    assert isinstance(consumer, FlinkKafkaConsumer)
    props = consumer.properties
    assert props['bootstrap.servers'] == KAFKA_BOOTSTRAP
    assert props['group.id'] == 'processor'
    assert props['auto.offset.reset'] == 'earliest'
    assert consumer.topics == ['t1', 't2']


# File: processor/tests/test_aggregates.py
import pytest
from processor.transforms.window_functions import OHLCVAggregateFunction
from processor.models import CandleAccumulator, Trade


def make_trade(price, size):
    return Trade(symbol='Z', price=price, size=size, event_ts=0)


def test_aggregate_accumulator():
    agg = OHLCVAggregateFunction()
    acc = agg.create_accumulator()
    assert isinstance(acc, CandleAccumulator)
    # add two trades
    acc = agg.add(make_trade(5,1), acc)
    acc = agg.add(make_trade(10,2), acc)
    assert acc.open == 5
    assert acc.high == 10
    assert acc.low == 5
    assert acc.close == 10
    assert acc.volume == pytest.approx(3)


def test_aggregate_merge():
    agg = OHLCVAggregateFunction()
    a = agg.add(make_trade(2,1), agg.create_accumulator())
    b = agg.add(make_trade(8,3), agg.create_accumulator())
    merged = agg.merge(a, b)
    assert merged.open == 2
    assert merged.close == 8
    assert merged.high == 8
    assert merged.volume == pytest.approx(4)
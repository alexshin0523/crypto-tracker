import pytest
from processor.sinks.kafka_sink import create_kafka_candle_sink
from pyflink.datastream.connectors.kafka import FlinkKafkaProducer


def test_create_kafka_candle_sink():
    sink = create_kafka_candle_sink('1m')
    assert isinstance(sink, FlinkKafkaProducer)
    assert sink._topic == 'candles.1m'


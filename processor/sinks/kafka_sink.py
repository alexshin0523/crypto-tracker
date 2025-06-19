from pyflink.datastream.connectors.kafka import FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from ..config import KAFKA_BOOTSTRAP

def create_kafka_candle_sink(interval: str) -> FlinkKafkaProducer:
    topic = f"candles.{interval}"
    print(f"Setting up {interval} -> {topic}")
    props = {"bootstrap.servers": KAFKA_BOOTSTRAP}
    print(f"Creating Flink Kafka producer for {topic}")
    return FlinkKafkaProducer(
        topic=topic,
        serialization_schema=SimpleStringSchema(),
        producer_config=props,
    )
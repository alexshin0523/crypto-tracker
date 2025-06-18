from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic
from pyflink.common import Duration, Types, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.time import Time
from .config import KAFKA_BOOTSTRAP, MAX_OUT_OF_ORDER_MS
from .deserializer import json_to_trade
from .timestampers import TradeTimestampAssigner
from .window_functions import OHLCVWindowFunction, OHLCVAggregateFunction
from .schema import CANDLE_TYPE, row_to_candle
import time
import multiprocessing

DESIRED_PARTITIONS = 1

WINDOW_CONFIGS = [
    ("1s", 1_000),
    ("1m", 60_000),
    ("1h", 3_600_000),
]

def build(env: StreamExecutionEnvironment):
    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    topics_list = None
    while not topics_list:
        print("grabbing topics list...")
        topics_list  = admin.list_topics(timeout=5).topics
        if not topics_list:
            time.sleep(.2)

    trade_topics = [name for name in topics_list if name.startswith("trades.")]
    print(trade_topics)

    for interval, _ in WINDOW_CONFIGS:
        topic = f"candles.{interval}"
        if topic not in topics_list:
            new_topic = NewTopic(topic, num_partitions=DESIRED_PARTITIONS, replication_factor=1)
            admin.create_topics([new_topic]).get(topic).result()

    env.set_parallelism(DESIRED_PARTITIONS)

    print("Creating Flink Kafka consumer...")
    consumer_props = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": "processor",
        "auto.offset.reset": "earliest",
    }
    consumer = FlinkKafkaConsumer(
        topics=trade_topics,
        deserialization_schema=SimpleStringSchema(),  # raw JSON
        properties=consumer_props,
    )

    base_ds = (
        env
        .add_source(consumer)
        .map(json_to_trade, output_type=Types.PICKLED_BYTE_ARRAY())
        .assign_timestamps_and_watermarks(
            WatermarkStrategy
            .for_bounded_out_of_orderness(Duration.of_millis(MAX_OUT_OF_ORDER_MS))
            .with_timestamp_assigner(TradeTimestampAssigner())
        )
        .key_by(lambda t: t.symbol)
    )

    for interval, window_ms in WINDOW_CONFIGS:
        topic = f"candles.{interval}"
        print(f"Setting up {interval} -> {topic}")
        if topic not in admin.list_topics(timeout=5).topics:
            admin.create_topics([NewTopic(topic, DESIRED_PARTITIONS, 1)]).get(topic).result()

        print(f"Creating Flink Kafka producer for {topic}")
        producer = FlinkKafkaProducer(
            topic=topic,
            serialization_schema=SimpleStringSchema(),
            producer_config={"bootstrap.servers": KAFKA_BOOTSTRAP},
        )

        print(f"Creating Flink DataStream for {topic}")
        (
            base_ds
            .window(TumblingEventTimeWindows.of(Time(window_ms)))
            .aggregate(
                OHLCVAggregateFunction(),
                OHLCVWindowFunction(interval),
                output_type=CANDLE_TYPE
            )
            .map(row_to_candle, output_type=Types.STRING())
            .add_sink(producer)
        )






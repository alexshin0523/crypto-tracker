from confluent_kafka.admin import AdminClient
from pyflink.common import Duration, Types, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common.time import Time

from .sinks.kafka_sink import create_kafka_candle_sink
from .topics import create_interval_topics, discover_topics
from .transforms.deserializer import json_to_trade
from .timestampers import TradeTimestampAssigner
from .transforms.window_functions import OHLCVWindowFunction, OHLCVAggregateFunction
from .schema import CANDLE_TYPE, row_to_candle
from .config import KAFKA_BOOTSTRAP, MAX_OUT_OF_ORDER_MS, WINDOW_CONFIGS
from .sources import create_trade_consumer
from .sinks.redis_sink import RedisConfig, RedisSinkFactory


def build(env: StreamExecutionEnvironment):
    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    topics_dict = discover_topics(admin)

    create_interval_topics(admin, topics_dict)

    print("Creating Flink Kafka consumer...")
    trade_topics = [name for name in topics_dict if name.startswith("trades.")]
    consumer = create_trade_consumer(trade_topics)

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

    redis_cfg = RedisConfig()
    redis_sink = RedisSinkFactory(redis_cfg).create_redis_sink()

    for interval, window_ms in WINDOW_CONFIGS:
        producer = create_kafka_candle_sink(interval)


        print(f"Setting up Flink DataStream for candles.{interval}")
        window_ds = (
            base_ds
            .window(TumblingEventTimeWindows.of(Time(window_ms)))
            .aggregate(
                OHLCVAggregateFunction(),
                OHLCVWindowFunction(interval),
                output_type=CANDLE_TYPE
            )
            .map(row_to_candle, output_type=Types.STRING())
            .add_sink(producer)
            .add_sink(redis_sink)
        )
        window_ds.add_sink(producer)
        window_ds.add_sink(redis_sink)






KAFKA_BOOTSTRAP = 'kafka:9092'
GROUP_ID = 'redis-writer'
REDIS_HOST = 'redis'
REDIS_PORT = 6379
INTERVAL_TO_MS = {
    "1s": 1000,
    "1m": 60_000,
    "1h": 3_600_000,
}

RETENTION_CANDLES = 150

import os, multiprocessing

# ---- Kafka connection ----------------------------------------
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

# ---- Event-time handling -------------------------------------
# How much lateness we allow each trade to have, in milliseconds
MAX_OUT_OF_ORDER_MS: int = int(os.getenv("MAX_OUT_OF_ORDER_MS", "100"))

# ---- Candle parameters ---------------------------------------
WINDOW_SECONDS: int = int(os.getenv("WINDOW_SECONDS", "60"))

# ---- State backend path (must match docker-compose volume) ----
STATE_DIR: str = os.getenv("STATE_DIR", "file:///state-backend")

DESIRED_PARTITIONS = int(os.getenv("PARTITIONS", "4"))

WINDOW_CONFIGS = [
    ("1s", 1_000),
    ("1m", 60_000),
    ("1h", 3_600_000),
]

# Convenience helper for converting Durations if you need it later
def seconds(n: int) -> int:
    """Return milliseconds for n seconds (Flink Duration helper)."""
    return n * 1000
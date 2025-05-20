FROM python:3.10-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        curl \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

# install Poetry
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --no-interaction --no-ansi

COPY . /app/processor

ARG KAFKA_SQL_CONN_VER=3.0.2-1.18
RUN mkdir -p /app/jars \
 && curl -fsSL \
      https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/${KAFKA_SQL_CONN_VER}/flink-sql-connector-kafka-${KAFKA_SQL_CONN_VER}.jar \
      -o /app/jars/flink-sql-connector-kafka-${KAFKA_SQL_CONN_VER}.jar

ENV CONNECTOR_JAR=/app/jars/flink-sql-connector-kafka-${KAFKA_SQL_CONN_VER}.jar

# create state dir for RocksDB backend
RUN mkdir -p /state-backend
VOLUME ["/state-backend"]

ENTRYPOINT ["poetry", "run", "python", "-m", "processor.main"]

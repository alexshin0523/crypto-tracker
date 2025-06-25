FROM maven:3.8.3-openjdk-17-slim AS builder

WORKDIR /build
COPY processor/redis-kafka-connectors/pom.xml ./

RUN mvn dependency:go-offline -q -e

RUN mvn package -DskipTests -q


FROM flink:1.18-scala_2.12

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3.10 python3-pip python3-venv zip openjdk-17-jdk \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --no-cache-dir poetry==1.8.2 confluent-kafka==2.2.0 protobuf==4.23.4 \
 && ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY processor/pyproject.toml processor/poetry.lock* /app/
RUN poetry install --no-root --no-interaction --no-ansi

COPY processor /app/processor

RUN cd /app && zip -r processor.zip processor

COPY --from=builder /build/target/flink-connectors-1.0.0-fat.jar /app/jars/connectors-fat.jar

# create state dir for RocksDB backend
RUN mkdir -p /state-backend
VOLUME ["/state-backend"]

USER flink
ENTRYPOINT ["bash","-c","\
  /opt/flink/bin/flink run \
    --jobmanager jobmanager:8081 \
    --pyModule processor.main \
    --pyFiles /app/processor.zip \
    --pyRequirements /app/processor/requirements.txt \
    --pyClientExecutable /usr/bin/python3 \
    --jarfile /app/jars/connectors-fat.jar \
    --detached \
"]
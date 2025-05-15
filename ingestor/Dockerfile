FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY binance_ingestor.py verify_topics.py ./


CMD ["python", "binance_ingestor.py"]
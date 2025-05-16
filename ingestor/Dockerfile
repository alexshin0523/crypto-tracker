FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p ingestor/utils
COPY binance_ingestor.py ./ingestor/
COPY utils/verify_topics.py ./ingestor/utils
RUN touch ingestor/__init__.py

CMD ["python", "-m", "ingestor.binance_ingestor"]
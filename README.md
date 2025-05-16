# crypto-tracker
A real-time “Crypto-Ticker” service that streams Binance trades, aggregates sub-second OHLCV candles through Kafka + Faust, and serves live data via a FastAPI WebSocket/REST API with auto-scaling on Kubernetes.


# Testing Kafka Topics
To check active topics, run 

```docker exec ingestor python ingestor/utils/verify_topics.py```


THEN if you want to spin up temporary consumer to read messages from all topics, run

```docker run --network=host edenhill/kcat:1.7.1 -C -b localhost:19092 -t trades.BTCUSDT -o beginning -e```

pyt

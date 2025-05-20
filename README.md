# Crypto-Tracker
Crypto-Tracker is an open-source, real-time streaming analytics platform for cryptocurrency markets. It ingests live trade data from exchange WebSockets into Kafka, processes it with PyFlink to generate OHLCV candles and advanced technical indicators (RSI, MACD, Bollinger Bands, etc.), and exposes a REST / WebSocket API. A React-based frontend lets users track any coins, build custom watchlists, and explore interactive candlestick charts and metrics. Designed in Python for modularity and horizontal scalability, Crypto-Ticker aims to evolve into a full-featured web app for on-the-fly crypto insights.


# Testing Kafka Topics
To check active topics, run 

```docker exec ingestor python ingestor/utils/verify_topics.py```


THEN if you want to spin up temporary consumer to read messages from a topic, run

```docker run --network=host edenhill/kcat:1.7.1 -C -b localhost:19092 -t {topic_name} -o beginning -e```

pyt

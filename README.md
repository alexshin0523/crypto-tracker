# crypto-tracker
A real-time “Crypto-Ticker” service that streams Binance trades, aggregates sub-second OHLCV candles through Kafka + Faust, and serves live data via a FastAPI WebSocket/REST API with auto-scaling on Kubernetes.

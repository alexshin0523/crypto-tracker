FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Create aggregator package directory
RUN mkdir -p aggregator
COPY main.py models.py ./aggregator/
# Create an __init__.py to make it a proper package
RUN touch aggregator/__init__.py

CMD ["faust", "-A", "aggregator.main", "worker", "-l", "info"]

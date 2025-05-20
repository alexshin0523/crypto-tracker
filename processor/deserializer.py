import json
from typing import Any
from .models import Trade

def json_to_trade(value: str) -> Trade:
    data = json.loads(value)

    # extract only the fields we need, converting types as required
    return Trade(
        symbol   = data["s"],                     # e.g. "BTCUSDT"
        price    = float(data["p"]),              # price comes as a string
        size     = float(data["q"]),              # quantity as a string
        event_ts = int(data["E"]),                # epoch-ms timestamp
    )
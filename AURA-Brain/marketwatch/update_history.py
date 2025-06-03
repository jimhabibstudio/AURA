# marketwatch/update_history.py
# Syncs daily live material prices into historical_prices.json

import json
import os
from datetime import datetime
from marketwatch_scraper import MarketDataFetcher

HISTORICAL_PATH = "marketwatch/historical_prices.json"

def load_history():
    if not os.path.exists(HISTORICAL_PATH):
        return {}
    with open(HISTORICAL_PATH, "r") as f:
        return json.load(f)

def save_history(data):
    with open(HISTORICAL_PATH, "w") as f:
        json.dump(data, f, indent=2)

def append_to_history(new_data):
    history = load_history()
    timestamp = new_data.pop("timestamp")

    for material, price in new_data.items():
        if price is None:
            continue  # skip invalid values
        if material not in history:
            history[material] = []
        history[material].append({
            "timestamp": timestamp,
            "price": price
        })

    save_history(history)

if __name__ == "__main__":
    fetcher = MarketDataFetcher()
    latest_prices = fetcher.get_all_prices()
    print("📦 Saving new prices to history:")
    print(latest_prices)
    append_to_history(latest_prices)

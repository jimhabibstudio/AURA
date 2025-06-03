# marketwatch/price_trend_forecaster.py
# Predicts future material prices using linear regression (Tesla+SpaceX-level foresight)

import json
import os
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Optional


DATA_FILE = "marketwatch/historical_prices.json"


class PriceTrendForecaster:
    def __init__(self, data_path: str = DATA_FILE):
        self.data_path = data_path
        self.model_cache = {}

    def load_historical_data(self) -> Dict[str, List[Dict[str, float]]]:
        """Load historical material price data from local JSON file."""
        if not os.path.exists(self.data_path):
            return {}
        with open(self.data_path, "r") as f:
            return json.load(f)

    def forecast_material(self, material: str, days_ahead: int = 30) -> Optional[float]:
        """Forecast price for a material using linear regression."""
        history = self.load_historical_data().get(material, [])
        if len(history) < 5:
            return None  # Not enough data to predict

        # Prepare training data
        X = []
        y = []
        for i, entry in enumerate(history):
            date_obj = datetime.fromisoformat(entry['timestamp'])
            days_since = (date_obj - datetime.fromisoformat(history[0]['timestamp'])).days
            X.append([days_since])
            y.append(entry['price'])

        model = LinearRegression().fit(X, y)
        self.model_cache[material] = model

        future_day = X[-1][0] + days_ahead
        future_price = model.predict([[future_day]])
        return round(float(future_price[0]), 2)

    def forecast_all(self, days_ahead: int = 30) -> Dict[str, float]:
        """Forecast all materials."""
        history = self.load_historical_data()
        forecasts = {}
        for material in history.keys():
            prediction = self.forecast_material(material, days_ahead)
            if prediction:
                forecasts[material] = prediction
        return forecasts


if __name__ == "__main__":
    forecaster = PriceTrendForecaster()
    forecast = forecaster.forecast_all()
    print(f"📈 Forecasted Prices (30 days ahead):\n{json.dumps(forecast, indent=2)}")

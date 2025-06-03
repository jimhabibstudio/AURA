# marketwatch/regional_normalizer.py
# Normalizes prices by region, currency, and inflation (Tesla+SpaceX Scale)

import requests
import json
from typing import Dict
from forex_python.converter import CurrencyRates

class RegionalNormalizer:
    def __init__(self):
        self.currency_api = CurrencyRates()

        # Regional coefficients (example values, extend this from research)
        self.labor_multiplier = {
            "nigeria": 0.4,
            "usa": 1.0,
            "india": 0.35,
            "germany": 1.2,
            "brazil": 0.5
        }

        self.material_multiplier = {
            "nigeria": 0.9,
            "usa": 1.0,
            "india": 0.8,
            "germany": 1.1,
            "brazil": 0.85
        }

        self.local_currency = {
            "nigeria": "NGN",
            "usa": "USD",
            "india": "INR",
            "germany": "EUR",
            "brazil": "BRL"
        }

    def convert_currency(self, value_usd: float, target_currency: str) -> float:
        try:
            rate = self.currency_api.get_rate('USD', target_currency)
            return round(value_usd * rate, 2)
        except Exception as e:
            print(f"[!] Currency conversion failed: {e}")
            return value_usd  # fallback to USD

    def normalize_prices(self, raw_data: Dict[str, float], region: str) -> Dict[str, float]:
        if region not in self.material_multiplier:
            raise ValueError("Region not supported!")

        mat_factor = self.material_multiplier[region]
        labor_factor = self.labor_multiplier[region]
        target_currency = self.local_currency[region]

        normalized = {}
        for item, value in raw_data.items():
            if item == "timestamp" or value is None:
                continue
            if "tile" in item or "wood" in item or "cement" in item:
                adjusted = value * mat_factor
            else:
                adjusted = value * labor_factor

            normalized[item] = self.convert_currency(adjusted, target_currency)

        normalized["currency"] = target_currency
        normalized["region"] = region
        normalized["timestamp"] = raw_data.get("timestamp", "")
        return normalized


if __name__ == "__main__":
    # Test with mocked data from marketwatch_scraper
    mock_data = {
        "steel": 750.0,
        "cement": 120.0,
        "wood": 500.0,
        "alibaba_tile": 3.2,
        "timestamp": "2025-06-03T12:00:00Z"
    }

    normalizer = RegionalNormalizer()
    ngn_prices = normalizer.normalize_prices(mock_data, region="nigeria")
    usa_prices = normalizer.normalize_prices(mock_data, region="usa")

    print("🇳🇬 Nigeria Adjusted Costs:")
    print(json.dumps(ngn_prices, indent=2))

    print("\n🇺🇸 USA Adjusted Costs:")
    print(json.dumps(usa_prices, indent=2))

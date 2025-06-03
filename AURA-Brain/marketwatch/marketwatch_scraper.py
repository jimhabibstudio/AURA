# marketwatch/marketwatch_scraper.py
# Tesla+SpaceX-Level Intelligence: Live Market Cost Acquisition and Trend Forecasting

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Sample APIs – these should be swapped for actual verified providers
MATERIAL_API = "https://api.mockconstruction.com/materials"
LABOR_API = "https://api.mockconstruction.com/labor"
CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/USD"

# Supported materials and labor roles (can be expanded)
TRACKED_MATERIALS = ["cement", "steel", "sand", "brick", "glass", "wood", "rebar", "tile"]
LABOR_TYPES = ["mason", "carpenter", "electrician", "plumber", "painter"]

# Base regions for tracking
REGIONS = ["Lagos", "Nairobi", "London", "New York", "Bangalore", "Cairo", "Johannesburg"]

# Simulated key: replace with actual tokens from vendors
HEADERS = {"Authorization": "Bearer your_api_key_here"}


def fetch_material_prices(region: str) -> Dict[str, float]:
    """Fetch current material costs by region."""
    try:
        response = requests.get(f"{MATERIAL_API}?region={region}", headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("prices", {})
        else:
            return {mat: None for mat in TRACKED_MATERIALS}
    except Exception as e:
        print(f"Error fetching materials for {region}: {e}")
        return {mat: None for mat in TRACKED_MATERIALS}


def fetch_labor_costs(region: str) -> Dict[str, float]:
    """Fetch current labor wages by role and region."""
    try:
        response = requests.get(f"{LABOR_API}?region={region}", headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("wages", {})
        else:
            return {role: None for role in LABOR_TYPES}
    except Exception as e:
        print(f"Error fetching labor costs for {region}: {e}")
        return {role: None for role in LABOR_TYPES}


def fetch_currency_rates(base_currency: str = "USD") -> Dict[str, float]:
    """Fetch live currency conversion rates."""
    try:
        response = requests.get(f"{CURRENCY_API}")
        if response.status_code == 200:
            return response.json().get("rates", {})
        else:
            return {}
    except Exception as e:
        print(f"Error fetching currency rates: {e}")
        return {}


def normalize_to_usd(data: Dict[str, float], currency: str, rates: Dict[str, float]) -> Dict[str, float]:
    """Convert regional costs to USD equivalent."""
    if currency == "USD" or not rates.get(currency):
        return data
    conversion = rates[currency]
    return {k: round(v / conversion, 2) if v else None for k, v in data.items()}


def save_to_library(region: str, material_data: Dict, labor_data: Dict, timestamp: str):
    """Save fetched data into cost_library.json format."""
    snapshot = {
        "region": region,
        "timestamp": timestamp,
        "materials": material_data,
        "labor": labor_data
    }
    filename = f"../knowledge/cost_snapshots/{region}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"✅ Saved snapshot: {filename}")


def scrape_all_regions():
    """Run complete market sweep for all regions."""
    rates = fetch_currency_rates()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")

    for region in REGIONS:
        print(f"\n🌍 Gathering market intelligence for {region}...")
        material_prices = fetch_material_prices(region)
        labor_wages = fetch_labor_costs(region)

        # Assume region → currency mapping (could be refined)
        region_currency = {
            "Lagos": "NGN",
            "Nairobi": "KES",
            "London": "GBP",
            "New York": "USD",
            "Bangalore": "INR",
            "Cairo": "EGP",
            "Johannesburg": "ZAR"
        }

        currency = region_currency.get(region, "USD")
        norm_materials = normalize_to_usd(material_prices, currency, rates)
        norm_labor = normalize_to_usd(labor_wages, currency, rates)

        save_to_library(region, norm_materials, norm_labor, timestamp)

        time.sleep(1)  # avoid hammering APIs


if __name__ == "__main__":
    scrape_all_regions()

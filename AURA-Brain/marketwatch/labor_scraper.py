# labor_scraper.py
# Tesla+SpaceX Scale: Global Construction Labor Cost Scraper + Intelligence Engine

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}


class LaborCostScraper:
    def __init__(self):
        self.sources = {
            "USA": "https://www.salary.com/research/salary/benchmark/construction-worker-salary",
            "Nigeria": "https://nigeriansalary.com/construction-worker-salary/",
            "UK": "https://www.payscale.com/research/UK/Job=Construction_Worker/Hourly_Rate",
            "India": "https://www.glassdoor.co.in/Salaries/india-construction-worker-salary-SRCH_IL.0,5_IN115_KO6,27.htm"
        }

    def fetch_salary_us(self, url: str) -> Optional[float]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            val = soup.find("div", {"class": "median-salary"}).find("span")
            if val:
                salary = val.text.replace("$", "").replace(",", "")
                return round(float(salary) / 160, 2)  # Convert monthly to hourly
        except Exception as e:
            print(f"[!] US Salary scrape failed: {e}")
        return None

    def fetch_salary_ng(self, url: str) -> Optional[float]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            val = soup.find("div", class_="salary")
            if val:
                text = val.text.split("₦")[1].split("/")[0].replace(",", "")
                monthly = float(text)
                return round(monthly / 160, 2)  # assume 160 work hours per month
        except Exception as e:
            print(f"[!] Nigeria scrape failed: {e}")
        return None

    def fetch_salary_payscale(self, url: str) -> Optional[float]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            val = soup.find("div", class_="pay-range__value")
            if val:
                return float(val.text.replace("£", "").strip())
        except Exception as e:
            print(f"[!] UK scrape failed: {e}")
        return None

    def fetch_salary_glassdoor(self, url: str) -> Optional[float]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            val = soup.find("div", {"data-test": "MedianBasePay"})
            if val:
                text = val.text.replace("₹", "").replace(",", "").split("/")[0]
                monthly = float(text)
                return round(monthly / 160, 2)
        except Exception as e:
            print(f"[!] India scrape failed: {e}")
        return None

    def get_all_labor_rates(self) -> Dict[str, float]:
        data = {}
        for region, url in self.sources.items():
            if region == "USA":
                data[region] = self.fetch_salary_us(url)
            elif region == "Nigeria":
                data[region] = self.fetch_salary_ng(url)
            elif region == "UK":
                data[region] = self.fetch_salary_payscale(url)
            elif region == "India":
                data[region] = self.fetch_salary_glassdoor(url)
        data['timestamp'] = datetime.utcnow().isoformat()
        return data


if __name__ == "__main__":
    scraper = LaborCostScraper()
    rates = scraper.get_all_labor_rates()
    print("🧱 Real-Time Construction Labor Rates (Hourly):")
    print(json.dumps(rates, indent=2))

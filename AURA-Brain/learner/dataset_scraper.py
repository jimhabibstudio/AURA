# learner/dataset_scraper.py

import os, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path
import mimetypes

TARGET_FOLDER = "data/floorplans"

SOURCES = [
    "https://www.houseplans.com/floorplans",
    "https://www.archdaily.com/search/projects/categories/houses",
    "https://www.floorplans.com",
    "https://www.architecturaldesigns.com/house-plans",
    "https://www.dreamhomesource.com",
    "https://www.homeplans.com",
    "https://www.homestratosphere.com",
    "https://www.zillow.com/homes/floor_plan/",
    "https://www.trulia.com",
    "https://www.apartmentguide.com/floorplans/",
    "https://www.houzz.com/photos/query/floor-plan",
    "https://www.reddit.com/r/floorplan",
    "https://www.pinterest.com/search/pins/?q=floor%20plans"
]

def is_valid_file(url):
    return any(url.lower().endswith(ext) for ext in [".jpg", ".png", ".jpeg", ".pdf", ".svg"])

def create_filename(url, source, idx):
    ext = mimetypes.guess_extension(mimetypes.guess_type(url)[0] or ".jpg") or ".jpg"
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    return f"{source.replace('https://', '').replace('/', '_')}_{idx}_{timestamp}{ext}"

def scrape_site(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        img_links = [img.get("src") or img.get("data-src") for img in soup.find_all("img")]
        file_links = img_links + [a.get("href") for a in soup.find_all("a", href=True)]
        return [urljoin(url, link) for link in file_links if link and is_valid_file(link)]
    except Exception as e:
        print(f"[ERROR] Failed to scrape {url} → {e}")
        return []

def save_file(url, dest_folder, name):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        file_path = os.path.join(dest_folder, name)
        with open(file_path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"[ERROR] Download failed: {url} → {e}")
        return False

def download_sample_floorplans(limit_per_site=10):
    Path(TARGET_FOLDER).mkdir(parents=True, exist_ok=True)
    for site in SOURCES:
        print(f"\n🔍 Scraping from {site}")
        links = scrape_site(site)
        saved = 0
        for idx, link in enumerate(links):
            if saved >= limit_per_site:
                break
            filename = create_filename(link, site, idx)
            if save_file(link, TARGET_FOLDER, filename):
                print(f"✅ Saved: {filename}")
                saved += 1

if __name__ == "__main__":
    download_sample_floorplans()

# learner/floorplan_parser.py
# Phase 1: Parse Floorplan Images into AI-Usable Representations

import cv2
import os
import numpy as np
import pytesseract
from pathlib import Path
from typing import List, Dict

# Define room labels for classification
KNOWN_ROOMS = ["Living", "Bedroom", "Kitchen", "Bathroom", "Toilet", "Dining", "Garage", "Balcony", "Store", "Office"]

def preprocess_image(image_path: str) -> np.ndarray:
    """Load and clean up image for OCR."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

def extract_text_regions(thresh_img: np.ndarray) -> List[Dict]:
    """Use OCR to detect room names and bounding boxes."""
    results = []
    d = pytesseract.image_to_data(thresh_img, output_type=pytesseract.Output.DICT)
    for i in range(len(d['text'])):
        if int(d['conf'][i]) > 60:
            text = d['text'][i].strip().capitalize()
            for known_room in KNOWN_ROOMS:
                if known_room in text:
                    x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
                    results.append({
                        "room": known_room,
                        "bbox": (x, y, x + w, y + h)
                    })
                    break
    return results

def detect_walls(thresh_img: np.ndarray) -> List[Dict]:
    """Very simple wall detector using contours (for now)."""
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    walls = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 3, True)
        x, y, w, h = cv2.boundingRect(approx)
        if w > 20 and h > 20:  # Filter out noise
            walls.append({"bbox": (x, y, x + w, y + h)})
    return walls

def parse_floorplan(image_path: str) -> Dict:
    """Main function to extract structured floorplan data."""
    thresh = preprocess_image(image_path)
    rooms = extract_text_regions(thresh)
    walls = detect_walls(thresh)
    return {
        "image_path": image_path,
        "rooms": rooms,
        "walls": walls
    }

if __name__ == '__main__':
    sample = "data/floorplans/example_plan.jpg"
    if os.path.exists(sample):
        parsed = parse_floorplan(sample)
        print("Parsed Plan:")
        for room in parsed['rooms']:
            print(room)
        print(f"Total walls detected: {len(parsed['walls'])}")
    else:
        print("Sample image not found. Run dataset_scraper.py first.")

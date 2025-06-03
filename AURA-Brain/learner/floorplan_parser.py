# learner/floorplan_parser.py
# Tesla-level Floorplan Parser for AURA Phase 1

import cv2
import os
import numpy as np
import pytesseract
from pathlib import Path
from typing import List, Dict, Tuple

# Architecture-aware room labels
KNOWN_ROOMS = [
    "Living", "Bedroom", "Kitchen", "Bathroom", "Toilet", 
    "Dining", "Garage", "Balcony", "Store", "Office", "Pantry", "Closet"
]

def preprocess_image(image_path: str) -> np.ndarray:
    """Load and clean image for OCR and structure detection."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    return img, edges

def extract_rooms(img: np.ndarray) -> List[Dict]:
    """Use OCR to detect known room names and locations."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
    
    rooms = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip().capitalize()
        if text in KNOWN_ROOMS and int(data['conf'][i]) > 50:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            rooms.append({
                "room": text,
                "bbox": (x, y, x + w, y + h)
            })
    return rooms

def detect_walls(edges: np.ndarray) -> List[Dict]:
    """Detect walls using probabilistic Hough transform."""
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=40, maxLineGap=10)
    wall_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            wall_lines.append({"start": (x1, y1), "end": (x2, y2)})
    return wall_lines

def detect_doors_and_windows(edges: np.ndarray) -> List[Dict]:
    """Primitive symbolic detection for doors/windows."""
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    features = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        area = cv2.contourArea(c)
        if 10 < area < 500 and 0.1 < aspect_ratio < 4.0:
            features.append({
                "bbox": (x, y, x + w, y + h),
                "type": "door_or_window"  # Placeholder label
            })
    return features

def parse_floorplan(image_path: str) -> Dict:
    """Full floorplan parsing logic for AI training ingestion."""
    raw_img, edge_img = preprocess_image(image_path)
    rooms = extract_rooms(raw_img)
    walls = detect_walls(edge_img)
    doors = detect_doors_and_windows(edge_img)
    
    return {
        "image": image_path,
        "rooms": rooms,
        "walls": walls,
        "features": doors
    }

if __name__ == "__main__":
    sample = "data/floorplans/example_plan.jpg"
    if os.path.exists(sample):
        result = parse_floorplan(sample)
        print(f"\nParsed Output for: {sample}")
        print(f"Rooms ({len(result['rooms'])}): {[r['room'] for r in result['rooms']]}")
        print(f"Walls Detected: {len(result['walls'])}")
        print(f"Doors/Windows: {len(result['features'])}")
    else:
        print("❌ No sample image found. Run dataset_scraper.py to generate examples.")

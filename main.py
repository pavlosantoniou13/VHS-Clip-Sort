import cv2
import pytesseract
import os
import shutil
import re

# --- CONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
INPUT_FOLDER = 'test' 
OUTPUT_FOLDER = 'sorted_vhs'

import collections # Add this at the top of your script

import cv2
import pytesseract
import collections
import numpy as np # Make sure to import numpy for kernels

def get_year_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if fps == 0 or total_frames == 0:
        return "Unknown"
        
    duration_seconds = int(total_frames / fps)
    
    # --- ROUND 1: Standard Scan ---
    print(f"    [Round 1] Standard scan starting...")
    found_years = run_scan(cap, duration_seconds, mode="standard")

    # --- ROUND 2: Aggressive Fallback (Only runs if Round 1 failed) ---
    if not found_years:
        print(f"    [!] No years found. Starting Round 2: Aggressive Scan...")
        found_years = run_scan(cap, duration_seconds, mode="aggressive")
        if not found_years :
            print(f"    [!] No years found. Starting Round 3: Aggressive Scan...")
            found_years = run_scan(cap, duration_seconds, mode="aggressive2")


    cap.release()

    if found_years:
        most_common_year = collections.Counter(found_years).most_common(1)[0][0]
        return most_common_year
    
    return "Unknown"

def run_scan(cap, duration, mode):
    matches = []
    # Create a small 2x2 kernel for thickening text in aggressive mode
    kernel = np.ones((2,2), np.uint8)

    for s in [x * 0.5 for x in range(0, duration * 2)]:
        cap.set(cv2.CAP_PROP_POS_MSEC, s * 1000)
        success, frame = cap.read()
        if not success: break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if mode == "standard":
            # Just a basic high-contrast threshold
            blurred = cv2.GaussianBlur(gray, (3,3), 0)
            _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed = cv2.dilate(thresh, kernel, iterations=1)
        elif mode == "aggresive":
            # AGGRESSIVE: Blur to remove noise, then Thicken (Dilate) the letters
            h, w = gray.shape
            crop = gray[int(h*0.7):h, 0:int(w*0.5)] # Bottom-left quadrant

            # 2. ADAPTIVE THRESHOLD: Instead of one 'limit' (127), it calculates 
            # thresholds for small neighborhoods. Perfect for text on uneven floors.
            processed = cv2.adaptiveThreshold(crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            # 3. UPSCALING: VHS text is tiny. Doubling it makes it 'readable' for Tesseract.
            processed = cv2.resize(processed, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        else :

            enhanced = cv2.convertScaleAbs(gray, alpha=3.0, beta=-100)

            blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

            processed = cv2.adaptiveThreshold(
                blurred, 255, 
                cv2.ADAPTIVE_THRESH_MEAN_C, 
                cv2.THRESH_BINARY_INV, 
                15, 8
            )
            processed = cv2.resize(processed, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

            processed = cv2.dilate(processed, kernel, iterations=1)

        text = pytesseract.image_to_string(processed, config='--psm 11')
        match = re.search(r'(19|20)\d{2}', text)
    
        
        if match:
            print(match)
            if (int(match.group(0)) > 1991) :
                matches.append(match.group(0))

        if len(matches) > 5 :
            return matches            
    return matches


# --- MAIN LOOP ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.wmv')]
    
    if not files:
        print(f"No .wmv files found in {INPUT_FOLDER}")
    else:
        for file in files:
            print(f"\n--- Starting Full Scan: {file} ---")
            full_path = os.path.join(INPUT_FOLDER, file)
            
            year = get_year_from_video(full_path)
            
            year_dir = os.path.join(OUTPUT_FOLDER, year)
            os.makedirs(year_dir, exist_ok=True)
            
            shutil.copy(full_path, os.path.join(year_dir, file))
            print(f"--- Finished: Moved to {year} ---")

print("\nAll videos have been thoroughly scanned!")
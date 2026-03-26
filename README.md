# 📼 VHS Video Sorter (OCR Edition)

An automated Python tool designed to rescue and organize digitized VHS tapes. This script scans video files for on-screen timestamps (common in 90s home movies), extracts the year using **Tesseract OCR**, and automatically sorts the files into year-based folders.

To handle the low resolution, tracking noise, and color bleeding typical of VHS transfers, the script utilizes a **three-tier aggressive scanning strategy**.

---

## 🚀 Key Features

* **Multi-Stage OCR Scanning:** Uses three different image processing modes (Standard, Aggressive, and Ultra-Aggressive) to catch hard-to-read text.
* **Intelligent ROI (Region of Interest):** Automatically crops to the bottom-left quadrant where timestamps usually reside to reduce noise.
* **Preprocessing Pipeline:** Implements Adaptive Thresholding, Gaussian Blurring, and Image Dilatation to sharpen "muddy" VHS text.
* **Resolution Upscaling:** Doubling ($2\times$) and Tripling ($3\times$) frame resolution before OCR to help Tesseract recognize tiny characters.
* **Validation Logic:** Filters results based on a user-defined date range (e.g., 1990–2005) to ensure random numbers aren't mistaken for years.

---

## 🛠️ Prerequisites

### 1. Install Tesseract OCR
The script requires the Tesseract engine installed on your system.
* **Windows:** Download the installer from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). 
* **Note:** During installation, record your install path (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`).

### 2. Python Dependencies
Install the required libraries via pip:
```bash
pip install opencv-python pytesseract numpy
import fitz  # PyMuPDF for handling PDFs
import pytesseract
import cv2
import numpy as np
from PIL import Image
import json
import re
import io

# ✅ Step 1: Convert PDF Pages to Images Without Poppler
def pdf_to_images(pdf_path):
    """Extracts images from a PDF file using PyMuPDF (fitz)."""
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)  # Convert page to an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    return images

# ✅ Step 2: Preprocess Image (Denoising, Grayscale, Thresholding)
def preprocess_image(image):
    """Applies noise reduction, grayscale conversion, and thresholding to improve OCR."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)  # Convert to grayscale
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Apply Gaussian Blur to remove noise
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Apply adaptive thresholding
    return thresh

# ✅ Step 3: Perform OCR with Confidence & Positioning
def perform_ocr(image):
    """Extracts text with confidence scores and bounding box positions."""
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    extracted_text = []
    for i in range(len(ocr_data["text"])):
        word = ocr_data["text"][i].strip()
        confidence = int(ocr_data["conf"][i])
        x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
        
        if word and confidence > 50:  # Ignore empty or low-confidence words
            extracted_text.append({
                "word": word,
                "confidence": confidence,
                "bounding_box": {"x": x, "y": y, "width": w, "height": h}
            })
    
    return extracted_text

# ✅ Step 4: Structure Extracted Data into JSON
def structure_to_json(ocr_results):
    """Converts OCR extracted words into structured JSON format."""
    structured_data = {"words": ocr_results}
    
    # Define expected field patterns for key-value extraction
    field_patterns = {
        "First Name": r"First Name:\s*([A-Za-z]+)",
        "Last Name": r"Last Name:\s*([A-Za-z]+)",
        "SSN": r"SSN:\s*(\d{3}-\d{2}-\d{4})",
        "Date of Birth": r"Date of Birth:\s*(\d{2}/\d{2}/\d{4})"
    }
    
    extracted_fields = {}
    text_string = " ".join([word["word"] for word in ocr_results])  # Reconstruct text
    
    for field, pattern in field_patterns.items():
        match = re.search(pattern, text_string)
        if match:
            extracted_fields[field] = match.group(1)

    structured_data["extracted_fields"] = extracted_fields
    return structured_data

# ✅ Step 5: Run End-to-End OCR Processing Without Poppler
def process_pdf(pdf_path):
    """Processes a PDF by converting to images, cleaning, extracting text, and structuring as JSON."""
    images = pdf_to_images(pdf_path)
    all_results = []

    for i, image in enumerate(images):
        print(f"📄 Processing Page {i + 1}...")

        processed_image = preprocess_image(image)  # Apply noise reduction
        ocr_results = perform_ocr(processed_image)  # Perform OCR
        structured_json = structure_to_json(ocr_results)  # Convert to JSON

        all_results.append(structured_json)

    return all_results

# ✅ Run the pipeline on a PDF
pdf_path = r"C:\Users\senth\OneDrive\Desktop\paper_enroll\scanned_doc.pdf"
results = process_pdf(pdf_path)

# ✅ Save to JSON file
with open("ocr_output.json", "w") as json_file:
    json.dump(results, json_file, indent=4)

print("✅ OCR Process Complete! JSON output saved.")

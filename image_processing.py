# image_processing.py
import cv2
import os
import numpy as np
from PIL import Image

def preprocess_image(image):
    """Applies noise reduction, grayscale conversion, and thresholding to improve OCR."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def save_cleaned_image(image, output_dir, page_num):
    """Saves preprocessed (noise-removed) images for verification."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"cleaned_page_{page_num}.png")
    cv2.imwrite(output_path, image)
    print(f"✅ Cleaned image saved: {output_path}")

def highlight_extracted_text(image, extracted_text):
    """Overlays bounding boxes of extracted text on the image."""
    img = np.array(image)
    for word_info in extracted_text:
        x, y, w, h = word_info["bounding_box"].values()
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, word_info["word"], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return Image.fromarray(img)

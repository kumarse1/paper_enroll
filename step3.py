import json
import re
import os
import fitz  # PyMuPDF for extracting text from PDF
import pytesseract
import cv2
import numpy as np
from PIL import Image
import nltk
from nltk.tokenize import word_tokenize

nltk.download("punkt")  # Download tokenizer

# ✅ Step 1: Define Known Forms for Detection
KNOWN_FORMS = {
    "Health Information Form": ["health information", "fairfax county public schools", "student health form"],
    "Enrollment Form": ["student enrollment", "admission", "registration"],
    "Medical History Form": ["medical history", "health conditions", "medications"]
}

# ✅ Step 2: Static Verbiage to Remove
LONG_STATIC_VERBIAGE = [
    "Complete this form every school year to inform us about your student's",
    "Parental Consent: I agree to allow my child's healthcare provider(s) to discuss information",
    "Number of Emergency Room (ER) Visits in the last calendar year:",
    "existing and new health conditions that affect your student's school day"
]

# ✅ Step 3: Convert PDF to Images
def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

# ✅ Step 4: Detect Form Type
def detect_form_type(ocr_text):
    for form_name, keywords in KNOWN_FORMS.items():
        for keyword in keywords:
            if keyword.lower() in ocr_text.lower():
                return form_name
    return "Unknown Form"

# ✅ Step 5: Preprocess Image (Noise Reduction, Grayscale, Thresholding)
def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

# ✅ Step 6: Perform OCR with Confidence, Merging & Filtering
def perform_ocr(image):
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    extracted_text = []
    word_buffer = []
    prev_x = None

    for i in range(len(ocr_data["text"])):
        word = ocr_data["text"][i].strip()
        confidence = int(ocr_data["conf"][i])
        x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]

        if word and confidence > 50 and word not in LONG_STATIC_VERBIAGE:
            if prev_x is not None and (x - prev_x) < 15:
                word_buffer.append(word)
            else:
                if word_buffer:
                    extracted_text.append({"word": " ".join(word_buffer), "confidence": confidence,
                                           "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h}})
                word_buffer = [word]
            prev_x = x + w

    if word_buffer:
        extracted_text.append({"word": " ".join(word_buffer), "confidence": confidence,
                               "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h}})
    return extracted_text

# ✅ Step 7: Tokenize Extracted Text (Optional)
def tokenize_extracted_text(extracted_text):
    tokens = word_tokenize(" ".join([word["word"] for word in extracted_text]))
    return tokens

# ✅ Step 8: Structure Data into JSON
def structure_to_json(ocr_results):
    structured_data = {"real_values": ocr_results}
    return structured_data

# ✅ Step 9: Save Cleaned Image
def save_cleaned_image(image, output_dir, page_num):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"cleaned_page_{page_num}.png")
    cv2.imwrite(output_path, image)
    print(f"✅ Cleaned image saved: {output_path}")

# ✅ Step 10: Highlight Extracted Text on Image
def highlight_extracted_text(image, extracted_text):
    img = np.array(image)
    for word_info in extracted_text:
        x, y, w, h = word_info["bounding_box"].values()
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, word_info["word"], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return Image.fromarray(img)

# ✅ Step 11: Process PDF & Save Results
def process_pdf(pdf_path, output_json_path, cleaned_image_path):
    images = pdf_to_images(pdf_path)
    all_results = []

    for i, image in enumerate(images):
        print(f"📄 Processing Page {i + 1}...")

        processed_image = preprocess_image(image)
        save_cleaned_image(processed_image, cleaned_image_path, i + 1)

        ocr_results = perform_ocr(processed_image)
        form_type = detect_form_type("\n".join([word["word"] for word in ocr_results]))
        structured_json = structure_to_json(ocr_results)

        structured_json["form_type"] = form_type  # Add detected form type
        all_results.append(structured_json)

        highlighted_image = highlight_extracted_text(image, ocr_results)
        highlighted_image.show()  # Display extracted text overlay

    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(all_results, json_file, indent=4)

    print(f"✅ OCR Process Complete! JSON saved at: {output_json_path}")

# ✅ Run the pipeline
pdf_path = r"C:\Users\senth\OneDrive\Desktop\paper_enroll\scanned_doc.pdf"
output_json_path = r"C:\Users\senth\OneDrive\Desktop\paper_enroll\filtered_ocr_output.json"
cleaned_image_path = r"C:\Users\senth\OneDrive\Desktop\paper_enroll\cleaned_images"

process_pdf(pdf_path, output_json_path, cleaned_image_path)

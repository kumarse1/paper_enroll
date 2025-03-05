# main.py
import json
import os
from pdf_processing import pdf_to_images
from image_processing import preprocess_image, save_cleaned_image,highlight_extracted_text 
from ocr_processing import perform_ocr
from text_analysis import detect_form_type, structure_to_json

# Paths
pdf_path = r"C:\Users\senth\OneDrive\Desktop\paper_enroll\scanned_doc.pdf"
output_json_path = r"C:\Users\senth\OneDrive\Desktop\paper_enroll\filtered_ocr_output.json"
cleaned_image_path = r"C:\Users\senth\OneDrive\Desktop\paper_enroll\cleaned_images"

# Process PDF
images = pdf_to_images(pdf_path)
all_results = []

for i, image in enumerate(images):
    processed_image = preprocess_image(image)
    save_cleaned_image(processed_image, cleaned_image_path, i + 1)

    ocr_results = perform_ocr(processed_image)
    form_type = detect_form_type("\n".join([word["word"] for word in ocr_results]))
    structured_json = structure_to_json(ocr_results, form_type)

    all_results.append(structured_json)

with open(output_json_path, "w", encoding="utf-8") as json_file:
    json.dump(all_results, json_file, indent=4)

print(f"✅ OCR Process Complete! JSON saved at: {output_json_path}")

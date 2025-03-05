import pytesseract
import pandas as pd
from tabulate import tabulate
import re
import os
import io
import numpy as np
from PIL import Image

# Import the configurations
from config import LONG_STATIC_VERBIAGE, KNOWN_FORMS

def map_to_baseline_schema(word):
    """
    Map extracted text to a baseline schema based on expected field patterns.
    """
    # Define expected fields and their patterns
    expected_fields = {
        "First Name": {"type": "string", "pattern": r"^[A-Za-z]+$", "required": True},
        "Last Name": {"type": "string", "pattern": r"^[A-Za-z]+$", "required": True},
        "SSN": {"type": "string", "pattern": r"^\d{3}-\d{2}-\d{4}$", "required": True},
        "Date of Birth": {"type": "date", "pattern": r"^\d{2}/\d{2}/\d{4}$", "required": True}
    }
    
    # Additional pattern hints to help with field identification
    field_hints = {
        "First Name": [r"(?i)first\s*name", r"(?i)given\s*name"],
        "Last Name": [r"(?i)last\s*name", r"(?i)family\s*name", r"(?i)surname"],
        "SSN": [r"(?i)ssn", r"(?i)social\s*security", r"(?i)social\s*security\s*number"],
        "Date of Birth": [r"(?i)dob", r"(?i)birth\s*date", r"(?i)date\s*of\s*birth"]
    }
    
    # Check if the word contains any field hints
    for field_name, hint_patterns in field_hints.items():
        for pattern in hint_patterns:
            if re.search(pattern, word):
                return field_name
    
    # Check if the word or part of it matches expected patterns
    # First, check if it has a key:value format
    parts = word.split(":", 1)
    if len(parts) > 1:
        key, value = parts[0].strip(), parts[1].strip()
        
        # Check the key against field hints
        for field_name, hint_patterns in field_hints.items():
            for pattern in hint_patterns:
                if re.search(pattern, key):
                    # Validate the value against the field's pattern
                    if re.match(expected_fields[field_name]["pattern"], value):
                        return field_name
    
    # If no key:value format, check if the entire word matches any pattern
    for field_name, field_info in expected_fields.items():
        if re.match(field_info["pattern"], word):
            # If it's a valid SSN format, it's likely an SSN
            if field_name == "SSN" and re.match(r"^\d{3}-\d{2}-\d{4}$", word):
                return "SSN"
            # If it's a valid date format, it's likely a DOB
            if field_name == "Date of Birth" and re.match(r"^\d{2}/\d{2}/\d{4}$", word):
                return "Date of Birth"
            # For names, we need more context to determine first vs last
    
    # If we couldn't determine a specific field
    return "Unknown"

def identify_form_type(text):
    """
    Identify the type of form based on keywords in the text.
    """
    text_lower = text.lower()
    for form_type, keywords in KNOWN_FORMS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return form_type
    return "Unknown Form"

def perform_ocr(image):
    """Extracts text with confidence, merges words, and filters static verbiage."""
    # Get full text for form identification
    full_text = pytesseract.image_to_string(image)
    form_type = identify_form_type(full_text)
    print(f"Identified form type: {form_type}")
    
    # Get detailed OCR data
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    extracted_text = []
    word_buffer = []
    prev_x = None
    
    for i in range(len(ocr_data["text"])):
        word = ocr_data["text"][i].strip()
        confidence = int(ocr_data["conf"][i])
        x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
        
        # Skip the word if it's in the static verbiage list or low confidence
        if not word or confidence <= 50:
            continue
            
        # Check if the word is part of static verbiage to skip
        skip_word = False
        for static_text in LONG_STATIC_VERBIAGE:
            if static_text.lower() in word.lower() or word.lower() in static_text.lower():
                skip_word = True
                break
                
        if skip_word:
            continue
            
        # Process valid words
        if prev_x is not None and (x - prev_x) < 15:
            word_buffer.append(word)
        else:
            if word_buffer:
                complete_word = " ".join(word_buffer)
                mapped_schema = map_to_baseline_schema(complete_word)
                extracted_text.append({
                    "key": complete_word.split(':')[0].strip() if ':' in complete_word else complete_word,
                    "value": complete_word.split(':')[1].strip() if ':' in complete_word else "",
                    "confidence": confidence,
                    "mapped_schema": mapped_schema,
                    "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h},
                    "form_type": form_type
                })
            word_buffer = [word]
        prev_x = x + w
        
    # Process any remaining words in the buffer
    if word_buffer:
        complete_word = " ".join(word_buffer)
        mapped_schema = map_to_baseline_schema(complete_word)
        extracted_text.append({
            "key": complete_word.split(':')[0].strip() if ':' in complete_word else complete_word,
            "value": complete_word.split(':')[1].strip() if ':' in complete_word else "",
            "confidence": confidence,
            "mapped_schema": mapped_schema,
            "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h},
            "form_type": form_type
        })
        
    return extracted_text

def print_ocr_results_table(extracted_text):
    """Print OCR results in a nicely formatted table"""
    # Create a pandas DataFrame from the extracted text
    df = pd.DataFrame([{
        'Key': item['key'],
        'Value': item['value'],
        'Confidence': f"{item['confidence']}%",
        'Mapped Schema': item['mapped_schema'],
        'Form Type': item['form_type']
    } for item in extracted_text])
    
    # Print using tabulate for a nice table format
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    
    # Return the dataframe in case you want to use it for other purposes
    return df

# Example usage
if __name__ == "__main__":
    import os
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("PyMuPDF is not installed. Please install it with: pip install pymupdf")
        exit(1)
    
    # Replace with your PDF path
    pdf_path = "your_document.pdf"
    
    # Check if the file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        exit(1)
        
    # Convert PDF to images using PyMuPDF
    print(f"Converting PDF to images: {pdf_path}")
    try:
        pdf_document = fitz.open(pdf_path)
        pages = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            # Increase the resolution for better OCR results
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            pages.append(img)
            
        print(f"Successfully converted {len(pages)} pages")
    except Exception as e:
        print(f"Error converting PDF: {e}")
        exit(1)
    
    # Process each page
    all_results = []
    for i, image in enumerate(pages):
        print(f"Processing page {i+1}/{len(pages)}")
        results = perform_ocr(image)
        all_results.extend(results)
        
        # Print results for this page
        print(f"\nResults from page {i+1}:")
        print_ocr_results_table(results)
    
    # Print all results together if multiple pages
    if len(pages) > 1:
        print("\nCombined results from all pages:")
        print_ocr_results_table(all_results)
